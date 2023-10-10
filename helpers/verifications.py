from db import session, ARTICLE, SCRAPPING_DATA, BLACKLIST
from difflib import SequenceMatcher
import ahocorasick 

def title_in_db(input_title): #  true if title in db

    try:
        all_title = session.query(ARTICLE.title).all()
        title_list = [item[0].strip() for item in all_title]

        similarity_threshold = 0.9
        is_title_in_db = False
  
        for title in title_list:
            title_similarity_ratio = SequenceMatcher(None, input_title.casefold(), title.casefold()).ratio()

            if title_similarity_ratio >= similarity_threshold:
                is_title_in_db = True
                break

        return is_title_in_db
    except Exception as e:
        print(f'error in title_in_db: {str(e)}')
        return f'error in title_in_db: {str(e)}'

def url_in_db(input_url): #  true if url in db

    try:
        all_url = session.query(ARTICLE.url).all()
        url_list = [item[0].strip() for item in all_url]

        similarity_threshold = 0.9
        is_url_in_db = False
  
        for url in url_list:
            url_similarity_ratio = SequenceMatcher(None, input_url.casefold(), url.casefold()).ratio()

            if url_similarity_ratio >= similarity_threshold:
                is_url_in_db = True
                break

        return is_url_in_db
    except Exception as e:
        print(f'error in url_in_db: {str(e)}')
        return f'error in url_in_db: {str(e)}'

def validate_content(main_keyword, content):
    try:
        # Query the database for the SCRAPPING_DATA objects with a case-insensitive match for main_keyword
        scrapping_data_objects = session.query(SCRAPPING_DATA).filter(SCRAPPING_DATA.main_keyword == main_keyword.casefold()).all()

        keywords = scrapping_data_objects[0].keywords
        keyword_values = [keyword.keyword.casefold() for keyword in keywords]  # List of case-folded keywords

        A = ahocorasick.Automaton()
        for idx, keyword in enumerate(keyword_values):
            A.add_word(keyword, (idx, keyword))
        A.make_automaton()

        for _, keyword in A.iter(content.casefold()):
            return True

        return False
    except Exception as e:
        print(f'error in validate_content: {str(e)}')
        return f'error in validate_content: {str(e)}'

def title_in_blacklist(input_title_formatted):

    try:
        black_list = session.query(BLACKLIST).all()
        black_list_values = [keyword.black_Word for keyword in black_list] # list of blacklist

        is_title_in_blacklist = False
        similarity_threshold = 0.9

        for title in black_list_values:
            title_similarity_ratio = SequenceMatcher(None, input_title_formatted.casefold(), title.casefold()).ratio()
        
            if title_similarity_ratio >= similarity_threshold:
                is_title_in_blacklist = True
                break

        return is_title_in_blacklist
    
    except Exception as e:
        print(f'error in title_in_blacklist: {str(e)}')
        return f'error in title_in_blacklist: {str(e)}'




