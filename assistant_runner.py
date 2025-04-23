# assistant_runner.py
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

# Initialise client avec ta clef d'API OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Créer un assistant
assistant = client.beta.assistants.create(
    name="Strategic AI Monitor",
    instructions="Tu es un assistant de veille stratégique. Ton rôle est d'analyser des blocs de texte pour extraire des tendances, signaux faibles, concurrents et opportunités dans le domaine des agents IA.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)

# 2. Créer une session (thread)
thread = client.beta.threads.create()

# Fonction pour ajouter un message au thread

def add_message(content):
    return client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

# 3. Handler personnalisé pour suivre la réponse en streaming
class VeilleEventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print("\n\033[94massistant >\033[0m", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

# 4. Lancer la création du "run" et streamer la réponse

def run_and_stream(instruction="Voici le contenu à analyser :", additional_message=""):
    add_message(additional_message)
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instruction,
        event_handler=VeilleEventHandler(),
    ) as stream:
        stream.until_done()

# Exemple de test local (tu peux le remplacer par une intégration Streamlit)
if __name__ == "__main__":
    contenu_test = """
    Amelia AI annonce une nouvelle plateforme pour les agents conversationnels en milieu hospitalier. IBM Watson réoriente ses investissements vers la finance d'entreprise. Vertex AI est adopté par Finley pour améliorer la détection de fraude bancaire.
    """
    run_and_stream("Analyse les dernières nouvelles pour extraire les tendances clés.", contenu_test)
