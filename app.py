import streamlit as st
from fetch_news import run_news_crawl
from summarizer import summarize_articles, summarize_text_block
from report_builder import build_report_view, generate_docx
from fetch_sources import search_with_openai, search_arxiv, search_consensus_via_serpapi

st.set_page_config(page_title="Veille stratégique IA", layout="wide")
st.title("📊 Tableau de bord IA stratégique")

st.markdown("""
Ce tableau de bord automatise la veille technologique sur les agents IA en santé, finance et recherche scientifique.
""")

# ————————————————————————————————
# 🔍 Choix de secteur (mots-clés dynamiques)
# ————————————————————————————————
st.sidebar.header("🏢 Choix du secteur")
secteur = st.sidebar.selectbox("Sélectionne un secteur :", ["Finance", "Santé", "Tous les secteurs"])

keywords_finance = [
    "FinConecta", "Finley AI", "Interface.ai", "Deloitte", "Banque", "Finance",
    "gestion de patrimoine", "banque numérique", "comptabilité automatisée", "agentic AI", "LLM en finance"
]

keywords_sante = [
    "Hippocratic AI", "ONE AI Health", "agentic AI", "IA en santé",
    "diagnostic par IA", "robot médical", "dossier santé numérique", "IA pour la recherche clinique"
]

from summarizer import always_use_keywords

if secteur == "Finance":
    selected_keywords = keywords_finance + always_use_keywords
elif secteur == "Santé":
    selected_keywords = keywords_sante + always_use_keywords
else:
    selected_keywords = keywords_finance + keywords_sante + always_use_keywords

if st.sidebar.checkbox("Afficher les mots-clés utilisés"):
    st.sidebar.write(selected_keywords)

# ————————————————————————————————
# ⚙️ Sources à inclure
# ————————————————————————————————
st.sidebar.header("⚙️ Sources à inclure")
use_google_news = st.sidebar.checkbox("🌐 Google News", value=True)
use_serpapi = st.sidebar.checkbox("🔍 SerpAPI", value=True)
use_cse = st.sidebar.checkbox("🧭 Google CSE", value=True)
use_gemini = st.sidebar.checkbox("🤖 Gemini", value=True)
use_openai = st.sidebar.checkbox("🧠 OpenAI", value=True)
use_arxiv = st.sidebar.checkbox("📚 ArXiv", value=True)
use_consensus = st.sidebar.checkbox("🔬 Consensus", value=True)
use_agent = st.sidebar.checkbox("🧑‍💼 Activer l'agent stratégique", value=False)

# ————————————————————————————————
# ⚡ Mode rapide (limite le nombre d'articles)
# ————————————————————————————————
st.sidebar.header("⚡ Mode d'exécution")
fast_mode = st.sidebar.checkbox("Activer le mode rapide (résumés limités)", value=True)

# ————————————————————————————————
# 🚀 Lancer la veille
# ————————————————————————————————
if st.button("🚀 Lancer la veille maintenant"):
    progress = st.progress(0)
    total = len(selected_keywords)
    articles = []

    for i, keyword in enumerate(selected_keywords):
        with st.spinner(f"🔎 Recherche pour : {keyword}"):
            if use_google_news or use_serpapi or use_cse or use_gemini:
                articles.extend(run_news_crawl(
                    [keyword],
                    use_google_news=use_google_news,
                    use_serpapi=use_serpapi,
                    use_cse=use_cse,
                    use_gemini=use_gemini
                ))

            if use_arxiv:
                articles.extend(search_arxiv(keyword))
            if use_consensus:
                articles.extend(search_consensus_via_serpapi(keyword))
            if use_openai:
                openai_summary = search_with_openai(keyword)
                articles.append({
                    "keyword": keyword,
                    "title": "Résumé généré via OpenAI",
                    "link": "https://platform.openai.com/",
                    "snippet": openai_summary
                })

        progress.progress((i + 1) / total)

    st.success(f"✅ {len(articles)} articles trouvés.")
    st.divider()

    with st.spinner("🧠 Résumés IA en cours..."):
        summaries = summarize_articles(articles, limit=5 if fast_mode else None)

    # 📌 Résumé exécutif global (24h)
    st.subheader("📌 Résumé exécutif – 24 dernières heures")
    all_snippets = "\n".join([a['snippet'] for a in articles])
    summary_24h = summarize_text_block(all_snippets)
    st.markdown(summary_24h)

    # 📊 Rapport structuré complet
    with st.expander("📊 Rapport complet généré"):
        build_report_view(summaries, articles)

    # 📁 Téléchargement du rapport
    if summaries:
        docx_file = generate_docx(summaries, articles)
        st.download_button(
            label="📥 Télécharger le rapport en DOCX",
            data=docx_file,
            file_name="rapport_veille.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# 🧠 Agent intelligent (optionnel)
if use_agent:
    question = st.text_input("Pose une question à l’agent stratégique :")
    if question:
        with st.spinner("🤖 L'agent réfléchit..."):
            try:
                from agent_setup import run_veille_agent
                response = run_veille_agent(question)
                st.markdown(f"### Réponse de l'agent\n{response}")
            except Exception as e:
                st.error(f"❌ Erreur lors de l’appel à l’agent : {str(e)}")
