import os
import openai
from collections import defaultdict

# ✅ Ajout pour lire la clé depuis l'env
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
                {"role": "user", "content": text[:3000]}
            ],
            temperature=0.4,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except:
        return "Résumé exécutif indisponible"

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
                    {"role": "user", "content": f"Voici un extrait : '{text}'. Fais un résumé de 3 lignes."}
                ],
                temperature=0.5,
                max_tokens=200
            )
            summary = response.choices[0].message.content.strip()
            summaries[topic].append(f"🔗 [Voir l'article]({link})\n💬 {summary}")
        except:
            summaries[topic].append(f"🔗 [Voir l'article]({link})\nRésumé indisponible (erreur API)")
    return summaries

def generate_swot_analysis(text):
    if not text.strip() or not openai.api_key:
        return "Analyse SWOT indisponible"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un analyste stratégique spécialisé en SWOT."},
                {"role": "user", "content": f"Fais une analyse SWOT basée sur ce texte : {text[:3500]}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except:
        return "Analyse SWOT indisponible"

def generate_innovation_ideas(text):
    if not text.strip() or not openai.api_key:
        return ["[Erreur génération idées]"]
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un stratège de l'innovation."},
                {"role": "user", "content": f"Génère 5 idées d'application innovantes de l'IA basées sur : {text[:3500]}"}
            ],
            temperature=0.6,
            max_tokens=300
        )
        return response.choices[0].message.content.strip().split("\n")
    except:
        return ["[Erreur génération idées]"]

def generate_strategic_recommendations(text, mode="general"):
    if not text.strip() or not openai.api_key:
        return ["[Erreur génération recommandations]"]
    try:
        prompt = f"Donne des recommandations stratégiques{' pour Salesforce' if mode=='salesforce' else ''} à partir du texte suivant : {text[:3500]}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un consultant en stratégie IA."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content.strip().split("\n")
    except:
        return ["[Erreur génération recommandations]"]

def compute_strategic_score(text):
    try:
        keywords = INNOVATION_KEYWORDS + always_use_keywords
        text_lower = text.lower()
        hits = sum(1 for k in keywords if k.lower() in text_lower)
        score = int((hits / len(keywords)) * 100)
        return min(score, 100)
    except:
        return 0
