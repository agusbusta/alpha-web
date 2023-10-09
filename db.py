from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pathlib import Path
import json
from sqlalchemy.orm import sessionmaker

THIS_FOLDER = Path(__file__).parent.resolve()

DB_NAME='aialpha'    
DB_USER='postgres' 
DB_PASSWORD='postgres'
DB_PORT=5432
DB_HOST='localhost'


db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# data of each article

class ARTICLE(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String)  
    content = Column(String)   
    date = Column(String)   
    url = Column(String)   
    website_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) 
    images = relationship("IMAGE", cascade="all, delete-orphan")

class IMAGE(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)   


# data of the sites

class SCRAPPING_DATA(Base):
    __tablename__ = 'scrapping_data'

    id = Column(Integer, primary_key=True)
    main_keyword = Column(String)
    keywords = relationship("KEWORDS", cascade="all, delete-orphan")
    sites = relationship("SITES", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=datetime.utcnow) 

class KEWORDS(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True)
    keyword_info_id = Column(Integer, ForeignKey('scrapping_data.id'), nullable=False)
    keyword = Column(String)  
    created_at = Column(DateTime, default=datetime.utcnow) 

class BLACKLIST(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    black_Word = Column(String)  
    created_at = Column(DateTime, default=datetime.utcnow) 

class SITES(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    keyword_info_id = Column(Integer, ForeignKey('scrapping_data.id'), nullable=False)
    site = Column(String)  
    base_url = Column(String)  
    website_name = Column(String)  
    is_URL_complete = Column(Boolean)  
    created_at = Column(DateTime, default=datetime.utcnow) 

# export the connection

Base.metadata.create_all(engine)
session = Session()  

if not session.query(BLACKLIST).first():
        
    with open(f'{THIS_FOLDER}/data.json', 'r') as data_file:
        config = json.load(data_file)

    black_list = config[-1]
    
    for word in black_list['black_list']:
        list_blackword=BLACKLIST(black_Word=word)
        session.add(list_blackword)

    session.commit()

   
if not session.query(SCRAPPING_DATA).first():

    with open(f'{THIS_FOLDER}/data.json', 'r') as data_file:
        config = json.load(data_file)

    for item in config[:-1]:   
        keyword = item['main_keyword']
        keywords = item['keywords']
        sites = item['sites']

        scrapping_data = SCRAPPING_DATA(main_keyword=keyword)

        for keyword in keywords:
            scrapping_data.keywords.append(KEWORDS(keyword=keyword))

        for site_data in sites:
            site = SITES(
                site=site_data['site'],
                base_url=site_data['base_url'],
                website_name=site_data['website_name'],
                is_URL_complete=site_data['is_URL_complete']
            )
            scrapping_data.sites.append(site)

        
        session.add(scrapping_data)

    print('initial data saved to db')
    session.commit()

     