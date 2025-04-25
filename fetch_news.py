import urllib.parse
import requests
from bs4 import BeautifulSoup
from fetch_sources import (
    search_with_gemini,
    search_with_serpapi,
    search_with_google_cse
)

# ✅ Mots-clés permanents en IA & technologie (toujours inclus)
DEFAULT_TECH_KEYWORDS = [
    "Artificial Intelligence", "AI Trends", "Machine Learning", "Agentic AI",
    "LLMs", "Generative AI", "AI Regulation", "Technological Innovation",
    "AI in Finance", "AI in Healthcare", "Digital Transformation",
    "AI Agents", "Autonomous Agents", "Agent d’IA", "AI Startups"
]

# Liste des mots-clés à surveiller dynamiquement + fixes
KEYWORDS = list(set(DEFAULT_TECH_KEYWORDS))

# Recherche Google News simple (scraping)
def search_google_news(keyword):
    encoded_keyword = urllib.parse.quote_plus(keyword)
    url = f"https://www.google.com/search?q={encoded_keyword}&tbm=nws"
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

# Fonction centrale
def run_news_crawl(
    keywords,
    use_google_news=True,
    use_serpapi=True,
    use_cse=True,
    use_gemini=True
):
    all_results = []
    all_keywords = list(set(keywords + DEFAULT_TECH_KEYWORDS))

    for keyword in all_keywords:
        print(f"\n🔍 Recherche pour : {keyword}")

        if use_google_news:
            try:
                google_news_results = search_google_news(keyword)
                all_results.extend(google_news_results)
            except Exception as e:
                print(f"[Google News Error] {e}")

        if use_serpapi:
            try:
                serp_results = search_with_serpapi(keyword)
                all_results.extend(serp_results)
            except Exception as e:
                print(f"[SerpAPI Error] {e}")

        if use_cse:
            try:
                cse_results = search_with_google_cse(keyword)
                all_results.extend(cse_results)
            except Exception as e:
                print(f"[Google CSE Error] {e}")

        if use_gemini:
            try:
                gemini_snippet = search_with_gemini(
                    f"Fais une veille stratégique sur : {keyword}. Résume les nouvelles tendances technologiques, les concurrents émergents, les besoins du marché, et les usages des agents IA."
                )
                all_results.append({
                    "keyword": keyword,
                    "title": "Résumé généré par Gemini",
                    "link": "https://makersuite.google.com/",
                    "snippet": gemini_snippet
                })
            except Exception as e:
                print(f"[Gemini Error] {e}")

    return all_results

# Test local
if __name__ == "__main__":
    results = run_news_crawl(KEYWORDS)
    for r in results:
        print(f"[{r['keyword']}] {r['title']} - {r['link']}")
