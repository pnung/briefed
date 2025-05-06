import feedparser
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse
from .logger import logger
import time

class NewsScraper:
    def __init__(self):
        self.SOURCES = {
            'cnn': 'http://rss.cnn.com/rss/cnn_topstories.rss',
            'bbc': 'http://feeds.bbci.co.uk/news/rss.xml'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BriefedBot/1.0 (+https://github.com/yourusername/briefed)'
        })

    def scrape(self, url: str) -> List[Dict[str, str]]:
        try:
            feed = feedparser.parse(url)
            return [{
                'title': entry.title,
                'url': entry.link,
                'published': entry.get('published', '')
            } for entry in feed.entries[:10]]
        except Exception as e:
            logger.error(f"Failed to parse feed {url}: {e}")
            return []

    def extract_content(self, url: str) -> Optional[str]:
        try:
            domain = urlparse(url).netloc
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Domain-specific extraction rules
            if 'cnn.com' in domain:
                return self._extract_cnn(soup)
            elif 'bbc.co.uk' in domain:
                return self._extract_bbc(soup)
            
            # Default extraction
            return ' '.join(p.get_text().strip() for p in soup.find_all('p'))
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return None