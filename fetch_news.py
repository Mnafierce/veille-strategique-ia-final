import urllib.parse
import requests
from bs4 import BeautifulSoup
from fetch_sources import (
    search_with_gemini,
    search_with_serpapi,
    search_with_google_cse
)
from summarizer import always_use_keywords

# 🧠 Mots-clés stratégiques de base (toujours inclus)
INNOVATION_KEYWORDS = [
    "AI startup funding", "AI for operations", "enterprise automation trends",
    "predictive analytics in business", "intelligent agents in finance",
    "AI-powered decision-making", "AI trends in business strategy",
    "generative AI in enterprise", "AI and customer engagement", "future of automation"
]

SECTOR_KEYWORDS = {
    "Finance": [
        "AI in banking", "Fintech AI", "robo-advisor", "RegTech", "Fraud detection AI",
        "credit scoring AI", "automated underwriting", "Finley AI", "Interface.ai", "agentic AI in finance"
    ],
    "Santé": [
        "AI in healthcare", "Hippocratic AI", "ONE AI Health", "medical diagnostics AI",
        "clinical decision support", "health data automation", "agentic AI in health"
    ]
}


def search_google_news(keyword):
    encoded = urllib.parse.quote_plus(keyword)
    url = f"https://www.google.com/search?q={encoded}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return [{"keyword": keyword, "title": "Erreur Google News", "link": "", "snippet": str(e)}]

    results = []
    for result in soup.find_all('div', class_='dbsr'):
        title = result.find('div', class_='JheGif nDgy9d')
        link = result.find('a')['href']
        snippet = result.find('div', class_='Y3v8qd')

        results.append({
            "keyword": keyword,
            "title": title.text.strip() if title else "Sans titre",
            "link": link.strip(),
            "snippet": snippet.text.strip() if snippet else "Sans description"
        })

    return results


def run_news_crawl(
    keywords,
    use_google_news=True,
    use_serpapi=True,
    use_cse=True,
    use_gemini=True
):
    all_results = []

    # Inclure les mots-clés permanents
    search_keywords = list(set(keywords + always_use_keywords))

    for keyword in search_keywords:
        print(f"\n🔍 Recherche pour : {keyword}")

        if use_google_news:
            try:
                all_results.extend(search_google_news(keyword))
            except Exception as e:
                print(f"[Google News Error] {e}")

        if use_serpapi:
            try:
                all_results.extend(search_with_serpapi(keyword))
            except Exception as e:
                print(f"[SerpAPI Error] {e}")

        if use_cse:
            try:
                all_results.extend(search_with_google_cse(keyword))
            except Exception as e:
                print(f"[Google CSE Error] {e}")

        if use_gemini:
            try:
                snippet = search_with_gemini(
                    f"Effectue une veille stratégique sur : {keyword}. Résume les avancées, tendances, concurrents émergents et besoins du marché."
                )
                all_results.append({
                    "keyword": keyword,
                    "title": "Résumé généré par Gemini",
                    "link": "https://makersuite.google.com/",
                    "snippet": snippet
                })
            except Exception as e:
                print(f"[Gemini Error] {e}")

    return all_results

# ideas.py : Module pour génération d'idées innovantes

import os
from openai import OpenAI
import google.generativeai as genai
from summarizer import INNOVATION_KEYWORDS

# Initialiser OpenAI et Gemini
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-pro")

def generate_innovation_ideas():
    try:
        joined_keywords = ", ".join(INNOVATION_KEYWORDS)
        prompt = f"""
        Génère 5 idées d'innovation concrètes pour les entreprises en utilisant les dernières tendances dans :
        {joined_keywords}.
        Donne des idées claires, concrètes, applicables et pertinentes.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un stratège en innovation d'entreprise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content

    except Exception as e:
        print("[OpenAI Error - fallback Gemini]", e)
        try:
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e2:
            return f"[Erreur à toutes les sources] {e2}"

# Pour test local
if __name__ == "__main__":
    print(generate_innovation_ideas())

