import streamlit as st
from fetch_news import run_news_crawl, KEYWORDS
from fetch_sources import search_with_openai, search_arxiv, search_consensus_via_serpapi
from summarizer import summarize_articles, summarize_text_block
from report_builder import build_report_view, generate_docx
from alerts import trigger_alerts, save_alert_to_sheet
from weekly_ideas import generate_weekly_ideas

st.set_page_config(page_title="Tableau de bord stratégique IA", layout="wide")
st.title("📊 Tableau de bord stratégique – IA en temps réel")

st.markdown("""
Bienvenue sur le tableau de bord de veille stratégique IA.

**Fonctionnalités incluses :**
- Détection des tendances IA des dernières 24h
- Génération automatique de rapports hebdomadaires
- Analyse concurrentielle automatisée
- Recommandations stratégiques via IA
- Système d’alertes personnalisables
- Génération hebdomadaire d’idées innovantes via GPT-4
""")

# 🎛️ Paramètres latéraux
st.sidebar.header("🔍 Mots-clés à surveiller")
selected_keywords = st.sidebar.multiselect("Sujets à analyser :", KEYWORDS, default=KEYWORDS)

st.sidebar.header("⚙️ Sources à inclure")
use_google_news = st.sidebar.checkbox("🌐 Google News", value=True)
use_serpapi = st.sidebar.checkbox("🔍 SerpAPI", value=True)
use_cse = st.sidebar.checkbox("🧭 Google CSE", value=True)
use_gemini = st.sidebar.checkbox("🤖 Gemini", value=True)
use_openai = st.sidebar.checkbox("🧠 OpenAI", value=True)
use_arxiv = st.sidebar.checkbox("📚 ArXiv", value=True)
use_consensus = st.sidebar.checkbox("🔬 Consensus", value=True)

st.sidebar.header("⚡ Exécution")
fast_mode = st.sidebar.checkbox("Mode rapide (résumés limités)", value=True)
enable_alerts = st.sidebar.checkbox("🔔 Activer les alertes personnalisées", value=False)
enable_ideas = st.sidebar.checkbox("💡 Générer 5 idées innovantes IA (Hebdo)", value=False)

# ⚠️ Validation
if not selected_keywords:
    st.warning("❗ Veuillez sélectionner au moins un mot-clé.")
else:
    if st.button("🚀 Lancer la veille stratégique"):
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

        st.success(f"{len(articles)} articles trouvés.")
        st.divider()

        with st.spinner("🧠 Génération des résumés par IA..."):
            summaries = summarize_articles(articles, limit=5 if fast_mode else None)

        st.subheader("📌 Résumé des dernières 24h")
        if articles:
            all_snippets = "\n".join([a['snippet'] for a in articles if 'snippet' in a])
            summary_24h = summarize_text_block(all_snippets)
            st.markdown(summary_24h)

        with st.expander("📊 Rapport complet généré automatiquement"):
            build_report_view(summaries, articles)

        if summaries:
            docx_file = generate_docx(summaries, articles)
            st.download_button(
                label="📥 Télécharger le rapport en DOCX",
                data=docx_file,
                file_name="rapport_veille.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # 🔔 Alertes personnalisées
        if enable_alerts:
            st.subheader("🔔 Alertes stratégiques")
            alert_email = st.text_input("Email pour les alertes :")
            if alert_email:
                trigger_alerts(selected_keywords, alert_email)
                save_alert_to_sheet(selected_keywords, alert_email)
                st.success("✅ Alerte enregistrée et sauvegardée dans Google Sheets.")

        # 💡 Idées IA innovantes (Hebdo)
        if enable_ideas:
            st.subheader("💡 Idées innovantes proposées par IA")
            for idea in generate_weekly_ideas():
                st.markdown(f"✅ {idea}")
