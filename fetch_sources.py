import os
import requests
import feedparser
import google.generativeai as genai
from openai import OpenAI

# Chargement des clés API
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialisation des clients
genai.configure(api_key=GEMINI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ----------- Gemini (fallback ou synthèse) ------------------
def search_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("models/chat-bison-001")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Erreur Gemini] {e}"

# ----------- OpenAI synthèse ------------------
def search_with_openai(question):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant de recherche stratégique."},
                {"role": "user", "content": f"Fais une synthèse des tendances sur : {question}"}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        # fallback Gemini
        try:
            return search_with_gemini(f"Synthèse sur {question}")
        except Exception as e2:
            return f"[Erreur complète OpenAI+Gemini] {e2}"

# ----------- Consensus (via SerpAPI) ------------------
def search_consensus_via_serpapi(keyword):
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": f"{keyword} site:consensus.app",
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "hl": "fr",
            "gl": "ca",
            "num": 5
        }
        response = requests.get(url, params=params)
        results = response.json().get("organic_results", [])
        return [{
            "keyword": keyword,
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet", "")
        } for r in results]
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur Consensus", "link": "", "snippet": str(e)}]

# ----------- ArXiv ------------------
def search_arxiv(keyword):
    try:
        query = f"http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=5"
        feed = feedparser.parse(query)
        return [{
            "keyword": keyword,
            "title": entry.title,
            "link": entry.link,
            "snippet": entry.summary
        } for entry in feed.entries]
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur ArXiv", "link": "", "snippet": str(e)}]

# ----------- Google Custom Search Engine ------------------
def search_with_google_cse(keyword):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": keyword,
            "cx": GOOGLE_CSE_ID,
            "key": SERPAPI_KEY,
            "hl": "fr",
            "num": 5
        }
        response = requests.get(url, params=params)
        results = response.json().get("items", [])
        return [{
            "keyword": keyword,
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet", "")
        } for result in results]
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur Google CSE", "link": "", "snippet": str(e)}]

# ----------- Recherche classique via SerpAPI ------------------
def search_with_serpapi(keyword):
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": keyword,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "hl": "fr",
            "gl": "ca",
            "num": 5
        }
        response = requests.get(url, params=params)
        results = response.json().get("organic_results", [])
        return [{
            "keyword": keyword,
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet", "")
        } for result in results]
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur SerpAPI", "link": "", "snippet": str(e)}]

# ----------- Perplexity (non officiel ou clé privée) ------------------
def search_with_perplexity(query):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "source": "web",
            "autocomplete": False
        }
        response = requests.post("https://api.perplexity.ai/search", headers=headers, json=payload)
        data = response.json()

        articles = []
        for item in data.get("results", [])[:5]:
            articles.append({
                "keyword": query,
                "title": item.get("title"),
                "link": item.get("url"),
                "snippet": item.get("snippet", ""),
                "date": item.get("published_at") or None
            })
        return articles
    except Exception as e:
        return [{
            "keyword": query,
            "title": "Erreur Perplexity",
            "link": "",
            "snippet": str(e),
            "date": None
        }]
