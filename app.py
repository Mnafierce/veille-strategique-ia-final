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

# Configuration des mots-clés par secteur, sujet et pays
CONFIG = {
    "sectors": {
        "Santé": ["santé", "médical", "diagnostic", "soins", "hôpital", "patient"],
        "Économie": ["économie", "croissance", "PIB", "emploi", "inflation", "commerce"],
        "Finances": ["finance", "banque", "investissement", "fraude", "crypto", "marché"]
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
    }
}

# Fonction pour sauvegarder les résultats en cache
def save_cache(data: List[Dict], filename: str = 'cache.json'):
    try:
        with open(filename, 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': data}, f)
    except Exception as e:
        st.warning(f"Erreur lors de la sauvegarde du cache : {e}")

# Fonction pour charger les résultats depuis le cache
def load_cache(filename: str = 'cache.json', max_age_hours: int = 24) -> List[Dict]:
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                cache = json.load(f)
                timestamp = datetime.fromisoformat(cache['timestamp'])
                if datetime.now() - timestamp < timedelta(hours=max_age_hours):
                    return cache['data']
    except Exception as e:
        st.warning(f"Erreur lors du chargement du cache : {e}")
    return []

# Fonction pour collecter des articles via Google News
def fetch_articles(query: str, max_results: int = 5) -> List[Dict]:
    articles = []
    try:
        url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.find_all('article')[:max_results]:
            title = item.find('h3')
            link = item.find('a')['href'] if item.find('a') else None
            if title and link:
                articles.append({
                    "title": title.text,
                    "url": f"https://news.google.com{link}",
                    "source": "Google News",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "abstract": "N/A"
                })
        time.sleep(1)  # Pause pour éviter de surcharger
    except Exception as e:
        st.error(f"Erreur lors de la collecte des articles : {e}")
    return articles

# Fonction pour scraper Semantic Scholar
def fetch_studies_semantic_scholar(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    try:
        query = query.replace(' ', '+')
        url = f"https://www.semanticscholar.org/search?q={query}&sort=relevance"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='cl-paper-row')[:max_results]

        for result in results:
            title_tag = result.find('h2', class_='cl-paper-title')
            link_tag = result.find('a', class_='cl-paper-title')
            date_tag = result.find('span', class_='cl-paper-pubdate')

            title = title_tag.text.strip() if title_tag else 'N/A'
            url = f"https://www.semanticscholar.org{link_tag['href']}" if link_tag else '#'
            date = date_tag.text.strip() if date_tag else 'N/A'

            # Essayer d'extraire l'abstract
            abstract = 'N/A'
            if url != '#':
                try:
                    paper_response = requests.get(url, headers=headers)
                    paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
                    abstract_tag = paper_soup.find('div', class_='cl-paper-abstract')
                    abstract = abstract_tag.text.strip() if abstract_tag else 'N/A'
                    time.sleep(1)  # Pause pour éviter de surcharger
                except:
                    pass

            studies.append({
                'title': title,
                'url': url,
                'source': 'Semantic Scholar',
                'date': date,
                'abstract': abstract
            })
    except Exception as e:
        st.error(f"Erreur lors du scraping de Semantic Scholar : {e}")
    return studies

# Fonction pour scraper Google Scholar (backup)
def fetch_studies_google_scholar(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    try:
        query = query.replace(' ', '+')
        url = f"https://scholar.google.com/scholar?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='gs_r gs_or gs_scl')[:max_results]

        for result in results:
            title_tag = result.find('h3', class_='gs_rt')
            link_tag = title_tag.find('a') if title_tag else None
            date_tag = result.find('div', class_='gs_a')

            title = title_tag.text.strip() if title_tag else 'N/A'
            url = link_tag['href'] if link_tag else '#'
            date = date_tag.text.strip() if date_tag else 'N/A'
            abstract = 'N/A'  # Google Scholar ne fournit pas d'abstract directement

            studies.append({
                'title': title,
                'url': url,
                'source': 'Google Scholar',
                'date': date,
                'abstract': abstract
            })
        time.sleep(1)  # Pause pour éviter de surcharger
    except Exception as e:
        st.error(f"Erreur lors du scraping de Google Scholar : {e}")
    return studies

# Fonction principale pour collecter les études
def fetch_studies(query: str, max_results: int = 3) -> List[Dict]:
    # Vérifier le cache
    cache_key = f"studies_{query}_{max_results}"
    cached_results = load_cache(f"{cache_key}.json")
    if cached_results:
        return cached_results

    # Essayer Semantic Scholar
    studies = fetch_studies_semantic_scholar(query, max_results)
    if not studies:
        st.warning("Échec du scraping de Semantic Scholar. Passage à Google Scholar...")
        studies = fetch_studies_google_scholar(query, max_results)

    # Sauvegarder dans le cache
    if studies:
        save_cache(studies, f"{cache_key}.json")
    return studies

# Fonction pour générer un résumé exécutif
def generate_executive_summary(content: Dict, sector: str, subject: str, country: str) -> str:
    abstract = content.get('abstract', 'N/A')
    summary = f"""
    **Résumé exécutif** pour "{content['title']}" ({content['source']}, {content['date']}):
    Cet article/étude explore les avancées en {subject} dans le secteur {sector} au {country}. 
    Points clés : {abstract if abstract != 'N/A' else '[Simulé - Intégrer IA pour analyse réelle]'}.
    - Impact potentiel : Automatisation accrue, efficacité opérationnelle.
    - Applications : [À personnaliser selon contenu].
    - Pertinence pour Salesforce : Intégration possible dans les solutions CRM pour {sector}.
    """
    return summary

# Fonction pour analyser les concurrents
def analyze_competitors(sector: str, subject: str) -> str:
    competitors = {
        "Santé": ["IBM (Watson Health)", "Microsoft (Azure Health)", "Google Health"],
        "Économie": ["SAP", "Oracle", "Microsoft"],
        "Finances": ["IBM", "Microsoft (Copilot)", "OpenAI"]
    }
    return f"""
    **Analyse des concurrents** ({subject} dans {sector}):
    - {', '.join(competitors.get(sector, ['Aucun concurrent identifié']))}
    - Observations : [Simulé - Intégrer IA pour analyse détaillée].
    - Avantage Salesforce : Plateforme CRM leader, potentiel pour agents agentiques intégrés.
    """

# Fonction pour générer des recommandations stratégiques
def generate_strategic_recommendations(sector: str, subject: str, country: str) -> str:
    return f"""
    **Recommandations stratégiques pour Salesforce** ({subject}, {sector}, {country}):
    1. **Développer un agent agentique spécialisé** : Créer un agent IA autonome intégré à Salesforce CRM, capable d'automatiser des tâches complexes (ex. : détection de fraude en finance, diagnostics en santé).
    2. **Partenariats locaux** : Collaborer avec des startups IA au {country} (ex. : Element AI au Québec, DeepMind en Europe).
    3. **Focus sur l'éthique** : Intégrer des balises éthiques pour renforcer la confiance des clients dans {sector}.
    4. **Personnalisation** : Adapter les agents aux besoins spécifiques des clients {sector} (ex. : prévisions financières, gestion hospitalière).
    """

# Interface Streamlit
st.title("Veille Stratégique IA pour Salesforce")
st.markdown("Suivez les avancées des agents agentiques externes en santé, économie et finances, avec des recommandations stratégiques.")

# Sélection des filtres
col1, col2, col3 = st.columns(3)
with col1:
    sector = st.selectbox("Secteur", list(CONFIG["sectors"].keys()))
with col2:
    subject = st.selectbox("Sujet", list(CONFIG["subjects"].keys()))
with col3:
    country = st.selectbox("Pays", list(CONFIG["countries"].keys()))

# Construction de la requête avec mots-clés
keywords = CONFIG["sectors"][sector] + CONFIG["subjects"][subject] + CONFIG["countries"][country]
query = f"{subject} {sector} {country} {' '.join(keywords)}"
st.write(f"Requête : {query}")

# Bouton pour lancer la recherche
if st.button("Lancer la veille"):
    with st.spinner("Collecte des données..."):
        # Collecte des articles et études
        articles = fetch_articles(query)
        studies = fetch_studies(query)
        all_content = articles + studies

        if not all_content:
            st.warning("Aucun résultat trouvé. Essayez une autre combinaison.")
        else:
            # Sauvegarder tous les résultats dans le cache
            save_cache(all_content, 'all_results.json')

            # Affichage des résultats
            st.subheader("Résultats de la veille")
            for item in all_content:
                with st.expander(f"{item['title']} ({item['source']})"):
                    st.write(f"**URL** : {item['url']}")
                    st.write(f"**Date** : {item['date']}")
                    st.write(f"**Abstract** : {item['abstract']}")
                    st.markdown(generate_executive_summary(item, sector, subject, country))

            # Analyse des concurrents
            st.subheader("Analyse des concurrents")
            st.markdown(analyze_competitors(sector, subject))

            # Recommandations stratégiques
            st.subheader("Recommandations pour Salesforce")
            st.markdown(generate_strategic_recommendations(sector, subject, country))

            # Résumé général
            st.subheader("Résumé général")
            st.markdown(f"""
            **Synthèse** : La recherche sur {subject} dans {sector} au {country} montre un potentiel élevé pour les agents agentiques. Les tendances incluent l'automatisation accrue et l'intégration d'IA éthique. Salesforce peut se positionner comme leader en intégrant des agents autonomes dans ses solutions CRM.
            **Prochaines étapes** : Investir dans le développement d'agents spécialisés, établir des partenariats locaux, et prioriser l'éthique et la personnalisation.
            """)

# Exportation des résultats
if st.button("Exporter les résultats"):
    results = {
        "title": [],
        "url": [],
        "source": [],
        "date": [],
        "abstract": [],
        "summary": []
    }
    for item in all_content:
        results["title"].append(item["title"])
        results["url"].append(item["url"])
        results["source"].append(item["source"])
        results["date"].append(item["date"])
        results["abstract"].append(item["abstract"])
        results["summary"].append(generate_executive_summary(item, sector, subject, country))
    
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)
    st.download_button("Télécharger CSV", csv, "veille_strategique.csv", "text/csv")
