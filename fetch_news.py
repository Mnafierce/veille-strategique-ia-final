import os
import requests
import feedparser
from bs4 import BeautifulSoup

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def run_news_crawl(keywords, use_google_news=True):
    articles = []
    for keyword in keywords:
        if use_google_news:
            articles.extend(fetch_google_news(keyword))
    return articles

def fetch_google_news(keyword):
    try:
        url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}+when:7d&hl=fr&gl=FR&ceid=FR:fr"
        feed = feedparser.parse(url)
        news_list = []
        for entry in feed.entries[:5]:
            news_list.append({
                "keyword": keyword,
                "title": clean_text(entry.title),
                "link": entry.link,
                "snippet": clean_html(entry.summary),
                "date": entry.get("published", "")[:10] if entry.get("published") else ""
            })
        return news_list
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur Google News", "link": "", "snippet": str(e)}]

def clean_html(raw_html):
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text()
    except Exception:
        return raw_html

def clean_text(text):
    if text:
        return text.encode('utf-8', 'ignore').decode('utf-8')
    return ""
