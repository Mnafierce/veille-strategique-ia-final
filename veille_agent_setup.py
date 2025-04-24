# agent_setup.py

from agents import Agent, Tool, Runner

# Exemple d'outil simple pour illustrer
# Vous pouvez le remplacer par un vrai outil comme la recherche ArXiv

def synthese_personnalisee(instruction: str) -> str:
    # Exemple de traitement simulé
    return f"Synthèse exécutée pour : {instruction}"

synthese_tool = Tool.from_function(
    synthese_personnalisee,
    name="SyntheseTool",
    description="Produit une synthèse personnalisée sur un thème donné."
)

# Création de l'agent principal de veille stratégique
veille_agent = Agent(
    name="VeilleStrategiqueAgent",
    instructions=(
        "Tu es un expert analyste en veille technologique. Ton rôle est de répondre de façon claire, structurée et stratégique "
        "à toute question liée à l'intelligence artificielle, la finance, la santé ou l'impact des nouvelles technologies."
    ),
    tools=[synthese_tool],
)

def run_veille_agent(user_query: str) -> str:
    result = Runner.run_sync(veille_agent, user_query)
    return result.final_output