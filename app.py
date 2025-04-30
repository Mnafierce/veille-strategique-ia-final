import os
import time
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LogisticRegression
from googletrans import Translator, LANGUAGES
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import schedule
import threading
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.cluster import KMeans
except ImportError:
    st.error("scikit-learn n'est pas installé. Veuillez ajouter 'scikit-learn==1.5.2' à requirements.txt.")
    LogisticRegression = CountVectorizer = KMeans = None
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

# Configuration des mots-clés et profils de veille
CONFIG = {
    "sectors": {
        "Finances": ["finances", "fraude financière", "banque", "investissement", "cryptomonnaie", "marché financier", "blockchain", "fintech"],
        "Santé": ["santé", "médical", "diagnostic", "soins", "hôpital"],
        "Économie": ["économie", "marché", "croissance", "récession"]
    },
    "subjects": {
        "IA": ["intelligence artificielle", "machine learning", "deep learning", "modèle de langage", "agents agentiques"]
    },
    "countries": {
        "Québec": ["Québec", "Montréal", "Québec City", "francophone"]
    },
    "profiles": {
        "Startups IA Québec": ["startup IA", "innovation", "Québec"]
    }
}

# Fonction pour interroger Semantic Scholar avec retry
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_semantic_scholar(query):
    response = requests.get(f"https://api.semanticscholar.org/v1/paper/search?query={query}")
    response.raise_for_status()
    return response.json()

# Interface Streamlit
st.title("Veille Stratégique IA pour Salesforce")

# Filtres de recherche
st.header("Filtres de Recherche")
sector = st.selectbox("Secteur", options=list(CONFIG["sectors"].keys()), label="Sélectionner un secteur")
subject = st.selectbox("Sujet", options=list(CONFIG["subjects"].keys()), label="Sélectionner un sujet")
country = st.selectbox("Pays", options=list(CONFIG["countries"].keys()), label="Sélectionner un pays")
profile = st.selectbox("Profil de Veille", options=list(CONFIG["profiles"].keys()), label="Sélectionner un profil")

# Mots-clés personnalisés
keywords = st.text_input("Mots-clés personnalisés (séparés par des virgules)", value="IA, finances, Québec, startup", label="Entrer des mots-clés")
keywords_list = [k.strip() for k in keywords.split(",")]

# Recherche rapide
search_query = st.text_input("Recherche rapide", value="IA finances Québec OR startup IA Québec", label="Entrer une requête rapide")

# Intégration Deep Search
if st.button("Lancer Deep Search"):
    st.info("Deep Search activé. Les résultats seront affichés ci-dessous.")
    # Placeholder pour les résultats de Deep Search
    st.write("Résultats de Deep Search à venir...")

# Articles et Études
st.header("Articles et Études")
if st.button("Rechercher des études"):
    query = search_query if search_query else " ".join(keywords_list)
    try:
        studies = fetch_semantic_scholar(query)
        st.write(studies)
    except Exception as e:
        st.error(f"Erreur lors de la recherche : {e}")

# Visualisations
st.header("Visualisations")
# Exemple de visualisation avec Plotly
df = pd.DataFrame({
    "Date": ["2025-01", "2025-02", "2025-03"],
    "Investissements IA": [1.2, 1.5, 1.8]
})
fig = px.line(df, x="Date", y="Investissements IA", title="Tendances des Investissements IA au Québec")
st.plotly_chart(fig)

# Planification des mises à jour
def update_veille():
    st.write("Mise à jour de la veille...")

schedule.every().day.at("08:00").do(update_veille)

# Thread pour exécuter les tâches planifiées
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()

# Initialisation SQLite
def init_db():
    try:
        conn = sqlite3.connect('veille_cache.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS results
                     (id TEXT, query TEXT, timestamp TEXT, title TEXT, url TEXT, source TEXT, source_name TEXT, date TEXT, abstract TEXT, summary TEXT)''')
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
            c.execute('''INSERT INTO results (id, query, timestamp, title, url, source, source_name, date, abstract, summary)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (str(uuid.uuid4()), query, datetime.now().isoformat(), item['title'], item['url'],
                       item['source'], item.get('source_name', 'N/A'), item['date'], item.get('abstract', 'N/A'), item.get('summary', 'N/A')))
        conn.commit()
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du cache : {e}")
    finally:
        conn.close()

