from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from helpers.verifications import validate_content, title_in_blacklist

def validate_date_coinpedia(date_text):
    try:
        date = datetime.strptime(date_text, '%b %d, %Y %H:%M')
        current_time = datetime.now()
        time_difference = current_time - date
        if time_difference <= timedelta(hours=24):
            return date
    except ValueError:
        pass
    return None

def extract_image_url_coinpedia(html):
    image = html.find('img', class_='attachment-jannah-image-post size-jannah-image-post wp-post-image entered lazyloaded')
    if image:
        src = image.get('data-lazy-src')
        if src:
            return src
    return None

def extract_article_content_coinpedia(html):
    content = ""
    content_div = html.find('div', class_='entry-content entry clearfix')
    if content_div:
        p_tags = content_div.find_all('p')
        for tag in p_tags:
            content += tag.text.strip()
    return content.casefold()

def validate_coinpedia_article(article_link, main_keyword):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }

    try:
        article_response = requests.get(article_link, headers=headers)
        article_content_type = article_response.headers.get("Content-Type", "").lower()

        if article_response.status_code == 200 and 'text/html' in article_content_type:
            html = BeautifulSoup(article_response.text, 'html.parser')

            # Extract date
            date_element = html.find('span', class_='post_date_display')
            valid_date = validate_date_coinpedia(date_element.text.strip() if date_element else None)

            # Extract image URL
            image_url = extract_image_url_coinpedia(html)

            # Extract article content
            content = extract_article_content_coinpedia(html)

            # Validate title, content, and date
            title_element = html.find('h1')
            title = title_element.text.strip() if title_element else None
            is_title_in_blacklist = title_in_blacklist(title)
            content_validation = validate_content(main_keyword, content)

            if valid_date and content and title and not is_title_in_blacklist and content_validation:
                return content, valid_date, image_url
    except Exception as e:
        print("Error in Coinpedia:", str(e))

    return None, None, None
