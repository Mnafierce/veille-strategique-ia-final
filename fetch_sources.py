import os
import requests
import google.generativeai as genai
from openai import OpenAI

# Chargement sécurisé des clés API
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Clients API
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("models/gemini-pro")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ----------- 1. GEMINI ------------------

def search_with_gemini(prompt, temperature=0.4):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Erreur Gemini] {str(e)}"

# ----------- 2. SERPAPI ------------------

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

# ----------- 3. Google Programmable Search Engine ------------------

def search_with_google_cse(keyword):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": keyword,
        "cx": GOOGLE_CSE_ID,
        "key": SERPAPI_KEY,  # ou une clé API Google si différente
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
