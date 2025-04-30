# 📊 Veille Stratégique IA

## ✨ Objectif
Cette application automatise la veille technologique et stratégique sur les agents IA ("agentic AI") dans des domaines clés : Finance, Santé, et tendances émergentes. Elle collecte, résume et classe des articles pertinents via une interface Streamlit conviviale.

## ⚡ Fonctionnalités principales
- Recherche asynchrone sur : Perplexity, Google CSE, ArXiv, Consensus
- Résumés automatiques via OpenAI / fallback Gemini
- Analyse SWOT automatisée
- Timeline interactive des évolutions thématiques
- Export DOCX du rapport consolidé
- Mode Salesforce : recommandations stratégiques ciblées

## 🚀 Lancement rapide
```bash
# Créer l'environnement
python -m venv venv
source venv/bin/activate  # Ou .\venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Définir les clés API (dans .env ou variables d'environnement)
# Exemple :
export OPENAI_API_KEY="sk-..."
export SERPAPI_KEY="..."
export PERPLEXITY_API_KEY="..."
export GOOGLE_CSE_ID="..."
export GEMINI_API_KEY="..."

# Lancer l'application
streamlit run app.py
```

## 🌐 Sources utilisées
- [Perplexity AI](https://www.perplexity.ai/)
- [Google CSE / News](https://programmablesearchengine.google.com/)
- [ArXiv API](https://arxiv.org/help/api/index)
- [Consensus via SerpAPI](https://serpapi.com)
- [OpenAI GPT-3.5 Turbo](https://platform.openai.com)
- [Gemini Generative AI (Google)](https://makersuite.google.com/app)

## 🏑 Modules importants
- `app.py` : logiques UI Streamlit
- `async_sources.py` : appels API parallélisés
- `summarizer.py` : résumés + SWOT + recommandations
- `fetch_sources.py` : fallback Gemini, recherche simple
- `fetch_news.py` : Google News RSS
- `report_builder.py` : export DOCX

## ⚙ Idées d'évolution
- Intégration vecteur / base RAG (e.g. via Qdrant)
- Analyse comparative concurrentielle sur les agents
- Dashboard PowerBI ou Dash en mode export
- Intégration API HuggingFace Trends

---

Réalisé pour renforcer la stratégie IA de Salesforce, ce projet constitue un socle solide pour l'analyse proactive de l'écosystème agentique.




### 1. Installation des dépendances

```bash
pip install -r requirements.txt
