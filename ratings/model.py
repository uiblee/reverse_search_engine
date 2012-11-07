from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

Base = declarative_base()

### Class declarations go here

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    username = Column(String(64))
    password = Column(String(64))
    

    def __init__(self, username, password):
        self.username = username
        self.password = password
          

### End class declarations

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
