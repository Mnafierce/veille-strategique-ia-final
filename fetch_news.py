import urllib.parse
import requests
from bs4 import BeautifulSoup
from fetch_sources import (
    search_with_gemini,
    search_with_serpapi,
    search_with_google_cse
)
from summarizer import always_use_keywords

# Mots-clés innovation à utiliser pour la génération d'idées
INNOVATION_KEYWORDS = [
    "AI startup funding", "AI for operations", "enterprise automation trends",
    "predictive analytics in business", "intelligent agents in finance",
    "AI-powered decision-making", "AI trends in business strategy",
    "generative AI in enterprise", "AI and customer engagement", "future of automation"
]

# Mots-clés spécifiques à chaque secteur
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

# Recherche via Google News (scraping léger)
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

# Fonction principale d’agrégation

def run_news_crawl(
    keywords,
    use_google_news=True,
    use_serpapi=True,
    use_cse=True,
    use_gemini=True
):
    all_results = []

    # Ajouter les mots-clés toujours utilisés
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
