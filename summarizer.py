import os
from collections import defaultdict
from openai import OpenAI

# Initialiser OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    except Exception:
        return "Résumé indisponible"

def summarize_articles(articles, limit=None):
    summaries = defaultdict(str)
    topics = set([a["keyword"] for a in articles])

    for topic in topics:
        topic_articles = [a for a in articles if a["keyword"] == topic]
        if limit:
            topic_articles = topic_articles[:limit]

        for article in topic_articles:
            content = f"Titre: {article['title']}\nExtrait: {article['snippet']}\nLien: {article['link']}"
            summary = summarize_with_openai(content)
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
        return "Résumé exécutif indisponible"

def generate_swot_analysis(text_block):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un consultant stratégique. Analyse le texte et propose une grille SWOT pour l’entreprise Salesforce sur les agents agentiques IA."},
                {"role": "user", "content": text_block}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception:
        return "Analyse SWOT indisponible"

def compute_strategic_score(snippet, keywords):
    return sum(1 for kw in keywords if kw.lower() in snippet.lower())

always_use_keywords = [
    "intelligence artificielle", "agents intelligents", "agentic AI", "rupture technologique",
    "machine learning", "technologie émergente", "IA générative", "recherche en IA",
    "automatisation intelligente", "innovation algorithmique", "GPT-4", "LLM"
]

INNOVATION_KEYWORDS = [
    "AI startup funding", "AI for operations", "enterprise automation trends",
    "predictive analytics in business", "intelligent agents in finance",
    "AI-powered decision-making", "AI trends in business strategy",
    "generative AI in enterprise", "AI and customer engagement", "future of automation"
]

def generate_innovation_ideas(text_block):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un générateur d’idées d’innovation pour les grandes entreprises tech."},
                {"role": "user", "content": f"À partir de ce contenu :\n{text_block}\nPropose 5 idées innovantes utilisables par Salesforce dans le domaine des agents IA autonomes."}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.split("\n")
    except Exception:
        return ["[Erreur génération idées]"]

def generate_strategic_recommendations(text_block, mode="default"):
    prompt = f"Tu es un expert en stratégie IA. Donne 5 recommandations pour {mode} à partir du contenu suivant :\n{text_block}"
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Fournis des recommandations pratiques et stratégiques."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=400
        )
        return response.choices[0].message.content.split("\n")
    except Exception:
        return ["[Erreur génération recommandations]"]

    except Exception:
        return ["[Erreur génération recommandations]"]
