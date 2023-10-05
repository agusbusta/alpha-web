def validate_date_bitcoinist(date_div):
   
    DAY_KEYWORD = 'day'
    MIN_KEYWORD = 'min'
    HOUR_KEYWORD = 'hour'
    
    if not date_div:
        return None

    date_link = date_div.find('a')
    if not date_link:
        return None

    date_string = date_link.text.strip()
    if not date_string:
        return None

    if DAY_KEYWORD in date_string:
        days_ago = int(date_string.split()[0])
        if days_ago > 1:
            return None
        return date_string

    if MIN_KEYWORD in date_string or HOUR_KEYWORD in date_string:
        return date_string

    return None

def find_date_and_images_bitcoinist(article_soup, images_elements):
  
    date_time_element = article_soup.find('div', class_='jeg_meta_date')
    date = validate_date_bitcoinist(date_time_element)

    image_urls = []
    for img in images_elements:
        src = img.get('src')
        if src and src.startswith('https://s3.cointelegraph.com/uploads') and (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.webp')):
            image_urls.append(src)
    
    return image_urls, date