import time
import re
import requests
from db import db_url
from pathlib import Path
from bs4 import BeautifulSoup
from flask import Flask, request
from db import session, SCRAPPING_DATA, KEWORDS
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from helpers.verifications import url_in_db, title_in_db
from sites.beincrypto import validate_beincrypto_article
from sites.cointelegraph import validate_cointelegraph_article
from sites.coingape import validate_coingape_article
from sqlalchemy import exists
from playwright.sync_api import sync_playwright
from sites.bitcoinist import validate_bitcoinist_article
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

        print(f'Web scrapping of {website_name} STARTED')
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
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

                if main_keyword == 'hacks' or main_keyword == 'lsd':
                    title_validation = True
                else:
                    input_title_formatted = str(article_title).strip().casefold()
                    title_validation = re.search(main_keyword, input_title_formatted, re.IGNORECASE)
                
                is_url_in_db = url_in_db(article_url)
                is_title_in_db = title_in_db(article_title)

                if title_validation and not is_url_in_db and not is_title_in_db:
                    article_urls.append({'url': article_url, 'title': article_title})
        
        if not article_urls:
            print(f'No articles found for {website_name}')
            return f'No articles found for {website_name}'

        print('article_urls > ', article_urls)

        if article_urls:
            for article_schema in article_urls:
                article_link = article_schema['url']

                if website_name == 'Beincrypto':
                    title, content, valid_date, image_urls = validate_beincrypto_article(article_link, main_keyword)
                    if title and content and valid_date:
                        print(f'{website_name} article ok to saved to db')

                if website_name == 'Bitcoinist':
                    title, content, valid_date, image_urls = validate_bitcoinist_article(article_link, main_keyword)
                    if title and content and valid_date:
                        print(f'{website_name} article ok to saved to db')

                if website_name == 'Cointelegraph':
                    title, content, valid_date, image_urls = validate_cointelegraph_article(article_link, main_keyword)
                    if title and content and valid_date:
                        print(f'{website_name} article ok to saved to db')

                if website_name == 'Coingape':
                    title, content, valid_date, image_urls = validate_coingape_article(article_link, main_keyword)
                    if title and content and valid_date:
                        print(f'{website_name} article ok to saved to db')


            print(f'Web scrapping of {website_name} finished')
            return f'Web scrapping of {website_name} finished'
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
        return f'{target.capitalize()} News Bot is already active', 400
    else:
        scrapping_data_objects = session.query(SCRAPPING_DATA).filter(SCRAPPING_DATA.main_keyword == target.casefold()).all()

        if not scrapping_data_objects:
            return f'{target.capitalize()} does not match any in the database', 404
        
        if scrapping_data_objects:
            main_keyword = scrapping_data_objects[0].main_keyword
            job = scheduler.add_job(start_periodic_scraping, 'interval', minutes=2, id=target, replace_existing=True, args=[main_keyword])
            if job:
                return f'{target.capitalize()} News Bot activated', 200
            else: 
                return f'Error while activating the {target.capitalize()} News Bot'

    
def deactivate_news_bot(target):

    if scheduler.state == 0 or scheduler.state == 2:
        return 'Scheduler not active', 500 

    try:
        news_bot_job = scheduler.get_job(target)

        if not news_bot_job:
            return f'{target.capitalize()} News Bot is already inactive', 400
                
        scheduler.remove_job(news_bot_job.id)
        return f'{target.capitalize()} News Bot deactivated', 200
    
    except JobLookupError:
        return f"{target.capitalize()} News Bot was not found", 500


@app.route('/api/bot/status', methods=['GET', 'POST'])
def bot_status():
    value = scheduler.state
    if value == 1:
        state = 'Scheduler is active'
    else:
        state = 'Scheduler is not active'

    return state, 200 

@app.route('/api/bot/add/keyword', methods=['GET', 'POST'])
def add_keyword():
    data = request.json
    new_keyword = data['keyword']
    main_keyword = data['main_keyword']

    if not new_keyword or not main_keyword:
        return 'Keyword or main keyword are not present in the request', 404

    if main_keyword and new_keyword:
        scrapping_data_objects = session.query(
            SCRAPPING_DATA).filter(
                SCRAPPING_DATA.main_keyword == main_keyword).all()
        
        if not scrapping_data_objects:
            return 'Main keyword was not found in the database'
        
        if scrapping_data_objects:
            keyword_info_id = scrapping_data_objects[0].id
        
            keyword_exists = session.query(exists().where(
                (KEWORDS.keyword == new_keyword.casefold()) &
                (KEWORDS.keyword_info_id == keyword_info_id)
            )).scalar()
            if keyword_exists:
                return f"The keyword '{new_keyword}' already exists in the database for keyword_info_id {keyword_info_id}.", 404
            else:
                new_keyword_object = KEWORDS(keyword=new_keyword.casefold(), keyword_info_id=keyword_info_id)
                session.add(new_keyword_object)
                session.commit()
                return f"The keyword '{new_keyword}' has been inserted into the database for keyword_info_id {keyword_info_id}.", 200
        
        
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
    job_id = event.job_id
    print(f'{job_id} news bot. Maximum number of running instances reached')
    scheduler.remove_job(job_id)
    scheduler.shutdown()
   

if __name__ == "__main__":
    # try:
        scheduler.add_listener(job_error, EVENT_JOB_ERROR)
        scheduler.add_listener(job_max_instances_reached, EVENT_JOB_MAX_INSTANCES)
        scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
        app.run(port=4000, debug=False, threaded=True, use_reloader=False)
        print('AI Alpha server was activated')
    # except (KeyboardInterrupt, SystemExit):
    #     print('AI Alpha server was deactivated')
    #     scheduler.shutdown()






