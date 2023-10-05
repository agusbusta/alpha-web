import datetime

def validate_date_cointelegraph(date):
    is_valid_date = None
    
    try:
        if date:
            article_date = datetime.strptime(date, '%Y-%m-%d')
            if article_date.date() == datetime.now().date():
                is_valid_date = date
    except Exception:
        is_valid_date = None

    return is_valid_date
        
def find_date_and_images_cointelegraph(article_soup, images_elements):

    date_time_element = article_soup.find('time')
    date = date_time_element['datetime'].strip() if date_time_element and 'datetime' in date_time_element.attrs else None
    date = validate_date_cointelegraph(date)

    image_urls = []
    for img in images_elements:
        src = img.get('src')
        if src and src.startswith('https://s3.cointelegraph.com/uploads') and (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.webp')):
            image_urls.append(src)
    
    return image_urls, date