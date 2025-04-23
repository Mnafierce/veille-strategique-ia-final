import streamlit as st
from openai import OpenAI
import os

ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")  # ← définis-le dans secrets.toml
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def lancer_thread_stream_openai():
    st.subheader("💬 Assistant IA stratégique")
    st.markdown("Pose une question à l’assistant :")

    user_input = st.text_area("Ta question", key="question", height=100)

    if st.button("Envoyer"):
        if not user_input.strip():
            st.warning("❗ Entrée vide")
            return

        with st.spinner("⏳ L’assistant réfléchit..."):
            try:
                thread = client.beta.threads.create()

                # Ajouter le message de l’utilisateur
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input
                )

                # Lancer le traitement
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=ASSISTANT_ID
                )

                # Attendre que l’assistant réponde
                while True:
                    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                    if run_status.status == "completed":
                        break

                # Récupérer le dernier message de l’assistant
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                assistant_response = messages.data[0].content[0].text.value
                st.success("✅ Réponse :")
                st.markdown(assistant_response)

            except Exception as e:
                st.error(f"❌ Erreur assistant : {e}")
