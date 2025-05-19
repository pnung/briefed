import asyncio
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Request
from .scraper import NewsScraper
from .summarizer import TextRankSummarizer
from .database import Database
from .utils.cache import RedisCache
from .utils.logger import logger
from .monitoring import (
    start_monitoring,
    record_request_metrics,
    record_scrape_metrics,
    record_db_metrics
)

app = FastAPI(
    title="Briefed News Aggregator",
    description="High-throughput news aggregator with custom summarization",
    version="1.0.0"
)

# Initialize components
scraper = NewsScraper()
summarizer = TextRankSummarizer()
db = Database()
cache = RedisCache()

start_monitoring()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        db.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    
    # Start background scraping task
    asyncio.create_task(scheduled_scraping())
    logger.info("Scheduled scraping task started")

async def scheduled_scraping():
    """Background task for periodic scraping"""
    while True:
        try:
            await scrape_all_sources()
        except Exception as e:
            logger.error(f"Scheduled scraping failed: {str(e)}")
        await asyncio.sleep(300)  # 5 minutes

@app.get("/scrape", summary="Trigger manual scraping")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger immediate scraping of all news sources"""
    background_tasks.add_task(scrape_all_sources)
    return {"status": "scraping started", "sources": list(scraper.SOURCES.keys())}

async def scrape_all_sources():
    """Scrape all configured news sources"""
    start_time = time.time()
    logger.info("Starting scraping of all sources")
    
    try:
        session = db.get_session()
        for source, url in scraper.SOURCES.items():
            source_start = time.time()
            try:
                logger.info(f"Scraping {source}: {url}")
                articles = scraper.scrape(url)
                logger.info(f"Found {len(articles)} articles from {source}")
                
                for article in articles:
                    if session.query(Article).filter_by(url=article['url']).first():
                        continue  # Skip existing articles
                    
                    # Extract and summarize content
                    content = scraper.extract_content(article['url'])
                    summary = summarizer.summarize(content)
                    
                    # Save to database
                    article_record = Article(
                        title=article['title'],
                        url=article['url'],
                        source=source,
                        content=content,
                        summary=summary
                    )
                    session.add(article_record)
                    
                    # Cache summary
                    cache.set(f"summary:{article['url']}", summary)
                
                session.commit()
                
                # Record metrics
                duration = time.time() - source_start
                record_scrape_metrics(source, duration)
                logger.info(f"Completed {source} in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to scrape {source}: {str(e)}")
                session.rollback()
        
        logger.info(f"Completed all scraping in {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
    finally:
        session.close()

@app.get("/articles", summary="Retrieve articles")
async def get_articles(
    request: Request,
    source: str = Query(None, description="Filter by news source"),
    limit: int = Query(20, description="Number of articles to return")
):
    """Retrieve articles from the database"""
    start_time = time.time()
    try:
        session = db.get_session()
        query = session.query(Article).order_by(Article.created_at.desc())
        
        if source:
            query = query.filter(Article.source == source)
        
        articles = query.limit(limit).all()
        
        # Record metrics
        duration = time.time() - start_time
        record_request_metrics(
            request.method, 
            request.url.path, 
            200,
            duration
        )
        record_db_metrics("query", duration)
        
        return articles
        
    except Exception as e:
        logger.error(f"Failed to retrieve articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        session.close()

@app.get("/summary/{url:path}", summary="Get article summary")
async def get_summary(request: Request, url: str):
    """Get summary for a specific article URL"""
    start_time = time.time()
    try:
        # Check cache first
        cached_summary = cache.get(f"summary:{url}")
        if cached_summary:
            return {"summary": cached_summary, "source": "cache"}
        
        # If not in cache, check database
        session = db.get_session()
        article = session.query(Article).filter_by(url=url).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Cache the summary
        cache.set(f"summary:{url}", article.summary)
        
        # Record metrics
        duration = time.time() - start_time
        record_request_metrics(
            request.method, 
            request.url.path, 
            200,
            duration
        )
        
        return {"summary": article.summary, "source": "database"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")
    finally:
        session.close()

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Middleware to monitor all requests"""
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        status_code = 500
        if hasattr(e, 'status_code'):
            status_code = e.status_code
        duration = time.time() - start_time
        record_request_metrics(
            request.method, 
            request.url.path, 
            status_code,
            duration
        )
        raise
    
    duration = time.time() - start_time
    record_request_metrics(
        request.method, 
        request.url.path, 
        response.status_code,
        duration
    )
    return response