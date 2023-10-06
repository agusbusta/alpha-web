import time
import re
import requests
from db import db_url
from pathlib import Path
from bs4 import BeautifulSoup
from flask import Flask, request
from db import session, SCRAPPING_DATA
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from helpers.verifications import url_in_db, title_in_db
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url= db_url)


if scheduler.state != 1:
    scheduler.start()

THIS_FOLDER = Path(__file__).parent.resolve() # takes the parent path

app = Flask(__name__)


def scrape_articles(sites, main_keyword):

    try:
        site = sites.site
        base_url = sites.base_url
        website_name = sites.website_name
        is_URL_complete = sites.is_URL_complete
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
        }

        response = requests.get(site, headers=headers)
        content_type = response.headers.get("Content-Type", "").lower()

        article_urls = []

        if response.status_code == 200 and 'text/html' in content_type:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

        
        for link in links:
            href = link.get('href')
            article_title = link.text.strip()

            if href and article_title:

                if is_URL_complete == False:
                    article_url = base_url + href.strip()
                else:
                    article_url = href.strip()

                if main_keyword == 'hacks':
                    title_validation = True
                else:
                    input_title_formatted = str(article_title).strip().casefold()
                    title_validation = re.search(main_keyword, input_title_formatted, re.IGNORECASE)
                
                is_url_in_db = url_in_db(article_url)
                is_title_in_db = title_in_db(article_title)

                if title_validation and not is_url_in_db and not is_title_in_db:
                    article_urls.append({'url': article_url, 'title': article_title})
        print('article_urls >', article_urls)
        # if article_urls:
        #     for article_schema in article_urls:
        #         article_link = article_schema['url']

    except:
        return 'Error in scrape_articles'

def start_periodic_scraping(main_keyword):

    scrapping_data_objects = session.query(SCRAPPING_DATA).filter(SCRAPPING_DATA.main_keyword == main_keyword).all()

    if not scrapping_data_objects:
        return f'Bot with keyword {main_keyword} was not found'
    else:
        sites = scrapping_data_objects[0].sites
        for site in sites:
            scrape_articles(site, main_keyword)

    return f'All {str(main_keyword).casefold().capitalize()} sites scraped', 200



def activate_news_bot(target):

    if scheduler.state == 0 or scheduler.state == 2:
        return 'Scheduler not active', 500 
   
    news_bot_job = scheduler.get_job(target)
    if news_bot_job:
        return f'{target} News Bot is already active', 400
    else:
        scrapping_data_objects = session.query(SCRAPPING_DATA).filter(SCRAPPING_DATA.main_keyword == target).all()

        if not scrapping_data_objects:
            return 'Main Keyword does not match any in the database', 404
        
        if scrapping_data_objects:
            main_keyword = scrapping_data_objects[0].main_keyword
            job = scheduler.add_job(start_periodic_scraping, 'interval', minutes=2, id=target, replace_existing=True, args=[main_keyword])
            if job:
                return 'News Bot activated', 200
            else: 
                return 'Error while activating the News Bot'

    
def deactivate_news_bot(target):

    if scheduler.state == 0 or scheduler.state == 2:
        return 'Scheduler not active', 500 

    try:
        news_bot_job = scheduler.get_job(target)

        if not news_bot_job:
            return f'{target} News Bot is already inactive', 400
                
        scheduler.remove_job(news_bot_job.id)
        return 'News Bot deactivated', 200
    
    except JobLookupError:
        return "News Bot was not found", 500


@app.route('/api/bot/status', methods=['GET', 'POST'])
def bot_status():
    value = scheduler.state
    if value == 1:
        state = 'Scheduler is active'
    else:
        state = 'Scheduler is not active'

    return state, 200 
        
@app.route('/api/news/bot', methods=['GET', 'POST'])
def news_bot_commands():
    if request:
        data = request.json
        command = data['command']
        target = data['target']

        if command == 'activate': 
            res, status = activate_news_bot(target)
            return res, status
        elif command == 'deactivate':
            response, status = deactivate_news_bot(target)
            return response, status
        else:
            return 'Command not valid', 400
        

def job_executed(event): # for the status 200 of the bot
    print(f'{event.job_id} was executed successfully at {event.scheduled_run_time}, response: {event.retval}')

def job_error(event): # for the status with an error of the bot
    print(f'{event.job_id} has an internal error')

def job_max_instances_reached(event): # for the status with an error of the bot
    print(f'{event.job_id} maximum number of running instances reached')
    scheduler.shutdown()
  

if __name__ == "__main__":
    # try:
        scheduler.add_listener(job_error, EVENT_JOB_ERROR)
        scheduler.add_listener(job_max_instances_reached, EVENT_JOB_MAX_INSTANCES)
        scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
        app.run(port=4000, debug=True, threaded=True, use_reloader=True)
        print('AI Alpha server was activated')
    # except (KeyboardInterrupt, SystemExit):
    #     print('AI Alpha server was deactivated')
    #     scheduler.shutdown()






