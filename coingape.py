import datetime

def validate_date_coingape(date):
    valid_date = None

    try:
        if date:
            date_string = str(date).casefold().strip()
            current_date = datetime.now()
            present_day = current_date.day
            present_month = current_date.strftime("%B").casefold()

            if f"{present_month} {present_day}" in date_string:
                valid_date = date_string
            elif 'day' in date_string or 'hour' in date_string:
                if 'day' in date_string:
                   
                    formatted_date = date_string.split()[0]
                 
                    if formatted_date == '1':
                        valid_date = date_string
                else:
                    valid_date = date_string
            else:
                valid_date = None
    except Exception as e:
        valid_date = None

    return valid_date

def find_date_and_images_coingape(article_soup, images_elements):

    date_time_element = article_soup.find('div', class_='publishby d-flex')
    date = date_time_element.text.strip() if date_time_element else None
    date = validate_date_coingape(date)

    image_urls = []
    for img in images_elements:
        src = img.get('src')
        if src and src.startswith('https://s3.cointelegraph.com/uploads') and (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.webp')):
            image_urls.append(src)
    
    return image_urls, date
