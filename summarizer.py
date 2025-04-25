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
                {"role": "system", "content": "Tu es un expert en veille technologique. Résume de manière claire et concise pour un décideur."},
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
    """Résumé global des derniers 24h à partir de plusieurs extraits"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un analyste stratégique. Résume les événements clés des dernières 24h à partir de ce texte brut."},
                {"role": "user", "content": text}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Erreur OpenAI Résumé 24h] {str(e)}"

def generate_strategic_recommendations(summaries_by_topic):
    """Génère 5 recommandations stratégiques basées sur les résumés."""
    try:
        content = "\n".join([f"{k}: {v}" for k, v in summaries_by_topic.items()])
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en stratégie d'affaires et intelligence de marché. En te basant sur ces résumés de veille, propose 5 recommandations concrètes pour une entreprise technologique."
                },
                {"role": "user", "content": content}
            ],
            temperature=0.5,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erreur lors de la génération des recommandations stratégiques : {str(e)}"


