import aiohttp
import asyncio
import feedparser
import os
import urllib.parse

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

async def fetch_json(session, url, params=None, headers=None, method="GET", json_body=None):
    try:
        async with session.request(method, url, params=params, headers=headers, json=json_body) as response:
            return await response.json()
    except Exception:
        return {}

async def async_search_with_cse(session, keyword):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": keyword,
        "cx": GOOGLE_CSE_ID,
        "key": SERPAPI_KEY,
        "hl": "fr",
        "num": 5
    }
    data = await fetch_json(session, url, params=params)
    return [{
        "keyword": keyword,
        "title": r.get("title", ""),
        "link": r.get("link", ""),
        "snippet": r.get("snippet", "")
    } for r in data.get("items", [])]

async def async_search_with_perplexity(session, keyword):
    url = "https://api.perplexity.ai/search"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"q": keyword, "source": "web", "autocomplete": False}
    data = await fetch_json(session, url, headers=headers, method="POST", json_body=payload)
    return [{
        "keyword": keyword,
        "title": r.get("title", ""),
        "link": r.get("url", ""),
        "snippet": r.get("snippet", ""),
        "date": r.get("published_at", "")
    } for r in data.get("results", [])]

async def async_search_arxiv(session, keyword):
    query = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(keyword)}&start=0&max_results=5"
    loop = asyncio.get_event_loop()
    feed = await loop.run_in_executor(None, feedparser.parse, query)
    return [{
        "keyword": keyword,
        "title": entry.title,
        "link": entry.link,
        "snippet": entry.summary
    } for entry in feed.entries]

async def async_search_consensus(session, keyword):
    url = "https://serpapi.com/search"
    params = {
        "q": f"{keyword} site:consensus.app",
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "hl": "fr",
        "gl": "ca",
        "num": 5
    }
    data = await fetch_json(session, url, params=params)
    return [{
        "keyword": keyword,
        "title": r.get("title", ""),
        "link": r.get("link", ""),
        "snippet": r.get("snippet", "")
    } for r in data.get("organic_results", [])]

async def run_async_sources(keywords, use_cse, use_perplexity, use_arxiv, use_consensus):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for keyword in keywords:
            if use_cse:
                tasks.append(async_search_with_cse(session, keyword))
            if use_perplexity:
                tasks.append(async_search_with_perplexity(session, keyword))
            if use_arxiv:
                tasks.append(async_search_arxiv(session, keyword))
            if use_consensus:
                tasks.append(async_search_consensus(session, keyword))

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for batch in responses:
            if isinstance(batch, Exception):
                continue
            results.extend([item for item in batch if item and item.get("title")])
    return results

__all__ = ['run_async_sources']
