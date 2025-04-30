import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import uuid
import re
from typing import List, Dict
import json
import os
import time
import sqlite3
from sklearn.linear_model import LogisticRegression
import numpy as np
import plotly.express as px
from googletrans import Translator, LANGUAGES
import schedule
import threading

# Configuration des mots-clés et profils de veille
CONFIG = {
    "sectors": {
        "Santé": ["santé", "médical", "diagnostic", "soins", "hôpital", "patient", "télémédecine"],
        "Économie": ["économie", "croissance", "PIB", "emploi", "inflation", "commerce"],
        "Finances": ["finance", "banque", "investissement", "fraude", "crypto", "marché", "blockchain"]
    },
    "subjects": {
        "Agents Agentiques": ["agentique", "IA autonome", "agent intelligent", "automatisation"],
        "IA": ["intelligence artificielle", "machine learning", "deep learning", "LLM"],
        "Technologie": ["technologie", "innovation", "numérique", "cloud", "cybersécurité"]
    },
    "countries": {
        "Québec": ["Québec", "Montréal", "Québec City", "francophone"],
        "Canada": ["Canada", "Toronto", "Vancouver", "Ottawa"],
        "Europe": ["Europe", "France", "Allemagne", "Royaume-Uni", "UE"],
        "États-Unis": ["États-Unis", "USA", "Californie", "New York"]
    },
    "profiles": {
        "Startups IA Québec": ["startup", "IA", "Québec", "innovation"],
        "Réglementations UE Santé": ["réglementation", "santé", "Europe", "GDPR"],
        "Tendances Finances USA": ["finance", "IA", "États-Unis", "marché"]
    }
}

# Initialisation SQLite
def init_db():
    conn = sqlite3.connect('veille_cache.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id TEXT, query TEXT, timestamp TEXT, title TEXT, url TEXT, source TEXT, date TEXT, abstract TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Cache SQLite
def save_cache(data: List[Dict], query: str):
    conn = sqlite3.connect('veille_cache.db')
    c = conn.cursor()
    for item in data:
        c.execute('''INSERT INTO results (id, query, timestamp, title, url, source, date, abstract)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (str(uuid.uuid4()), query, datetime.now().isoformat(), item['title'], item['url'],
                   item['source'], item['date'], item.get('abstract', 'N/A')))
    conn.commit()
    conn.close()

def load_cache(query: str, max_age_hours: int = 24) -> List[Dict]:
    conn = sqlite3.connect('veille_cache.db')
    c = conn.cursor()
    c.execute('''SELECT title, url, source, date, abstract FROM results
                 WHERE query = ? AND timestamp > ?''',
              (query, (datetime.now() - timedelta(hours=max_age_hours)).isoformat()))
    results = [{"title": r[0], "url": r[1], "source": r[2], "date": r[3], "abstract": r[4]} for r in c.fetchall()]
    conn.close()
    return results

# Traduction avec googletrans
def translate_text(text: str, target_lang: str = 'en') -> str:
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        st.error(f"Erreur de traduction avec googletrans : {e}")
        return text

# Scraping arXiv
def fetch_arxiv(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    try:
        query = query.replace(' ', '+')
        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'xml')
        entries = soup.find_all('entry')
        for entry in entries:
            title = entry.find('title').text.strip()
            link = entry.find('id').text.strip()
            date = entry.find('published').text.strip()[:10]
            abstract = translate_text(entry.find('summary').text.strip(), target_lang='en')
            studies.append({
                'title': title,
                'url': link,
                'source': 'arXiv',
                'date': date,
                'abstract': abstract
            })
        time.sleep(1)
    except Exception as e:
        st.error(f"Erreur lors du scraping d'arXiv : {e}")
    return studies

# CORE API
def fetch_core(query: str, max_results: int = 3) -> List[Dict]:
    studies = []
    try:
        url = f"https://api.core.ac.uk/v3/search/works?q={query}&limit={max_results}"
        headers = {"Authorization": "Bearer YOUR_CORE_API_KEY"}  # Remplacer par votre clé
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for item in data.get('results', []):
            title = item.get('title', 'N/A')
            url = item.get('downloadUrl', '#')
            date = item.get('publishedDate', 'N/A')[:10]
            abstract = translate_text(item.get('abstract', 'N/A'), target_lang='en')
            studies.append({
                'title': title,
                'url': url,
                'source': 'CORE',
                'date': date,
                'abstract': abstract
            })
        time.sleep(1)
    except Exception as e:
        st.error(f"Erreur lors de l'appel à CORE API : {e}")
    return studies

# News
