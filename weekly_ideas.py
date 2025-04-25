# 🌟 weekly_ideas.py : Génération hebdomadaire de 5 idées stratégiques
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_weekly_ideas():
    st.subheader("🌟 Idées stratégiques de la semaine")

    if st.button("💡 Générer 5 idées IA innovantes"):
        with st.spinner("Génération des idées en cours..."):
            try:
                prompt = "Propose 5 idées innovantes exploitant l'intelligence artificielle dans la santé, la finance ou la gestion d'entreprise."
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Tu es un stratège IA créatif et visionnaire."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=500
                )
                st.success("Voici 5 idées 🌟")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
