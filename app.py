import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import uuid
import re
from typing import List, Dict
import json
import os
import time
import sqlite3
try:
    from sklearn.linear_model import LogisticRegression
except ImportError:
    st.error("scikit-learn n'est pas installé. Veuillez ajouter 'scikit-learn==1.5.2' à requirements.txt.")
    LogisticRegression = None
import numpy as np
try:
    import plotly.express as px
except ImportError:
    st.error("plotly n'est pas installé. Veuillez ajouter 'plotly==5.20.0' à requirements.txt.")
    px = None
try:
    from deep_translator import GoogleTranslator
except ImportError:
    st.error("deep_translator n'est pas installé. Veuillez ajouter 'deep_translator==1.11.1' à requirements.txt.")
    GoogleTranslator = None
import feedparser
import schedule
import threading

# Configuration des mots-clés et profils de veille
CONFIG = {
    "sectors": {
        "Santé": ["santé", "médical", "diagnostic", "soins", "hôpital", "patient", "télémédecine"],
        "Économie": ["économie", "croissance", "PIB", "emploi", "inflation", "commerce"],
        "Finances": ["finance", "banque", "investissement", "fraude", "crypto", "marché", "blockchain"]
    },
    "subjects": {
        "Agents Agentiques": ["agentique", "IA autonome", "agent intelligent", "automatisation"],
        "IA": ["intelligence artificielle", "machine learning", "deep learning", "LLM"],
        "Technologie": ["technologie", "innovation", "numérique", "cloud", "cybersécurité"]
    },
    "countries": {
        "Québec": ["Québec", "Montréal", "Québec City", "francophone"],
        "Canada": ["Canada", "Toronto", "Vancouver", "Ottawa"],
        "Europe": ["Europe", "France", "Allemagne", "Royaume-Uni", "UE"],
        "États-Unis": ["États-Unis", "USA", "Californie", "New York"]
    },
    "profiles": {
        "Startups IA Québec": ["startup", "IA", "Québec", "innovation"],
        "Réglementations UE Santé": ["réglementation", "santé", "Europe", "GDPR"],
        "Tendances Finances USA": ["finance", "IA", "États-Unis", "marché"]
    }
}

# Initialisation SQLite
def init_db():
    try:
        conn = sqlite3.connect('veille_cache.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS results
                     (id TEXT, query TEXT, timestamp TEXT, title TEXT, url TEXT, source TEXT, date TEXT, abstract TEXT)''')
        conn.commit()
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation de la base de données : {e}")
    finally:
        conn.close()

init_db()

# Cache SQLite
def save_cache(data: List[Dict], query: str):
    try:
        conn = sqlite3.connect('veille_cache.db')
        c = conn.cursor()
        for item in data:
            c.execute('''INSERT INTO results (id, query, timestamp, title, url, source, date, abstract)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (str(uuid.uuid4()), query, datetime.now().isoformat(), item['title'], item['url'],
                       item['source'], item['date'], item.get('abstract', 'N/A')))
        conn.commit()
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du cache : {e}")
    finally:
        conn.close()

def load_cache(query: str, max_age_hours: int = 24) -> List[Dict]:
    try:
        conn = sqlite3.connect('veille_cache.db')
        c = conn.cursor()
        c.execute('''SELECT title, url, source, date, abstract FROM results
                     WHERE query = ? AND timestamp > ?''',
                  (query, (datetime.now() - timedelta(hours=max_age_hours)).isoformat()))
        results = [{"title": r[0], "url": r[1], "source": r[2], "date": r[3], "abstract": r[4]} for r in c.fetchall()]
        return results
    except Exception as e:
        st.error(f"Erreur lors du chargement du cache : {e}")
        return []
    finally:
        conn.close()

# Traduction et résumé avec deep_translator
def summarize_text(text: str, target_lang: str = 'en', max_length: int = 100) -> str:
    if GoogleTranslator is None:
        return text[:max_length] + "..." if len(text) > max_length else text
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        # Traduire et limiter la longueur
        translated = translator.translate(text)
        return translated[:max_length] + "..." if len(translated) > max_length else translated
    except Exception as e:
        st.error(f"Erreur de résumé avec deep_translator : {e}")
        return text[:max_length] + "..." if len(text) > max_length else text

# Scraping arXiv
def fetch_arxiv(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    for _ in range(3):  # Retry jusqu'à 3 fois
        try:
            query = query.replace(' ', '+')
            url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'xml', parser='lxml')
            entries = soup.find_all('entry')
            for entry in entries:
                title = entry.find('title').text.strip()
                link = entry.find('id').text.strip()
                date = entry.find('published').text.strip()[:10]
                abstract = entry.find('summary').text.strip()
                summarized_abstract = summarize_text(abstract, target_lang='en')
                studies.append({
                    'title': title,
                    'url': link,
                    'source': 'arXiv',
                    'date': date,
                    'abstract': abstract,
                    'summary': summarized_abstract
                })
            time.sleep(1)
            break
        except Exception as e:
            st.error(f"Erreur lors du scraping d'arXiv (tentative {_+1}/3) : {e}")
            time.sleep(2)
    return studies

