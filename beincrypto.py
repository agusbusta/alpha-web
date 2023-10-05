from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

# Conditions
# Date can't be more than 24 hours old
# Content must have at least one keyword
# Must have an h1 - title

from datetime import datetime, timedelta
import re

def validate_date_beincrypto(date):
    print('date > ', date)
    current_date = datetime.now()
    valid_date = None

    # Utiliza una expresión regular para extraer la fecha en formato año-mes-día
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern, date)

    if match:
        article_date = datetime.strptime(match.group(1), '%Y-%m-%d')
        # Comprueba si la fecha está dentro del rango de 24 horas
        if current_date.date() == article_date.date() or current_date.date() - article_date.date() == timedelta(days=1):
            valid_date = date

    return valid_date

# Function to extract image URLs from the HTML content
def extract_image_urls(html):
    image_urls = []
    soup = BeautifulSoup(html, 'html.parser')
    img_elements = soup.find_all('img')
    
    for img in img_elements:
        src = img.get('src')
        if src and src.startswith('https://s32679.pcdn.co/'):
            image_urls.append(src)
    
    return image_urls

# Load keywords from the JSON file
with open('keywords.json', 'r') as json_file:
    keywords_data = json.load(json_file)

# Create a function to validate content
keyword_dict = {}
for entry in keywords_data:
    if 'main_keyword' in entry:
        main_keyword = entry['main_keyword']
        keywords = entry.get('keywords', [])
        keyword_dict[main_keyword] = keywords

# Function to validate the article using keywords
def validate_article(article_link, keywords_dict):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
        }
    
    article_response = requests.get(article_link, headers=headers)
    article_content_type = article_response.headers.get("Content-Type", "").lower() 

    if article_response.status_code == 200 and 'text/html' in article_content_type:
        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        title_element = article_soup.find('h1')
        title = title_element.text.strip() if title_element else None 

        contains_keyword = False
        
        # Search for keywords in the title
        for main_keyword, keywords in keywords_dict.items():
            if main_keyword.lower() in title.lower():
                contains_keyword = True
                break

        # If no keyword was found in the title, search in the content
        if not contains_keyword:
            content = ""
            all_p_elements = article_soup.findAll("p")
            for el in all_p_elements:
                content += el.text.lower()

            for main_keyword, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword.lower() in content:
                        contains_keyword = True
                        break
                if contains_keyword:
                    break

        date_time_element = article_soup.find('time')
        date = date_time_element['datetime'].strip() if date_time_element and 'datetime' in date_time_element.attrs else None
        valid_date = validate_date_beincrypto(date)

        # Extract image URLs from the article
        image_urls = extract_image_urls(article_response.text)

        # Comprueba si contiene palabra clave y si la fecha es válida
        if contains_keyword and valid_date:
            print(content, valid_date)
            print("Image URLs:", image_urls)
            return content, valid_date
        else:
            print("The article does not meet the required conditions.")
            return None, None

    print("Title:", title)
    print("Keywords Dict:", keywords_dict)

# Llama a la función con el enlace del artículo
validate_article('https://es.beincrypto.com/aprende/bonos-corredor-bolsa-libertex/', keyword_dict)
