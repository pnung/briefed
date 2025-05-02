# app/worker.py
import asyncio
from .scraper import NewsScraper
from .summarizer import TextRankSummarizer
from .database import Database
from .utils.cache import RedisCache
from .utils.logger import setup_logger

logger = setup_logger()

async def run_scraping():
    scraper = NewsScraper()
    summarizer = TextRankSummarizer()
    db = Database()
    cache = RedisCache()
    
    while True:
        try:
            logger.info(f"Scraped {len(articles)} new articles")
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
        await asyncio.sleep(300)