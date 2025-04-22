import os
import requests
import json
import google.generativeai as genai

# Chargement des clés via variables d’environnement (sécurisé)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------- 1. GEMINI (Google Generative AI) ------------------

def search_with_gemini(prompt, temperature=0.4):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Erreur Gemini] {e}"

# ----------- 2. SERPAPI (Recherche Web via Google Search) ------------------

def search_with_serpapi(keyword):
    url = "https://serpapi.com/search"
    params = {
        "q": keyword,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "hl": "fr",
        "gl": "ca"
    }

    try:
        response = requests.get(url, params=params)
        results = response.json().get("organic_results", [])
        formatted = []
        for result in results:
            formatted.append({
                "keyword": keyword,
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet", "")
            })
        return formatted
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur SerpAPI", "link": "", "snippet": str(e)}]

# ----------- 3. Google Programmable Search Engine (Custom Search API) ------------------

def search_with_google_cse(keyword):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": keyword,
        "cx": GOOGLE_CSE_ID,
        "key": SERPAPI_KEY,  # ou clé d'API Google si distincte
        "hl": "fr"
    }

    try:
        response = requests.get(url, params=params)
        results = response.json().get("items", [])
        formatted = []
        for result in results:
            formatted.append({
                "keyword": keyword,
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet", "")
            })
        return formatted
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur Google CSE", "link": "", "snippet": str(e)}]
