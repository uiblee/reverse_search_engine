from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# engine = create_engine('postgresql://localhost/search_engine', echo=False)

# what i use for localhost
#engine = create_engine('postgresql://localhost/search_engine', echo=False)
#session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

#what i would need for heroku and change lines in main file
db_uri = os.environ.get("DATABASE_URL", 'postgresql://localhost/search_engine')
engine = create_engine(db_uri, echo = False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement = True, primary_key = True)
    username = Column(String(64))
    password = Column(String(64))
    facebook_token = Column(String(128), nullable = True)
    linkedin_token = Column(String(128), nullable = True)
    google_token = Column(String(128), nullable = True)
    twitter_token = Column(String(128), nullable = True)
    crm_token = Column(String(128), nullable = True)
    keywords = Column(Text, nullable = True)


    def __init__(self, username, password, facebook_token = None, linkedin_token = None,
        google_token = None, twitter_token = None, crm_token = None, keywords = None):
        self.username = username
        self.password = password
        self.facebook_token = facebook_token
        self.linkedin_token = linkedin_token
        self.google_token = google_token
        self.twitter_token = twitter_token
        self.crm_token = crm_token
        self.keywords = keywords

    @classmethod
    def new_user(cls, username, password):
        new_user = User(username, password)
        session.add(new_user)
        session.commit()
          

### End class declarations

# def connect():
#     global ENGINE
#     global Session

#     ENGINE = create_engine('postgresql://localhost/search_engine')
#     Session = sessionmaker(bind=ENGINE)

#     return Session()

def main():
    """In case we need this for something"""
    
    pass

if __name__ == "__main__":

    main()
