import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Connexion à Google Sheets
def connect_to_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

# Évaluation des alertes stratégiques
def trigger_alerts(articles, keywords):
    alerts = []
    for article in articles:
        for keyword in keywords:
            if keyword.lower() in article["title"].lower() or keyword.lower() in article["snippet"].lower():
                alerts.append({
                    "keyword": keyword,
                    "title": article["title"],
                    "link": article["link"],
                    "snippet": article["snippet"],
                    "timestamp": datetime.now().isoformat()
                })
    return alerts

# Enregistrement dans Google Sheets
def save_alert_to_sheet(alerts, sheet_name="Veille_IA_Alertes"):
    try:
        sheet = connect_to_sheet(sheet_name)
        for alert in alerts:
            sheet.append_row([
                alert["timestamp"],
                alert["keyword"],
                alert["title"],
                alert["link"],
                alert["snippet"][:150]  # tronquer le texte si trop long
            ])
    except Exception as e:
        print(f"Erreur lors de l'écriture dans Google Sheets : {e}")
