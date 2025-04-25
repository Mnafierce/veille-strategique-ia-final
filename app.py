import streamlit as st
from fetch_news import run_news_crawl, KEYWORDS
from fetch_sources import search_with_openai, search_arxiv, search_consensus_via_serpapi
from summarizer import summarize_articles, summarize_text_block
from report_builder import build_report_view, generate_docx
from alerts import alert_interface
from idea_generator import generate_weekly_ideas

st.set_page_config(page_title="Veille stratégique IA", layout="wide")
st.title("📊 Tableau de bord de veille stratégique IA – 24h et hebdomadaire")

st.markdown("""
Ce tableau de bord automatise la veille technologique sur les agents IA en santé, finance et recherche scientifique.
Il inclut des résumés quotidiens, un rapport structuré hebdomadaire, un système d'alerte personnalisée, et des idées innovantes générées par IA.
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
use_agent = st.sidebar.checkbox("🧑‍💼 Activer l'agent stratégique", value=False)

st.sidebar.header("⚡ Mode d'exécution")
fast_mode = st.sidebar.checkbox("Activer le mode rapide (résumés limités)", value=True)

# ⚠️ Validation
if not selected_keywords:
    st.warning("❗ Veuillez sélectionner au moins un mot-clé.")
else:
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

        st.success(f"{len(articles)} articles trouvés.")
        st.divider()

        with st.spinner("🧠 Génération des résumés avec IA (article par article)..."):
            summaries = summarize_articles(articles, limit=5 if fast_mode else None)

        # 📌 Résumé exécutif des dernières 24h
        st.subheader("📌 Résumé exécutif – 24 dernières heures")
        all_snippets = "\n".join([a['snippet'] for a in articles if 'snippet' in a])
        summary_24h = summarize_text_block(all_snippets)
        st.markdown(summary_24h)

        # 📊 Rapport structuré
        with st.expander("📊 Rapport complet généré"):
            build_report_view(summaries, articles)

        # 📥 Téléchargement DOCX
        if summaries:
            docx_file = generate_docx(summaries, articles)
            st.download_button(
                label="📥 Télécharger le rapport en DOCX",
                data=docx_file,
                file_name="rapport_veille.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # 🚨 Alertes personnalisées
        alerts = alert_interface()
        for article in articles:
            for alert in alerts:
                if alert.lower() in article['title'].lower():
                    st.warning(f"🚨 Alerte détectée : **{alert}** dans {article['title']}")

        # 💡 Idées IA
        st.subheader("💡 Idées stratégiques générées par IA (hebdo)")
        for idea in generate_weekly_ideas():
            st.markdown(f"- {idea}")

        # 🧠 Agent stratégique
        if use_agent:
            st.subheader("🧑‍💼 Agent stratégique interactif")
            question = st.text_input("Pose une question à l’agent IA :")
            if question:
                with st.spinner("🤖 L'agent réfléchit..."):
                    try:
                        from agent_setup import run_veille_agent
                        response = run_veille_agent(question)
                        st.markdown(f"### Réponse de l'agent\n{response}")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l’appel à l’agent : {str(e)}")