def load_cache(query: str, max_age_hours: int = 24) -> List[Dict]:
    try:
        conn = sqlite3.connect('veille_cache.db')
        c = conn.cursor()
        c.execute('''SELECT title, url, source, source_name, date, abstract, summary FROM results
                     WHERE query = ? AND timestamp > ?''',
                  (query, (datetime.now() - timedelta(hours=max_age_hours)).isoformat()))
        results = [{"title": r[0], "url": r[1], "source": r[2], "source_name": r[3], "date": r[4], "abstract": r[5], "summary": r[6]} for r in c.fetchall()]
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
        translated = translator.translate(text)
        return translated[:max_length] + "..." if len(translated) > max_length else translated
    except Exception as e:
        st.error(f"Erreur de résumé avec deep_translator : {e}")
        return text[:max_length] + "..." if len(text) > max_length else text

# Scoring de pertinence (ajusté pour obtenir des scores plus élevés)
def score_relevance(item: Dict, keywords: List[str]) -> float:
    text = (item['title'] + " " + item.get('abstract', '')).lower()
    weights = {
        'finance': 3.0, 'fraude': 3.0, 'banque': 2.0, 'investissement': 2.0,
        'cryptomonnaie': 2.0, 'marché': 2.0, 'blockchain': 2.0, 'agentique': 4.0,
        'ia': 2.0, 'québec': 2.5
    }
    # Score de base : somme des poids des mots-clés présents
    base_score = sum(weights.get(keyword.lower(), 1.0) for keyword in keywords if keyword.lower() in text)
    # Bonus multiplicatif si plusieurs mots-clés sont présents
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in text)
    multiplier = 1.0 + (keyword_count * 0.2)  # Bonus de 20% par mot-clé trouvé
    final_score = base_score * multiplier
    # Normalisation : score maximum possible basé sur tous les mots-clés avec le multiplicateur maximum
    max_possible_score = sum(weights.get(keyword.lower(), 1.0) for keyword in keywords) * (1.0 + (len(keywords) * 0.2))
    return final_score / max_possible_score if max_possible_score > 0 else 0

# Filtrage des résultats pertinents (basé sur mots-clés principaux)
def filter_relevant_results(items: List[Dict], keywords: List[str]) -> List[Dict]:
    filtered = []
    required_keywords = {'ia', 'finances', 'québec', 'agentique'}  # Mots-clés principaux
    for item in items:
        text = (item['title'] + " " + item.get('abstract', '')).lower()
        if any(keyword in text for keyword in required_keywords):
            filtered.append(item)
    return filtered

# Raffinement des requêtes
def refine_query(content: List[Dict]) -> str:
    if CountVectorizer is None:
        return ""
    try:
        texts = [item.get('abstract', '') for item in content]
        vectorizer = CountVectorizer(stop_words='english', max_features=5)
        X = vectorizer.fit_transform(texts)
        keywords = [kw for kw in vectorizer.get_feature_names_out() if kw not in ['co2', 'carbon', 'climate', 'capture']]
        return ' '.join(keywords) if keywords else ""
    except Exception as e:
        st.error(f"Erreur lors du raffinement de la requête : {e}")
        return ""

