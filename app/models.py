from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('ix_articles_source_created_at', 'source', 'created_at'),
        Index('ix_articles_created_at', 'created_at'),
    )