from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import sessionmaker

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


# status of the whole bot

class NEWS_BOT_SETTINGS(Base):
    __tablename__ = 'news_bot_setting'

    id = Column(Integer, primary_key=True)
    is_bot_active = Column(Boolean)
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
    keyword_info_id = Column(Integer, ForeignKey('scrapping_data.id'))
    keyword = Column(String)  
    created_at = Column(DateTime, default=datetime.utcnow) 

class SITES(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    keyword_info_id = Column(Integer, ForeignKey('scrapping_data.id'))
    site = Column(String)  
    base_url = Column(String)  
    website_name = Column(String)  
    is_URL_complete = Column(Boolean)  
    created_at = Column(DateTime, default=datetime.utcnow) 

# export the connection

Base.metadata.create_all(engine)
session = Session()   


# create the default status of the whole bot

if session.query(NEWS_BOT_SETTINGS).count() == 0:
    first_record = NEWS_BOT_SETTINGS(is_bot_active=False)
    session.add(first_record)
    session.commit()         