import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import List, Dict

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

# Fonction pour collecter des articles via Google News (ou autre API)
def fetch_articles(query: str, max_results: int = 5) -> List[Dict]:
    articles = []
    try:
        # Exemple avec Google News (remplacer par une API réelle)
        url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.find_all('article')[:max_results]:
            title = item.find('h3')
            link = item.find('a')['href'] if item.find('a') else None
            if title and link:
                articles.append({
                    "title": title.text,
                    "url": f"https://news.google.com{link}",
                    "source": "Google News",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
    except Exception as e:
        st.error(f"Erreur lors de la collecte des articles : {e}")
    return articles

# Fonction pour collecter des études via Semantic Scholar
from bs4 import BeautifulSoup
import requests
from typing import List, Dict

def fetch_studies(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    try:
        # Formatter la requête pour l'URL de recherche
        query = query.replace(' ', '+')
        url = f"https://www.semanticscholar.org/search?q={query}&sort=relevance"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='cl-paper-row')[:max_results]

        for result in results:
            title_tag = result.find('h2', class_='cl-paper-title')
            link_tag = result.find('a', class_='cl-paper-title')
            date_tag = result.find('span', class_='cl-paper-pubdate')

            title = title_tag.text.strip() if title_tag else 'N/A'
            url = f"https://www.semanticscholar.org{link_tag['href']}" if link_tag else '#'
            date = date_tag.text.strip() if date_tag else 'N/A'

            studies.append({
                'title': title,
                'url': url,
                'source': 'Semantic Scholar',
                'date': date
            })

    except Exception as e:
        st.error(f"Erreur lors du scraping de Semantic Scholar : {e}")
    return studies

# Fonction pour générer un résumé exécutif (simulé, à remplacer par Grok ou autre IA)
def generate_executive_summary(content: Dict, sector: str, subject: str, country: str) -> str:
    return f"""
    **Résumé exécutif** pour "{content['title']}" ({content['source']}, {content['date']}):
    Cet article/étude explore les avancées en {subject} dans le secteur {sector} au {country}. 
    Points clés : [Simulé - Intégrer IA pour analyse réelle].
    - Impact potentiel : Automatisation accrue, efficacité opérationnelle.
    - Applications : [À personnaliser selon contenu].
    - Pertinence pour Salesforce : Intégration possible dans les solutions CRM pour {sector}.
    """

# Fonction pour analyser les concurrents (simulé)
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

# Fonction pour générer des recommandations stratégiques pour Salesforce
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
            # Affichage des résultats
            st.subheader("Résultats de la veille")
            for item in all_content:
                with st.expander(f"{item['title']} ({item['source']})"):
                    st.write(f"**URL** : {item['url']}")
                    st.write(f"**Date** : {item['date']}")
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
        "summary": []
    }
    for item in all_content:
        results["title"].append(item["title"])
        results["url"].append(item["url"])
        results["source"].append(item["source"])
        results["date"].append(item["date"])
        results["summary"].append(generate_executive_summary(item, sector, subject, country))
    
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)
    st.download_button("Télécharger CSV", csv, "veille_strategique.csv", "text/csv")
