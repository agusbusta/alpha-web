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
            title_similarity_ratio = SequenceMatcher(None, input_title, title).ratio()

            if title_similarity_ratio >= similarity_threshold:
                is_title_in_db = True
                break

        return is_title_in_db
    except:
        return 'error in title_in_db'

def url_in_db(input_url): #  true if url in db

    try:
        all_url = session.query(ARTICLE.url).all()
        url_list = [item[0].strip() for item in all_url]

        similarity_threshold = 0.9
        is_url_in_db = False
  
        for url in url_list:
            url_similarity_ratio = SequenceMatcher(None, input_url, url).ratio()

            if url_similarity_ratio >= similarity_threshold:
                is_url_in_db = True
                break

        return is_url_in_db
    except:
        return 'error in url_in_db'

def validate_content(main_keyword, content):

    try:   
        scrapping_data_objects = session.query(SCRAPPING_DATA).filter(SCRAPPING_DATA.main_keyword == main_keyword).all()

        keywords = scrapping_data_objects[0].keywords
        keyword_values = [keyword.keyword for keyword in keywords] # list of keywords
        
        A = ahocorasick.Automaton()
        for idx, keyword in enumerate(keyword_values):
            A.add_word(keyword, (idx, keyword))
        A.make_automaton()
        
        for _, keyword in A.iter(content):
            return True
        
        return False
    except:
        return 'error in validate_content'

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
    
    except:
        return 'error in title_in_blacklist'