# Génération de rapport synthétique
def generate_report(content: List[Dict]) -> str:
    if CountVectorizer is None or KMeans is None:
        return "Rapport indisponible : scikit-learn non installé."
    try:
        texts = [item.get('abstract', '') for item in content]
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform(texts)
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(X)
        report = ""
        for i in range(3):
            cluster_items = [content[j] for j in range(len(content)) if labels[j] == i]
            if cluster_items:
                report += f"**Thème {i+1}** : {', '.join([item['title'][:50] for item in cluster_items[:3]])}\n"
                report += f"- Sources : {', '.join(set(item['source_name'] for item in cluster_items))}\n"
                report += f"- Insight clé : {summarize_text(' '.join([item.get('abstract', '')[:200] for item in cluster_items]), max_length=150)}\n\n"
        return report if report else "Aucun thème identifié."
    except Exception as e:
        st.error(f"Erreur lors de la génération du rapport : {e}")
        return "Rapport indisponible."

# Scraping arXiv
def fetch_arxiv(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    for _ in range(3):
        try:
            query = query.replace(' ', '+')
            categories = "cat:cs.AI+OR+cat:econ.EM+OR+cat:cs.LG"
            url = f"http://export.arxiv.org/api/query?search_query={query}+AND+({categories})&max_results={max_results}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if not response.text.startswith('<?xml'):
                raise ValueError("La réponse d'arXiv n'est pas au format XML attendu.")
            soup = BeautifulSoup(response.text, 'lxml-xml')
            entries = soup.find_all('entry')
            if not entries:
                st.warning("Aucun résultat trouvé sur arXiv pour cette requête.")
            for entry in entries:
                title = entry.find('title').text.strip() if entry.find('title') else 'N/A'
                link = entry.find('id').text.strip() if entry.find('id') else '#'
                date = entry.find('published').text.strip()[:10] if entry.find('published') else 'N/A'
                abstract = entry.find('summary').text.strip() if entry.find('summary') else 'N/A'
                if any(term in abstract.lower() for term in ['co2', 'carbon capture', 'climate']):
                    continue
                summarized_abstract = summarize_text(abstract, target_lang='en')
                category = entry.find('category')['term'] if entry.find('category') else 'N/A'
                studies.append({
                    'title': title,
                    'url': link,
                    'source': 'arXiv',
                    'source_name': f"arXiv ({category})",
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
                if any(term in abstract.lower() for term in ['co2', 'carbon capture', 'climate']):
                    continue
                summarized_abstract = summarize_text(abstract, target_lang='en')
                journal = item.get('bibjson', {}).get('journal', {}).get('title', 'N/A')
                studies.append({
                    'title': title,
                    'url': url,
                    'source': 'DOAJ',
                    'source_name': journal,
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

# Scraping Semantic Scholar avec gestion des erreurs 429
def fetch_semantic_scholar(query: str, max_results: int = 3) -> List[Dict]:
    # Vérifier si des résultats existent déjà dans le cache
    cached_results = load_cache(query)
    cached_semantic_results = [item for item in cached_results if item['source'] == 'Semantic Scholar']
    if cached_semantic_results:
        st.info(f"Utilisation des résultats mis en cache pour Semantic Scholar (requête : {query}).")
        return cached_semantic_results[:max_results]

    studies = []
    for attempt in range(3):
        try:
            query = query.replace(' ', '%20')
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}&fields=title,url,abstract,venue,year"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get('data', [])[:max_results]:
                title = item.get('title', 'N/A')
                url = item.get('url', '#')
                date = str(item.get('year', 'N/A'))
                abstract = item.get('abstract', 'N/A')
                if any(term in abstract.lower() for term in ['co2', 'carbon capture', 'climate']):
                    continue
                summarized_abstract = summarize_text(abstract, target_lang='en')
                venue = item.get('venue', 'Semantic Scholar')
                studies.append({
                    'title': title,
                    'url': url,
                    'source': 'Semantic Scholar',
                    'source_name': venue,
                    'date': date,
                    'abstract': abstract,
                    'summary': summarized_abstract
                })
            time.sleep(1)
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                st.warning(f"Trop de requêtes à Semantic Scholar (tentative {attempt+1}/3). Attente avant de réessayer...")
                time.sleep(60)  # Attendre 60 secondes avant de réessayer
            else:
                st.error(f"Erreur lors de l'appel à Semantic Scholar (tentative {attempt+1}/3) : {e}")
                time.sleep(2)
                break
        except Exception as e:
            st.error(f"Erreur lors de l'appel à Semantic Scholar (tentative {attempt+1}/3) : {e}")
            time.sleep(2)
            break
    if not studies and attempt == 2:  # Après 3 tentatives échouées
        st.error("Impossible de récupérer les résultats de Semantic Scholar en raison des limites de l'API. Veuillez réessayer plus tard.")
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
                if any(term in abstract.lower() for term in ['co2', 'carbon capture', 'climate']):
                    continue
                summarized_abstract = summarize_text(abstract, target_lang='en')
                source_name = entry.get('source', {}).get('title', url.split('/')[2] if url != '#' else 'N/A')
                articles.append({
                    'title': title,
                    'url': url,
                    'source': 'Google News',
                    'source_name': source_name,
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
        X = np.array([len(item.get('abstract', '')) for item in data]).reshape(-1, 1)
        y = np.array([1 if 'agentique' in item.get('abstract', '').lower() else 0 for item in data])
        if len(np.unique(y)) > 1:
            model = LogisticRegression().fit(X, y)
            score = model.predict_proba([[500]])[0][1]
            return f"Probabilité d'adoption des agents agentiques dans {sector} au {country} d'ici 2026 : {score:.2%}"
        return "Données insuffisantes pour la prédiction."
    except Exception as e:
        return f"Erreur lors de la prédiction : {e}"

# Détection des signaux faibles
def detect_weak_signals(data: List[Dict], sector: str, country: str) -> str:
    signals = [item['title'] for item in data if 'startup' in item.get('abstract', '').lower() or 'emerging' in item.get('abstract', '').lower()]
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
st.set_page_config(
    page_title="Veille Stratégique IA pour Salesforce",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour forcer la lisibilité
st.markdown("""
    <style>
    /* Forcer le thème clair global */
    .main {
        background-color: #f5f7fa !important;
        color: #000000 !important;
    }
    .stApp {
        background-color: #f5f7fa !important;
        color: #000000 !important;
    }

    /* Style général pour tous les textes */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #000000 !important;
        font-family: 'Salesforce Sans', Arial, sans-serif !important;
    }

    /* Style des titres */
    h1 {
        color: #003087 !important;  /* Bleu foncé Salesforce */
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    h2, h3 {
        color: #003087 !important;
        margin-top: 1.5rem !important;
    }

    /* Style des champs de saisie */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
        padding: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    /* Style des sélecteurs (champ principal) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
        padding: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        background-color: #e6f0fa !important;
    }

    /* Style des options dans la liste déroulante */
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
    }
    div[data-baseweb="popover"] div[data-baseweb="menu"] div,
    div[data-baseweb="popover"] ul li {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 8px !important;
    }
    div[data-baseweb="popover"] div[data-baseweb="menu"] div:hover,
    div[data-baseweb="popover"] ul li:hover {
        background-color: #e6f0fa !important;
        color: #000000 !important;
    }

    /* Style des boutons */
    .stButton > button {
        background-color: #005FB8 !important;  /* Bleu Salesforce */
        color: #ffffff !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: background-color 0.3s !important;
    }
    .stButton > button:hover {
        background-color: #003087 !important;  /* Bleu foncé Salesforce */
    }

    /* Style des expanders */
    .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
        margin-bottom: 1rem !important;
    }
    .stExpander div[role="button"] {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f5f7fa !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px 5px 0 0 !important;
        padding: 10px 20px !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #005FB8 !important;
        color: #ffffff !important;
    }

    /* Style des messages (erreurs, succès, etc.) */
    .stAlert > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
    }

    /* Style des séparateurs */
    hr {
        border-top: 1px solid #cccccc !important;
        margin: 2rem 0 !important;
    }

    /* S'assurer que les éléments Markdown sont lisibles */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #000000 !important;
    }
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
    st.markdown("### Filtres de recherche")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="medium")
    with col1:
        st.markdown("**Secteur**")
        sector = st.selectbox("", list(CONFIG["sectors"].keys()), key="sector_select")
    with col2:
        st.markdown("**Sujet**")
        subject = st.selectbox("", list(CONFIG["subjects"].keys()), key="subject_select")
    with col3:
        st.markdown("**Pays**")
        country = st.selectbox("", list(CONFIG["countries"].keys()), key="country_select")
    with col4:
        st.markdown("**Profil de veille**")
        profile = st.selectbox("", ["Aucun"] + list(CONFIG["profiles"].keys()), key="profile_select")

    st.markdown("---")
    st.markdown("**Mots-clés personnalisés**")
    custom_keywords = st.text_input("(séparés par des virgules)", "", key="custom_keywords_input")
    keywords = CONFIG["sectors"][sector] + CONFIG["subjects"][subject] + CONFIG["countries"][country]
    if profile != "Aucun":
        keywords += CONFIG["profiles"][profile]
    if custom_keywords:
        keywords += [k.strip() for k in custom_keywords.split(",")]

    # Optimisation de la requête
    keywords = list(dict.fromkeys(keywords))  # Supprimer les doublons
    query = f"{subject} {sector} {country} {' '.join(keywords)}"
    st.markdown(f"**Requête** : {query}")

    st.markdown("---")
    st.markdown("**Recherche rapide**")
    quick_search = st.text_input("(remplace la requête ci-dessus)", "", key="quick_search_input")
    if quick_search:
        query = quick_search

    st.markdown("---")
    st.markdown("**Intégration Deep Search**")
    deep_search_input = st.text_area("Coller les résultats de Deep Search", "", key="deep_search_input")
    if deep_search_input:
        all_content.append({
            'title': "Résultats Deep Search",
            'url': '#',
            'source': 'Deep Search',
            'source_name': 'Deep Search',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'abstract': deep_search_input,
            'summary': summarize_text(deep_search_input, target_lang='en')
        })

    st.markdown("---")
    st.markdown("### Actions")
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        if st.button("Lancer la veille"):
            with st.spinner("Collecte des données en cours..."):
                # Optimisation de la requête pour Semantic Scholar
                semantic_query = f"{subject} {sector} {country} agentique"
                # Vérifier le cache
                all_content += load_cache(query)
                if not all_content or not deep_search_input:
                    articles = fetch_google_news(query)
                    studies_arxiv = fetch_arxiv(query)
                    studies_doaj = fetch_doaj(query)
                    studies_semantic = fetch_semantic_scholar(semantic_query)
                    all_content += articles + studies_arxiv + studies_doaj + studies_semantic
                    # Raffiner la requête
                    refined_query = refine_query(all_content)
                    if refined_query:
                        articles_refined = fetch_google_news(refined_query)
                        studies_doaj_refined = fetch_doaj(refined_query)
                        all_content += articles_refined + studies_doaj_refined
                    save_cache(all_content, query)

                if not all_content:
                    st.warning("Aucun résultat trouvé.")
                else:
                    # Filtrer les résultats pertinents
                    all_content = filter_relevant_results(all_content, keywords)
                    if not all_content:
                        st.warning("Aucun résultat pertinent trouvé après filtrage.")

                    # Appliquer le scoring de pertinence
                    for item in all_content:
                        item['relevance_score'] = score_relevance(item, keywords)

                    # Onglets pour organiser les résultats
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Articles", "Études", "Analyse Concurrentielle", "Recommandations", "Visualisations"])

                    with tab1:
                        st.subheader("Articles")
                        sort_by = st.selectbox("Trier par", ["Date", "Source", "Pertinence"], key="sort_articles")
                        sort_key = lambda x: x['date'] if sort_by == "Date" else x['source_name'] if sort_by == "Source" else -x['relevance_score']
                        # Filtrer les articles avec un score >= 90%
                        filtered_articles = [x for x in all_content if x['source'] == 'Google News' and x['relevance_score'] >= 0.9]
                        if not filtered_articles:
                            st.warning("Aucun article n'atteint un score de pertinence de 90% ou plus. Essayez d'ajuster vos mots-clés ou de réduire le seuil.")
                        for item in sorted(filtered_articles, key=sort_key):
                            with st.expander(f"{item['title']}"):
                                st.write(f"**Source** : [{item['source_name']}]({item['url']})")
                                st.write(f"**URL** : {item['url']}")
                                st.write(f"**Date** : {item['date']}")
                                st.write(f"**Abstract** : {item['abstract']}")
                                st.write(f"**Résumé** : {item['summary']} (Généré par IA via Google Translator)")
                                st.progress(item['relevance_score'])
                                st.write(f"**Score de pertinence** : {item['relevance_score']:.2%}")

                    with tab2:
                        st.subheader("Études")
                        sort_by = st.selectbox("Trier par", ["Date", "Source", "Pertinence"], key="sort_studies")
                        sort_key = lambda x: x['date'] if sort_by == "Date" else x['source_name'] if sort_by == "Source" else -x['relevance_score']
                        # Filtrer les études avec un score >= 90%
                        filtered_studies = [x for x in all_content if x['source'] in ['arXiv', 'DOAJ', 'Semantic Scholar'] and x['relevance_score'] >= 0.9]
                        if not filtered_studies:
                            st.warning("Aucune étude n'atteint un score de pertinence de 90% ou plus. Essayez d'ajuster vos mots-clés ou de réduire le seuil.")
                        for item in sorted(filtered_studies, key=sort_key):
                            with st.expander(f"{item['title']}"):
                                st.write(f"**Source** : [{item['source_name']}]({item['url']})")
                                st.write(f"**URL** : {item['url']}")
                                st.write(f"**Date** : {item['date']}")
                                st.write(f"**Abstract** : {item['abstract']}")
                                st.write(f"**Résumé** : {item['summary']} (Généré par IA via Google Translator)")
                                st.progress(item['relevance_score'])
                                st.write(f"**Score de pertinence** : {item['relevance_score']:.2%}")

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
                        st.subheader("Rapport synthétique")
                        st.markdown(generate_report(all_content))
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
                            # Graphique de pertinence
                            df_scores = pd.DataFrame([(x['title'], x['relevance_score']) for x in all_content], columns=['Titre', 'Score de Pertinence'])
                            fig_scores = px.bar(df_scores, x='Score de Pertinence', y='Titre', title='Pertinence des Résultats')
                            st.plotly_chart(fig_scores)
                        else:
                            st.error("Visualisations indisponibles : plotly non installé.")

                    # Alerte pour nouveaux résultats
                    if len(all_content) > len(load_cache(query, max_age_hours=1)):
                        st.success("Nouveaux résultats détectés !")

    with col_btn2:
        if st.button("Exporter les résultats") and all_content:
            results = {
                "title": [], "url": [], "source": [], "source_name": [], "date": [], "abstract": [], "summary": [], "relevance_score": []
            }
            for item in all_content:
                results["title"].append(item["title"])
                results["url"].append(item["url"])
                results["source"].append(item["source"])
                results["source_name"].append(item["source_name"])
                results["date"].append(item["date"])
                results["abstract"].append(item["abstract"])
                results["summary"].append(item["summary"])
                results["relevance_score"].append(item.get("relevance_score", 0))
            
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button("Télécharger CSV", csv, "veille_strategique.csv", "text/csv")

# Tâches planifiées
def run_scheduled_veille():
    query = "Agents Agentiques Santé Québec"
    all_content = fetch_google_news(query) + fetch_arxiv(query) + fetch_doaj(query) + fetch_semantic_scholar(query)
    refined_query = refine_query(all_content)
    if refined_query:
        all_content += fetch_google_news(refined_query) + fetch_doaj(refined_query)
    save_cache(all_content, query)
    st.success("Mise à jour quotidienne effectuée.")

schedule.every().day.at("02:00").do(run_scheduled_veille)

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=schedule_loop, daemon=True).start()
