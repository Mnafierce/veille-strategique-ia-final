import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")  ✅


def summarize_articles(articles):
    grouped = {}
    
    # Grouper les articles par mot-clé
    for article in articles:
        keyword = article['keyword']
        grouped.setdefault(keyword, []).append(f"- {article['title']}: {article['snippet']} ({article['link']})")

    summaries = {}

    for keyword, items in grouped.items():
        articles_text = "\n".join(items[:10])  # On limite à 10 articles pour le prompt

        prompt = f"""
Tu es un expert en veille stratégique. Résume les informations ci-dessous concernant le sujet suivant : "{keyword}".
Sois synthétique, structuré, professionnel et clair. Identifie les tendances, avancées ou faits saillants.

Articles :
{articles_text}
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un analyste d'intelligence d'affaires."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600
            )
            summaries[keyword] = response.choices[0].message['content']

        except Exception as e:
            summaries[keyword] = f"Erreur de résumé : {e}"

    return summaries


# Pour tester localement
if __name__ == "__main__":
    from fetch_news import run_news_crawl, KEYWORDS

    print("🔎 Lancement de la veille...")
    articles = run_news_crawl(KEYWORDS)
    print(f"\n{len(articles)} articles récupérés.")

    print("🧠 Résumé en cours...")
    résumés = summarize_articles(articles)

    for sujet, résumé in résumés.items():
        print(f"\n## {sujet}\n{résumé}")
