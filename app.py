import streamlit as st
from fetch_news import run_news_crawl, KEYWORDS
from fetch_sources import search_with_openai, search_arxiv, search_consensus_via_serpapi
from summarizer import summarize_articles
from generate_docx import generate_docx

st.set_page_config(page_title="Veille stratégique IA", layout="wide")
st.title("🧠 Veille Stratégique – Agents IA en Finance & Santé")

st.markdown("""
Ce tableau de bord automatise la veille technologique sur les agents IA en santé, finance et recherche scientifique.
""")

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

st.sidebar.header("⚡ Mode d'exécution")
fast_mode = st.sidebar.checkbox("Activer le mode rapide (résumés limités)", value=True)

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
                    from fetch_news import run_news_crawl
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

        with st.spinner("🧠 Génération des résumés avec IA..."):
            summaries = summarize_articles(articles, limit=5 if fast_mode else None)

        for topic in selected_keywords:
            st.subheader(f"📁 {topic}")
            if topic in summaries:
                st.markdown(summaries[topic])

            with st.expander("🔗 Articles sources"):
                for article in [a for a in articles if a["keyword"] == topic]:
                    source_icon = "🌐"
                    if "Gemini" in article["title"]:
                        source_icon = "🤖"
                    elif "OpenAI" in article["title"]:
                        source_icon = "🧠"
                    elif "Consensus" in article["link"]:
                        source_icon = "🔬"
                    elif "arxiv.org" in article["link"]:
                        source_icon = "📚"
                    elif "CSE" in article["title"]:
                        source_icon = "🧭"

                    st.markdown(f"""
- **{article['title']}**  
  {article['snippet']}  
  📎 [Lien]({article['link']}) — *{source_icon}*
""")

        if summaries:
            docx_file = generate_docx(summaries, articles)
            st.download_button(
                label="📥 Télécharger le rapport en DOCX",
                data=docx_file,
                file_name="rapport_veille.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )