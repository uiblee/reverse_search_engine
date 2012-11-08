from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('postgresql://localhost/search_engine', echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement = True, primary_key = True)
    username = Column(String(64))
    password = Column(String(64))
    

    def __init__(self, username, password):
        self.username = username
        self.password = password

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
