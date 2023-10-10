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


def validate_date_coingape(html):
    # Encuentra el div con clase 'publishby d-flex'
    date_div = html.find('div', class_='publishby d-flex')

    if date_div:
        # Verifica si el texto del div contiene "mins ago" o "hours ago"
        date_text = date_div.text.lower()
        if "mins ago" in date_text or "hours ago" in date_text:
            return True

    return False



def extract_image_urls(html):
    image_urls = []
    soup = BeautifulSoup(html, 'html.parser')
    img_elements = soup.find_all('img')

    for img in img_elements:
        src = img.get('src')

        if src and src.startswith('https://coingape.com/wp-content/uploads/'):
            image_urls.append(src)

    return image_urls


with open('/Users/agustin/Desktop/alphaWeb/data.json', 'r') as json_file:
    keywords_data = json.load(json_file)


# Create a function to validate content
keyword_dict = {}
for entry in keywords_data:
    if 'main_keyword' in entry:
        main_keyword = entry['main_keyword']
        keywords = entry.get('keywords', [])
        keyword_dict[main_keyword] = keywords
        
def extract_article_content(html):
    # Encuentra el div con el ID 'main-content'
    main_content_div = html.find('div', id='main-content')

    if main_content_div:
        # Encuentra todas las etiquetas 'p' dentro del div 'main-content'
        p_elements = main_content_div.find_all('p')
        
        # Inicializa el contenido del artículo
        content = ""
        
        # Recorre todas las etiquetas 'p' y extrae el texto de las etiquetas 'span' dentro de ellas
        for p_element in p_elements:
            span_elements = p_element.find_all('span')
            for span_element in span_elements:
                content += span_element.text.strip() + " "
        
        return content.strip()

    return None



# Function to validate the article using keywords
def validate_article(article_link, keywords_dict):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
        }
    
    article_response = requests.get(article_link, headers=headers)
    article_content_type = article_response.headers.get("Content-Type", "").lower() 

    content = ""  # Inicializa content aquí
    html = BeautifulSoup(article_response.text, 'html.parser')  # Parsea el HTML del artículo

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

        # Extract article content using the new function
        content = extract_article_content(article_soup)


        # If no keyword was found in the title, search in the content
        if not contains_keyword:
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

        # Llama a validate_date_bitcoinist con el contenido HTML del artículo
        valid_date = validate_date_coingape(html)

        # Extract image URLs from the article
        image_urls = extract_image_urls(article_response.text)

        if contains_keyword and valid_date:
            print("Content:", content)
            print("Valid Date:", valid_date)
            print("Image URLs:", image_urls)
            return content, valid_date
        else:
            print("The article does not meet the required conditions.")

    print("Title:", title)
    print("Keywords Dict:", keywords_dict)



# Llama a la función con el enlace del artículo
validate_article('https://coingape.com/weekly-recap-crypto-market-remains-strong-btc-eth-rally/', keyword_dict)