# Scraping DOAJ
def fetch_doaj(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    for _ in range(3):
        try:
            query = query.replace(' ', '+')
            url = f"https://doaj.org/api/v1/search/articles/{query}?page=1&per_page={max_results}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get('results', [])[:max_results]:
                title = item.get('bibjson', {}).get('title', 'N/A')
                url = item.get('bibjson', {}).get('link', [{}])[0].get('url', '#')
                date = item.get('created_date', 'N/A')[:10]
                abstract = item.get('bibjson', {}).get('abstract', 'N/A')
                summarized_abstract = summarize_text(abstract, target_lang='en')
                studies.append({
                    'title': title,
                    'url': url,
                    'source': 'DOAJ',
                    'date': date,
                    'abstract': abstract,
                    'summary': summarized_abstract
                })
            time.sleep(1)
            break
        except Exception as e:
            st.error(f"Erreur lors de l'appel à DOAJ (tentative {_+1}/3) : {e}")
            time.sleep(2)
    return studies

# Scraping Google News via RSS
def fetch_google_news(query: str, max_results: int = 5) -> List[Dict]:
    articles = []
    for _ in range(3):
        try:
            query = query.replace(' ', '+')
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:max_results]:
                title = entry.get('title', 'N/A')
                url = entry.get('link', '#')
                date = entry.get('published', 'N/A')[:10]
                abstract = entry.get('description', 'N/A')
                summarized_abstract = summarize_text(abstract, target_lang='en')
                articles.append({
                    'title': title,
                    'url': url,
                    'source': 'Google News',
                    'date': date,
                    'abstract': abstract,
                    'summary': summarized_abstract
                })
            time.sleep(1)
            break
        except Exception as e:
            st.error(f"Erreur lors de la collecte des actualités Google News (tentative {_+1}/3) : {e}")
            time.sleep(2)
    return articles

# Prédiction des tendances
def predict_trend(data: List[Dict], sector: str, country: str) -> str:
    if LogisticRegression is None:
        return "Prédiction indisponible : scikit-learn non installé."
    try:
        X = np.array([len(item['abstract']) for item in data]).reshape(-1, 1)
        y = np.array([1 if 'agentique' in item['abstract'].lower() else 0 for item in data])
        if len(np.unique(y)) > 1:
            model = LogisticRegression().fit(X, y)
            score = model.predict_proba([[500]])[0][1]
            return f"Probabilité d'adoption des agents agentiques dans {sector} au {country} d'ici 2026 : {score:.2%}"
        return "Données insuffisantes pour la prédiction."
    except Exception as e:
        return f"Erreur lors de la prédiction : {e}"

# Détection des signaux faibles
def detect_weak_signals(data: List[Dict], sector: str, country: str) -> str:
    signals = [item['title'] for item in data if 'startup' in item['abstract'].lower() or 'emerging' in item['abstract'].lower()]
    return f"Signaux faibles ({sector}, {country}) : {', '.join(signals) if signals else 'Aucun signal détecté.'}"

# Analyse concurrentielle
def analyze_competitors(sector: str, subject: str) -> str:
    competitors = {
        "Santé": ["Microsoft (Azure Health)", "IBM (Watson Health)"],
        "Économie": ["Microsoft", "IBM"],
        "Finances": ["Microsoft (Copilot)", "IBM"]
    }
    return f"""
    **Analyse des concurrents** ({subject} dans {sector}):
    - {', '.join(competitors.get(sector, ['Aucun concurrent identifié']))}
    - Stratégies : Brevets en IA, partenariats avec startups.
    - Avantage Salesforce : CRM leader, agents agentiques intégrés.
    """

