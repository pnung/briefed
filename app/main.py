from fastapi import FastAPI, BackgroundTasks
from .scraper import NewsScraper
from .summarizer import TextRankSummarizer
from .database import Database
from .utils.cache import RedisCache
import asyncio

app = FastAPI()
scraper = NewsScraper()
summarizer = TextRankSummarizer()
db = Database()
cache = RedisCache()

@app.on_event("startup")
async def startup_event():
    db.init_db()
    asyncio.create_task(scheduled_scraping())

async def scheduled_scraping():
    while True:
        await scrape_all_sources()
        await asyncio.sleep(300)  # 5 minutes

@app.get("/scrape")
async def trigger_scrape():
    BackgroundTasks.add_task(scrape_all_sources)
    return {"status": "scraping started"}

async def scrape_all_sources():
    pass