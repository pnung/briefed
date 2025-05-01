from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(300))
    url = Column(String(500), unique=True)
    source = Column(String(50))
    content = Column(Text)
    summary = Column(Text)