# Interface Streamlit
st.set_page_config(page_title="Veille Stratégique IA pour Salesforce", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #005FB8; color: white; }
    .stSelectbox, .stTextInput { background-color: #ffffff; border-radius: 5px; }
    h1 { color: #003087; font-family: 'Salesforce Sans', Arial, sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("Veille Stratégique IA pour Salesforce")
st.markdown("Suivez les avancées des agents agentiques externes en santé, économie et finances, avec des recommandations stratégiques.")

# Mode hors-ligne
try:
    requests.get("https://www.google.com", timeout=5)
    online = True
except:
    online = False
    st.warning("Mode hors-ligne : Affichage des résultats mis en cache.")

# Sélection des filtres
all_content = []
if online:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sector = st.selectbox("Secteur", list(CONFIG["sectors"].keys()))
    with col2:
        subject = st.selectbox("Sujet", list(CONFIG["subjects"].keys()))
    with col3:
        country = st.selectbox("Pays", list(CONFIG["countries"].keys()))
    with col4:
        profile = st.selectbox("Profil de veille", ["Aucun"] + list(CONFIG["profiles"].keys()))

    # Filtres dynamiques pour mots-clés
    custom_keywords = st.text_input("Mots-clés personnalisés (séparés par des virgules)", "")
    keywords = CONFIG["sectors"][sector] + CONFIG["subjects"][subject] + CONFIG["countries"][country]
    if profile != "Aucun":
        keywords += CONFIG["profiles"][profile]
    if custom_keywords:
        keywords += [k.strip() for k in custom_keywords.split(",")]

    query = f"{subject} {sector} {country} {' '.join(keywords)}"
    st.write(f"Requête : {query}")

    # Barre de recherche rapide
    quick_search = st.text_input("Recherche rapide", "")
    if quick_search:
        query = quick_search

    # Bouton pour lancer la recherche
    if st.button("Lancer la veille"):
        with st.spinner("Collecte des données..."):
            # Vérifier le cache
            all_content = load_cache(query)
            if not all_content:
                articles = fetch_google_news(query)
                studies_arxiv = fetch_arxiv(query)
                studies_doaj = fetch_doaj(query)
                all_content = articles + studies_arxiv + studies_doaj
                save_cache(all_content, query)

            if not all_content:
                st.warning("Aucun résultat trouvé.")
            else:
                # Onglets pour organiser les résultats
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Articles", "Études", "Analyse Concurrentielle", "Recommandations", "Visualisations"])

                with tab1:
                    st.subheader("Articles")
                    sort_by = st.selectbox("Trier par", ["Date", "Source", "Pertinence"], key="sort_articles")
                    for item in sorted([x for x in all_content if x['source'] == 'Google News'],
                                     key=lambda x: x['date'] if sort_by == "Date" else x['source']):
                        with st.expander(f"{item['title']}"):
                            st.write(f"**URL** : {item['url']}")
                            st.write(f"**Date** : {item['date']}")
                            st.write(f"**Abstract** : {item['abstract']}")
                            st.write(f"**Résumé** : {item['summary']}")

                with tab2:
                    st.subheader("Études")
                    sort_by = st.selectbox("Trier par", ["Date", "Source", "Pertinence"], key="sort_studies")
                    for item in sorted([x for x in all_content if x['source'] in ['arXiv', 'DOAJ']],
                                     key=lambda x: x['date'] if sort_by == "Date" else x['source']):
                        with st.expander(f"{item['title']}"):
                            st.write(f"**URL** : {item['url']}")
                            st.write(f"**Date** : {item['date']}")
                            st.write(f"**Abstract** : {item['abstract']}")
                            st.write(f"**Résumé** : {item['summary']}")

                with tab3:
                    st.subheader("Analyse Concurrentielle")
                    st.markdown(analyze_competitors(sector, subject))

                with tab4:
                    st.subheader("Recommandations pour Salesforce")
                    st.markdown(f"""
                    **Recommandations stratégiques** ({subject}, {sector}, {country}):
                    1. Développer un agent agentique spécialisé pour {sector}.
                    2. Partenariats avec startups IA au {country}.
                    3. Intégrer des balises éthiques pour {sector}.
                    4. Personnaliser les agents pour les clients {sector}.
                    """)
                    st.subheader("Prédictions")
                    st.write(predict_trend(all_content, sector, country))
                    st.subheader("Signaux faibles")
                    st.write(detect_weak_signals(all_content, sector, country))

                with tab5:
                    st.subheader("Visualisations")
                    if px is not None:
                        df_viz = pd.DataFrame([x['source'] for x in all_content], columns=['Source'])
                        fig = px.histogram(df_viz, x='Source', title='Répartition des sources')
                        st.plotly_chart(fig)
                    else:
                        st.error("Visualisations indisponibles : plotly non installé.")

                # Alerte pour nouveaux résultats
                if len(all_content) > len(load_cache(query, max_age_hours=1)):
                    st.success("Nouveaux résultats détectés !")

# Exportation des résultats
if st.button("Exporter les résultats") and all_content:
    results = {
        "title": [], "url": [], "source": [], "date": [], "abstract": [], "summary": []
    }
    for item in all_content:
        results["title"].append(item["title"])
        results["url"].append(item["url"])
        results["source"].append(item["source"])
        results["date"].append(item["date"])
        results["abstract"].append(item["abstract"])
        results["summary"].append(item["summary"])
    
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)
    st.download_button("Télécharger CSV", csv, "veille_strategique.csv", "text/csv")

# Tâches planifiées
def run_scheduled_veille():
    query = "Agents Agentiques Santé Québec"
    all_content = fetch_google_news(query) + fetch_arxiv(query) + fetch_doaj(query)
    save_cache(all_content, query)
    st.success("Mise à jour quotidienne effectuée.")

schedule.every().day.at("02:00").do(run_scheduled_veille)

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=schedule_loop, daemon=True).start()
