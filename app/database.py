from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from .models import Base
from .logger import logger
import os

class Database:
    def __init__(self):
        self.engine = None
        self.Session = None
        self._setup_engine()

    def _setup_engine(self):
        try:
            self.engine = create_engine(
                f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
                f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}",
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600
            )
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info("Database engine initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def init_db(self):
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created")
        except SQLAlchemyError as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def get_session(self):
        if not self.Session:
            self._setup_engine()
        return self.Session()

    def close_session(self):
        if self.Session:
            self.Session.remove()