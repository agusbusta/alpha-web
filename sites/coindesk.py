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

def validate_date_coindesk(html):
    # Encuentra el span con la clase 'typography__StyledTypography-sc-owin6q-0 hcIsFR'
    date_span = html.find('span', class_='typography__StyledTypography-sc-owin6q-0 hcIsFR')

    if date_span:
        date_text = date_span.text.strip()
        
        # Utiliza una expresión regular para extraer el día y el mes del texto de la fecha
        match = re.search(r'(\w+) (\d+), (\d+)', date_text)
        
        if match:
            month_str, day_str, year_str = match.groups()
            current_date = datetime.now()
            
            # Convierte el mes a número utilizando un diccionario de mapeo
            months = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            month = months.get(month_str)
            day = int(day_str)
            year = int(year_str)
            
            # Comprueba si el día, mes y año coinciden con la fecha actual
            if year == current_date.year and month == current_date.month and day == current_date.day:
                return True

    return False



def extract_image_urls_coindesk(html):
    image_urls = []
    soup = BeautifulSoup(html, 'html.parser')
    img_elements = soup.find_all('img')

    for img in img_elements:
        src = img.get('src')

        if src and src.startswith('https://www.coindesk.com/resizer/'):
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

        # Busca el div con la clase 'at-content-wrapper'
        content_div = article_soup.find('div', class_='at-content-wrapper')

        if content_div:
            # Encuentra todos los párrafos (etiquetas <p>) dentro del div
            paragraphs = content_div.find_all('p')

            # Concatena el texto de todos los párrafos para obtener el contenido del artículo
            content = "\n".join(paragraph.text.strip() for paragraph in paragraphs)

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
            for main_keyword, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        contains_keyword = True
                        break
                if contains_keyword:
                    break

        valid_date = validate_date_coindesk(html)

        # Extract image URLs from the article
        image_urls = extract_image_urls_coindesk(article_response.text)

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
validate_article('https://www.coindesk.com/markets/2023/10/10/billionaire-paul-tudor-jones-backs-bitcoin-and-gold-as-geopolitical-risks-rise/?_gl=1*pd5d34*_up*MQ..*_ga*MTYzMjI4OTQxMC4xNjk2OTU4ODEz*_ga_VM3STRYVN8*MTY5Njk1ODgxMy.1.1.1.1.1', keyword_dict)
