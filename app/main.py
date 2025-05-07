from fastapi import FastAPI, BackgroundTasks, Query
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

@app.get("/articles")
def get_articles(source: str = Query(None), limit: int = 20):
    session = db.get_session()
    query = session.query(Article)
    if source:
        query = query.filter(Article.source == source)
    return query.order_by(Article.id.desc()).limit(limit).all()

@app.get("/summary/{url:path}")
def get_summary(url: str):
    cached = cache.get(f"summary:{url}")
    if cached:
        return cached
    
    session = db.get_session()
    article = session.query(Article).filter_by(url=url).first()
    if not article:
        return {"error": "Article not found"}
    
    cache.set(f"summary:{url}", article.summary)
    return article.summary

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
    session = db.get_session()
    for source, url in NewsScraper.SOURCES.items():
        articles = scraper.scrape(url)
        for article in articles:
            # Skip if already exists
            if session.query(Article).filter_by(url=article['url']).first():
                continue
                
            content = scraper.extract_content(article['url'])
            summary = summarizer.summarize(content)
            
            # Save to DB
            new_article = Article(
                title=article['title'],
                url=article['url'],
                source=source,
                content=content,
                summary=summary
            )
            session.add(new_article)
            
            cache.set(f"summary:{article['url']}", summary)
    
    session.commit()
    session.close()