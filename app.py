import streamlit as st
from fetch_news import run_news_crawl
from fetch_sources import (
    search_with_openai, search_arxiv,
    search_consensus_via_serpapi,
    search_with_perplexity, search_with_google_cse as search_with_cse_sources
)
from summarizer import (
    summarize_articles, summarize_text_block,
    generate_innovation_ideas, generate_strategic_recommendations,
    generate_swot_analysis, compute_strategic_score,
    always_use_keywords, INNOVATION_KEYWORDS
)
from report_builder import build_report_view, generate_docx
from streamlit_timeline import timeline
import datetime

st.set_page_config(page_title="Veille stratégique IA", layout="wide")
st.title("\U0001F4CA Tableau de bord IA – Stratégie & Innovation")

st.markdown("""
Ce tableau de bord automatise la veille stratégique sur les agents IA dans les domaines de la santé, de la finance,
ainsi que les innovations émergentes.
""")

st.sidebar.header("🍿️ Domaines ciblés")
selected_sector = st.sidebar.radio("Choisis un secteur :", ["Santé", "Finance", "Tous"])

# Sous-thèmes dynamiques
subtopics = {
    "Santé": ["santé mentale", "diagnostic IA", "robotique chirurgicale"],
    "Finance": ["fintech B2B", "analyse prédictive", "insurtech"],
    "Tous": [""]
}
selected_subtopic = st.sidebar.selectbox("Sous-thème :", subtopics[selected_sector])

st.sidebar.header("⚙️ Modules à activer")
use_google_news = st.sidebar.checkbox("🌐 Google News", value=True)
use_cse = st.sidebar.checkbox("🛁 Google CSE/TechCrunch/VB", value=True)
use_perplexity = st.sidebar.checkbox("🧠 Perplexity AI", value=True)
use_gemini = st.sidebar.checkbox("🤖 Gemini", value=True)
use_openai = st.sidebar.checkbox("💬 OpenAI", value=True)
use_arxiv = st.sidebar.checkbox("📚 ArXiv (scientifique)", value=False)
use_consensus = st.sidebar.checkbox("🔬 Consensus", value=False)

st.sidebar.header("⚡ Mode IA")
fast_mode = st.sidebar.checkbox("Mode rapide (résumés limités)", value=True)
salesforce_mode = st.sidebar.checkbox("💼 Mode Salesforce (recommandations commerciales)", value=False)
show_ideas = st.sidebar.checkbox("💡 Afficher 5 idées innovantes de la semaine", value=True)
show_swot = st.sidebar.checkbox("🧮 Générer une analyse SWOT", value=True)

sector_keywords = {
    "Santé": ["Hippocratic AI", "AI in Healthcare", "One AI Health", "Amelia AI", "IA médicale"],
    "Finance": ["Finley AI", "Interface.ai", "AI in Finance", "automatisation bancaire"],
    "Tous": []
}

keywords = sector_keywords[selected_sector] + INNOVATION_KEYWORDS + always_use_keywords
if selected_subtopic:
    keywords.append(selected_subtopic)

if st.button("🚀 Lancer la veille stratégique"):
    progress = st.progress(0)
    articles = []

    for i, keyword in enumerate(keywords):
        with st.spinner(f"🔎 Recherche pour : {keyword}"):
            if use_google_news or use_cse:
                articles.extend(run_news_crawl([keyword], use_google_news=use_google_news))
            if use_cse:
                articles.extend(search_with_cse_sources(keyword))
            if use_perplexity:
                articles.extend(search_with_perplexity(keyword))
            if use_arxiv:
                articles.extend(search_arxiv(keyword))
            if use_consensus:
                articles.extend(search_consensus_via_serpapi(keyword))
            if use_openai:
                articles.append({
                    "keyword": keyword,
                    "title": "Résumé OpenAI",
                    "link": "https://platform.openai.com/",
                    "snippet": search_with_openai(keyword),
                    "date": datetime.datetime.now().isoformat()
                })
        progress.progress((i + 1) / len(keywords))

    st.success(f"{len(articles)} articles trouvés.")
    st.divider()

    with st.spinner("🧠 Résumés générés par IA..."):
        summaries = summarize_articles(articles, limit=5 if fast_mode else None)

    st.subheader("📌 Résumé exécutif – dernières 24h")
    all_snippets = "\n".join([a['snippet'] for a in articles])
    summary_24h = summarize_text_block(all_snippets)
    st.markdown(summary_24h)

    if show_swot:
        st.subheader("🧠 Analyse SWOT automatique")
        swot_text = generate_swot_analysis(all_snippets)
        st.markdown(swot_text)

    st.subheader("📚 Résumés par sujet")
    col1, col2 = st.columns(2)
    for i, (topic, summary) in enumerate(summaries.items()):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"### {topic}")
            st.markdown(summary)

    with st.expander("📊 Rapport complet structuré"):
        build_report_view(summaries, articles)

    if show_ideas:
        st.subheader("💡 5 idées innovantes générées par IA")
        for idea in generate_innovation_ideas(all_snippets):
            st.markdown(f"- {idea}")

    if salesforce_mode:
        st.subheader("📈 Recommandations IA – Commercial / Salesforce")
        for reco in generate_strategic_recommendations(all_snippets, mode="salesforce"):
            st.markdown(f"✅ {reco}")

    # Timeline enrichie avec dates réelles si disponibles
    st.subheader("🕒 Timeline des sujets stratégiques")
    events = []
    for article in articles:
        date_str = article.get("date") or datetime.datetime.now().isoformat()
        date = datetime.datetime.fromisoformat(date_str[:19])
        color_map = {
            "Santé": "#1f77b4",
            "Finance": "#ff7f0e",
            "Tous": "#2ca02c"
        }
        events.append({
            "start_date": {
                "year": date.year,
                "month": date.month,
                "day": date.day
            },
            "text": {
                "headline": article.get("title", "Sans titre"),
                "text": article.get("snippet", "")[:300] + "..."
            },
            "group": selected_subtopic or selected_sector,
            "background": color_map.get(selected_sector, "#999999")
        })
    timeline({"title": {"text": {"headline": "Évolution des agents IA par thème"}}, "events": events})

    if summaries:
        docx_file = generate_docx(summaries, articles)
        st.download_button(
            label="📅 Télécharger le rapport en DOCX",
            data=docx_file,
            file_name="rapport_veille.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

