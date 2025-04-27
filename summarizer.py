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
        return None  # on gère l'erreur ailleurs


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

            summary = summarize_with_openai(content)
            if summary is None:  # fallback si quota OpenAI dépassé
                summary = summarize_with_gemini(content)

            summaries[topic] += f"- {summary}\n\n"

    return summaries


def summarize_text_block(text):
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
    except Exception:
        return summarize_with_gemini(f"Résume les grandes tendances de ces extraits d'actualités :\n{text}")


# Mots-clés permanents intégrés à toutes les recherches
always_use_keywords = [
    "intelligence artificielle", "agents intelligents", "agentic AI", "rupture technologique",
    "machine learning", "technologie émergente", "IA générative", "recherche en IA",
    "automatisation intelligente", "innovation algorithmique", "GPT-4", "LLM"
]

# Mots-clés pour idées innovantes
INNOVATION_KEYWORDS = [
    "AI startup funding", "AI for operations", "enterprise automation trends",
    "predictive analytics in business", "intelligent agents in finance",
    "AI-powered decision-making", "AI trends in business strategy",
    "generative AI in enterprise", "AI and customer engagement", "future of automation"
]
