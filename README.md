📊 Veille Stratégique – Agents IA en Finance & Santé
Cette application Streamlit génère automatiquement une veille quotidienne sur les avancées en intelligence artificielle, notamment les agents autonomes (AI agents), dans les secteurs de la santé, de la finance et de l'économie.

🚀 Fonctionnalités
Collecte automatisée d'actualités via :

Google News

SerpAPI

Google Programmable Search

Google Gemini (IA générative)

Résumés intelligents avec OpenAI

Téléchargement du rapport en DOCX

Interface web simple et professionnelle

🧰 Technologies utilisées
Python, Streamlit

OpenAI, Gemini, SerpAPI, Google CSE

BeautifulSoup, Requests, python-docx

🔐 Configuration des clés (via Streamlit Cloud)
Ajoute les clés dans Settings > Secrets :

toml
Copier
Modifier
OPENAI_API_KEY = "..."
GEMINI_API_KEY = "..."
SERPAPI_KEY = "..."
GOOGLE_CSE_ID = "..."
📦 Installation locale (optionnelle)
bash
Copier
Modifier
pip install -r requirements.txt
streamlit run app.py
