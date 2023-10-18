import re
from db import db_url
from pathlib import Path
from sqlalchemy import exists
from flask import Flask, request
from playwright.sync_api import sync_playwright
from sites.coindesk import validate_coindesk_article
from sites.coingape import validate_coingape_article
from apscheduler.jobstores.base import JobLookupError
from db import session, SCRAPPING_DATA, KEWORDS, ARTICLE
from sites.bitcoinist import validate_bitcoinist_article
from sites.beincrypto import validate_beincrypto_article
from sites.cointelegraph import validate_cointelegraph_article
from apscheduler.schedulers.background import BackgroundScheduler
from helpers.verifications import url_in_db, title_in_db, title_in_blacklist
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url= db_url)

token=os.getenv("SLACK_BOT_TOKEN")
signing_secret=os.getenv("SLACK_SIGNING_SECRET")

client = WebClient(
    token=token,
)

if scheduler.state != 1:
    scheduler.start()

THIS_FOLDER = Path(__file__).parent.resolve() # takes the parent path

app = Flask(__name__)

def send_message_to_slack(channel_id, title, date_time, url, summary, images_list):
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Title: {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:*\n{date_time}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*URL:*\n{url}"
                    }
                ]
            },
            {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"*Summary*\n{summary}"
			},
			"accessory": {
				"type": "image",
				"image_url": f"{images_list[0] if images_list else 'No Image'}",
				"alt_text": "alt text for image"
			}
            },
            {
                "type": "divider"
            }
        ]
    
        try:
            result = client.chat_postMessage(
                channel=channel_id,
                text='New Notification from News Bot', 
                blocks=blocks
            )
            response = result['ok']
            if response == True:
                return f'Message sent successfully to Slack channel {channel_id}', 200

        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return f'Error sending message to Slack channel {channel_id}', 500


def scrape_sites(site,base_url, website_name, is_URL_complete, main_keyword):

    article_urls = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            page.goto(site)
            page.wait_for_load_state('networkidle')

            a_elements = page.query_selector_all('a')

            for link in a_elements:
                href = link.get_attribute('href')
                article_title = link.text_content().strip().casefold()

                if href and article_title:
                    if is_URL_complete == False:
                        article_url = base_url + href.strip()
                    else:
                        article_url = href.strip()

                    
                    if main_keyword == 'bitcoin':
                        input_title_formatted = str(article_title).strip().casefold()
                        title_validation = bool(re.search(main_keyword, input_title_formatted, re.IGNORECASE))
                    else:
                        title_validation = True
    
                    is_url_in_db = url_in_db(article_url)
                    is_title_in_db = title_in_db(article_title)
                    is_title_in_blacklist = title_in_blacklist(article_title)
            
                    if title_validation == True:
                        if is_title_in_blacklist == False:
                            if is_url_in_db == False and is_title_in_db == False:
                                article_urls.add(article_url)


            browser.close()
            return article_urls, website_name
    except Exception as e:
        return f'Failed to scrape: {e}'
        
           


def scrape_articles(sites, main_keyword):

    try:
        site = sites.site
        base_url = sites.base_url
        website_name = sites.website_name
        is_URL_complete = sites.is_URL_complete

        # print(f'Web scrape of {main_keyword} STARTED')

        article_urls, website_name = scrape_sites(site,base_url,
                                                   website_name,
                                                   is_URL_complete,
                                                   main_keyword)
        
        if not article_urls:
            print(f'No articles found for {website_name}')
            return f'No articles found for {website_name}'

        if article_urls:
            for article_link in article_urls:

                article_to_save = []

                if website_name == 'Beincrypto':
                    title, content, valid_date, image_urls = validate_beincrypto_article(article_link, main_keyword)
                    if title and content and valid_date:
                        article_to_save.append((title, content, valid_date, article_link, website_name))

                if website_name == 'Bitcoinist':
                    title, content, valid_date, image_urls = validate_bitcoinist_article(article_link, main_keyword)
                    if title and content and valid_date:
                        article_to_save.append((title, content, valid_date, article_link, website_name))

                if website_name == 'Cointelegraph':
                    title, content, valid_date, image_urls = validate_cointelegraph_article(article_link, main_keyword)
                    if title and content and valid_date:
                        article_to_save.append((title, content, valid_date, article_link, website_name))

                if website_name == 'Coingape':
                    title, content, valid_date, image_urls = validate_coingape_article(article_link, main_keyword)
                    if title and content and valid_date:
                        article_to_save.append((title, content, valid_date, article_link, website_name))

                if website_name == 'Coindesk':
                    title, content, valid_date, image_urls = validate_coindesk_article(article_link, main_keyword)
                    if title and content and valid_date:
                        article_to_save.append((title, content, valid_date, article_link, website_name))

                
                for article_data in article_to_save:
                    title, content, valid_date, article_link, website_name = article_data

                    new_article = ARTICLE(title=title,
                                        content=content,
                                        date=valid_date,
                                        url=article_link,
                                        website_name=website_name
                                        )

                    session.add(new_article)
                    session.commit()
                    
                    btc_slack_channel_id = 'C05RK7CCDEK'
                    eth_slack_channel_id = 'C05URLDF3JP'
                    lsd_slack_channel_id = 'C05UNS3M8R3'
                    hacks_slack_channel_id = 'C05UU8JBKKN'
                    
                    if main_keyword == 'bitcoin':
                        channel_id = btc_slack_channel_id
                    elif main_keyword == 'ethereum':
                        channel_id = eth_slack_channel_id
                    elif main_keyword == 'hacks':
                        channel_id = hacks_slack_channel_id
                    else:
                        channel_id = lsd_slack_channel_id
                    
                    send_message_to_slack(channel_id=channel_id)
                    print(f'\nArticle: "{title}" has been added to the DB, Link: {article_link} from {website_name} in {main_keyword.capitalize()}.')

            
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
            job = scheduler.add_job(start_periodic_scraping, 'interval', minutes=5, id=target, replace_existing=True, args=[main_keyword], max_instances=2)
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
        

@app.route("/api/slack/post/message", methods=["POST"])
def slack_post_message():
    response, status = send_message_to_slack('C05RM0DF8J3','Test Title', 'Test Date', 'Test Url', 'Test Summary', 'Test Image Link')
    return response, status
        

def job_executed(event): # for the status 200 of the bot
    print(f'{event.job_id} was executed successfully at {event.scheduled_run_time}, response: {event.retval}')

def job_error(event): # for the status with an error of the bot
    print(f'{event.job_id} has an internal error')

def job_max_instances_reached(event): # for the status with an error of the bot
    job_id = event.job_id
    print(f'{job_id} news bot warning. Maximum number of running instances reached, consider upgrading the time interval ')
   

if __name__ == "__main__":       
    # try:
        scheduler.add_listener(job_error, EVENT_JOB_ERROR)
        scheduler.add_listener(job_max_instances_reached, EVENT_JOB_MAX_INSTANCES)
        scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
        print('AI Alpha server was activated')
        app.run(port=4000, threaded=True, use_reloader=True)
    # except (KeyboardInterrupt, SystemExit):
    #     pass 

    # print('AI Alpha server was deactivated')






