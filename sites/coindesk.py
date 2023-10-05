import datetime

def validate_date_coindesk(date):

    is_valid_date = None

    if date:

        try:
            date = str(date).casefold().strip()
            current_date = datetime.utcnow().strftime("%b %d, %Y at %I:%M %p UTC").casefold().strip()

            day = date.split(" ")[0] 
            month = date.split(" ")[1]
    
            if day in current_date and month in current_date:
                is_valid_date = date
            else:
                is_valid_date = None

        except Exception:
            is_valid_date = None

    return is_valid_date

def find_date_and_images_coindesk(article_soup, images_elements):

    date_time_element = article_soup.find('span', class_='typography__StyledTypography-sc-owin6q-0 hcIsFR')
    date = date_time_element.text.strip() if date_time_element else None
    date = validate_date_coindesk(date)

    image_urls = []
    for img in images_elements:
        src = img.get('src')
        if src and src.startswith('https://s3.cointelegraph.com/uploads') and (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.webp')):
            image_urls.append(src)
    
    return image_urls, date