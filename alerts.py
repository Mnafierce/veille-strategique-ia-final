import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

# Configuration d'accès
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_keyfile = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "gcp_credentials.json")  # ou chemin relatif
spreadsheet_url = os.getenv("GOOGLE_SHEETS_URL")

def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client

def save_alert_to_sheet(keyword, alert_type, detail, source_link):
    try:
        client = get_gsheet_client()
        sheet = client.open_by_url(spreadsheet_url).sheet1

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [now, keyword, alert_type, detail, source_link]
        sheet.append_row(row)
        print(f"✅ Alerte ajoutée : {row}")
    except Exception as e:
        print(f"❌ Erreur lors de l’ajout dans Google Sheets : {e}")
