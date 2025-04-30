import os
import openai
import traceback
from collections import defaultdict
from fetch_sources import search_with_gemini

openai.api_key = os.getenv("OPENAI_API_KEY") or ""

INNOVATION_KEYWORDS = [
    "GPT-4", "LLM", "IA générative", "agentic AI", "automatisation intelligente",
    "rupture technologique", "machine learning", "AI startup funding"
]

always_use_keywords = [
    "agents intelligents", "intelligence artificielle", "AI in Finance"
]

def summarize_text_block(text):
    if not text.strip() or not openai.api_key:
        return "Résumé exécutif indisponible"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un analyste stratégique. Résume ce contenu pour un décideur."},
                {"role": "user", "content": text[:1000]}
            ],
            temperature=0.4,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        return search_with_gemini(f"Résumé exécutif : {text[:1000]}") or "Résumé exécutif indisponible"

def summarize_articles(articles, limit=None):
    summaries = defaultdict(list)
    for article in articles[:limit] if limit else articles:
        text = article.get("snippet", "")
        link = article.get("link", "")
        topic = article.get("keyword", "Autre")

        if not text.strip():
            summaries[topic].append(f"🔗 [Voir l'article]({link})\nRésumé indisponible")
            continue

        if not openai.api_key:
            summaries[topic].append(f"🔗 [Voir l'article]({link})\nRésumé indisponible (clé API manquante)")
            continue

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant de recherche stratégique."},
                    {"role": "user", "content": f"Voici un extrait : '{text[:1000]}'. Fais un résumé de 3 lignes."}
                ],
                temperature=0.5,
                max_tokens=150
            )
            summary = response.choices[0].message.content.strip()
            summaries[topic].append(f"🔗 [Voir l'article]({link})\n💬 {summary}")
        except Exception as e:
            traceback.print_exc()
            try:
                fallback = search_with_gemini(text[:1000])
                summaries[topic].append(f"🔗 [Voir l'article]({link})\n💬 {fallback}")
            except:
                summaries[topic].append(f"🔗 [Voir l'article]({link})\nRésumé indisponible (erreur API)")
    return summaries

# fetch_sources.py
import os
import requests
import feedparser
import google.generativeai as genai

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def search_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("models/chat-bison-001")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Erreur Gemini] {e}"

