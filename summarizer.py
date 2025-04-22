import os
import openai
from collections import defaultdict

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_articles(articles):
    summaries = defaultdict(str)

    for article in articles:
        topic = article["keyword"]
        content = f"Titre: {article['title']}\nExtrait: {article['snippet']}\nLien: {article['link']}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en veille technologique. Résume les informations de manière concise, en extrayant les insights les plus pertinents pour un décideur."},
                    {"role": "user", "content": content}
                ],
                temperature=0.4,
                max_tokens=300
            )

            summary = response.choices[0].message.content
            summaries[topic] += f"- {summary}\n\n"

        except Exception as e:
            summaries[topic] += f"- Erreur lors du résumé : {str(e)}\n\n"

    return summaries

