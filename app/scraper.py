# app/scraper.py
import feedparser
from bs4 import BeautifulSoup
import requests

class NewsScraper:
    SOURCES = {
        'cnn': 'http://rss.cnn.com/rss/cnn_topstories.rss',
        'bbc': 'http://feeds.bbci.co.uk/news/rss.xml'
    }

    def scrape(self, url):
        feed = feedparser.parse(url)
        return [{'title': e.title, 'url': e.link} for e in feed.entries[:10]]
    
    def extract_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return ' '.join(p.text for p in soup.find_all('p'))