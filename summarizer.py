import os
from collections import defaultdict
from openai import OpenAI
import google.generativeai as genai

# Initialiser OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configurer Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-pro")


def summarize_with_openai(content):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en veille technologique. Résume les informations de manière concise, en extrayant les insights les plus pertinents pour un décideur."},
                {"role": "user", "content": content}
            ],
            temperature=0.4,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Erreur OpenAI] {str(e)}"


def summarize_with_gemini(content):
    try:
        response = gemini_model.generate_content(content)
        return response.text
    except Exception as e:
        return f"[Erreur Gemini] {str(e)}"


def summarize_articles(articles, limit=None, use_gemini=False):
    summaries = defaultdict(str)
    topics = set([a["keyword"] for a in articles])

    for topic in topics:
        topic_articles = [a for a in articles if a["keyword"] == topic]
        if limit:
            topic_articles = topic_articles[:limit]

        for article in topic_articles:
            content = f"Titre: {article['title']}\nExtrait: {article['snippet']}\nLien: {article['link']}"
            summary = summarize_with_gemini(content) if use_gemini else summarize_with_openai(content)
            summaries[topic] += f"- {summary}\n\n"

    return summaries


def summarize_text_block(text):
    """Résumé global à partir d'un bloc de texte (pour la section 24h)"""
    return summarize_with_openai(
        f"Résume les tendances principales dans ce contenu extrait des 24 dernières heures :\n{text}"
    )
