# 📊 report_builder.py : Génère un rapport structuré façon Gemini Deep Search
import streamlit as st
from io import BytesIO
from docx import Document

def build_report_view(summaries_by_topic, articles):
    """Affiche un rapport structuré dans Streamlit"""

    st.subheader("📌 Résumé exécutif")
    st.markdown("""
    Ce rapport présente une synthèse stratégique sur les avancées liées aux agents IA externes,
    en santé, finance et technologie, pour les mots-clés sélectionnés.
    """)

    # Regrouper par thématique
    grouped = {}
    for topic, summary in summaries_by_topic.items():
        if any(k in topic.lower() for k in ["health", "santé", "hippocratic"]):
            cat = "💊 Santé"
        elif any(k in topic.lower() for k in ["finance", "bank", "finley"]):
            cat = "💰 Finance"
        elif any(k in topic.lower() for k in ["ai", "agent", "lyzr", "gemini"]):
            cat = "🤖 Agents IA / Technologies"
        else:
            cat = "📦 Autres"

        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append((topic, summary))

    for cat, entries in grouped.items():
        st.subheader(cat)
        for topic, summary in entries:
            st.markdown(f"**🔹 {topic}**")
            st.markdown(summary)
            with st.expander("🔎 Articles sources"):
                for art in [a for a in articles if a["keyword"] == topic]:
                    st.markdown(f"- **{art['title']}**  \\n                    {art['snippet']}  \\n                    [Lien original]({art['link']})")


def generate_docx(summaries_by_topic, articles):
    """Crée un fichier DOCX structuré façon Deep Search"""
    doc = Document()
    doc.add_heading("Rapport stratégique – Agents IA", 0)

    doc.add_paragraph(
        "Ce rapport regroupe les tendances, concurrents, et signaux du marché liés aux agents intelligents,"
        " dans les domaines de la santé, finance et intelligence artificielle."
    )

    # Résumé exécutif
    doc.add_heading("Résumé exécutif", level=1)
    doc.add_paragraph(
        "Ce résumé est généré automatiquement à partir d'une veille stratégique sur des dizaines de sources."
    )

    grouped = {}
    for topic, summary in summaries_by_topic.items():
        if any(k in topic.lower() for k in ["health", "santé", "hippocratic"]):
            cat = "Santé"
        elif any(k in topic.lower() for k in ["finance", "bank", "finley"]):
            cat = "Finance"
        elif any(k in topic.lower() for k in ["ai", "agent", "lyzr", "gemini"]):
            cat = "IA / Agents"
        else:
            cat = "Autres"
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append((topic, summary))

    for cat, entries in grouped.items():
        doc.add_heading(cat, level=2)
        for topic, summary in entries:
            doc.add_heading(topic, level=3)
            doc.add_paragraph(summary)

            sources = [a for a in articles if a["keyword"] == topic]
            if sources:
                doc.add_paragraph("Sources :", style="Intense Quote")
                for art in sources:
                    doc.add_paragraph(f"- {art['title']} : {art['link']}", style="List Bullet")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer