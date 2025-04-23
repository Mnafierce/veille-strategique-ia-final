import streamlit as st
from fetch_news import run_news_crawl, KEYWORDS
from summarizer import summarize_articles
from generate_docx import generate_docx
from send_to_mem0 import send_to_mem0  # à créer si tu veux envoyer les résumés vers mem0

# Configuration de la page
st.set_page_config(page_title="Veille stratégique IA", layout="wide")

# Titre principal
st.title("🧠 Veille Stratégique – Agents IA en Finance & Santé")
st.markdown("""
Ce tableau de bord génère automatiquement une synthèse des actualités liées aux agents intelligents,
dans les secteurs de la santé, de la finance et de l'intelligence artificielle.
""")

# Menu latéral
st.sidebar.header("🔍 Mots-clés à surveiller")
selected_keywords = st.sidebar.multiselect(
    "Sélectionne les entreprises ou sujets à analyser :",
    KEYWORDS,
    default=KEYWORDS
)

st.sidebar.header("⚙️ Sources à inclure")
use_google_news = st.sidebar.checkbox("🌐 Google News", value=True)
use_serpapi = st.sidebar.checkbox("🔍 SerpAPI", value=True)
use_cse = st.sidebar.checkbox("🧭 Google CSE", value=True)
use_gemini = st.sidebar.checkbox("🤖 Gemini", value=True)

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
            with st.spinner(f"🔍 Recherche : {keyword}"):
                result = run_news_crawl(
                    [keyword],
                    use_google_news=use_google_news,
                    use_serpapi=use_serpapi,
                    use_cse=use_cse,
                    use_gemini=use_gemini
                )
                articles.extend(result)
            progress.progress((i + 1) / total)

        st.success(f"{len(articles)} articles trouvés.")
        st.divider()

        with st.spinner("🧠 Génération des résumés avec IA..."):
            summaries = summarize_articles(articles, limit=5 if fast_mode else None, use_gemini=use_gemini)


        for topic in selected_keywords:
            st.subheader(f"🗂️ {topic}")
            if topic in summaries:
                st.markdown(summaries[topic])
                send_to_mem0(summaries[topic], topic)

            with st.expander("🔎 Articles sources"):
                for article in [a for a in articles if a["keyword"] == topic]:
                    source_label = "🌐 Google News"
                    if "Gemini" in article["title"]:
                        source_label = "🤖 Gemini"
                    elif "SerpAPI" in article["title"]:
                        source_label = "🔍 SerpAPI"
                    elif "Google CSE" in article["title"]:
                        source_label = "🧭 Google CSE"

                    st.markdown(f"""
- **{article['title']}**  
  {article['snippet']}  
  📎 [Lien]({article['link']}) — *{source_label}*
""")

        if summaries:
            docx_file = generate_docx(summaries, articles)
            st.download_button(
                label="📥 Télécharger le rapport en DOCX",
                data=docx_file,
                file_name="rapport_veille.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )