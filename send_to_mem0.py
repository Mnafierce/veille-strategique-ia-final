import os
import requests

def send_to_mem0(content, topic):
    """
    Envoie un résumé vers Mem0 en tant que mémoire thématique.
    """
    api_key = os.getenv("MEM0_API_KEY")
    if not api_key:
        print("⚠️ Clé API Mem0 introuvable.")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": f"Résumé stratégique – {topic}",
        "content": content,
        "tags": ["veille", "ia", topic.lower()]
    }

    try:
        response = requests.post("https://api.mem0.ai/v1/memories", headers=headers, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Résumé envoyé à Mem0 : {topic}")
            return True
        else:
            print(f"❌ Erreur Mem0 : {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception Mem0 : {str(e)}")
        return False
