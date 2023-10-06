import time
import json
from db import db_url
from db import session, SCRAPPING_DATA
from pathlib import Path
from flask import Flask, request
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url= db_url)


if scheduler.state != 1:
    scheduler.start()

THIS_FOLDER = Path(__file__).parent.resolve() # takes the parent path

app = Flask(__name__)

def start_periodic_scraping():

    scrapping_data_objects = session.query(SCRAPPING_DATA).all()

    for scrapping_data in scrapping_data_objects:
        print('main word >', scrapping_data.main_keyword)
    for keyword in scrapping_data.keywords:
        print('keyword > ', keyword.keyword)
    for site in scrapping_data.sites:
        print('sites > ', site)

    return 'ok'


def activate_news_bot():

    if scheduler.state == 0 or scheduler.state == 2:
        return 'Scheduler not active', 500 
   
    news_bot_job = scheduler.get_job('News_Bot')
    if news_bot_job:
        return 'News Bot is already active', 400
    else:
        job = scheduler.add_job(start_periodic_scraping, 'interval', seconds=3, id='News_Bot', replace_existing=True)
        if job:
            return 'News Bot activated', 200
        else: 
            return 'Error while activating the News Bot'

    
def deactivate_news_bot():

    if scheduler.state == 0 or scheduler.state == 2:
        return 'Scheduler not active', 500 

    try:
        news_bot_job = scheduler.get_job('News_Bot')
        if not news_bot_job:
            return 'News bot is not active', 404
                
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

        if command == 'activate': 
            res, status = activate_news_bot()
            return res, status
        elif command == 'deactivate':
            response, status = deactivate_news_bot()
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






