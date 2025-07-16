import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime, timedelta
import os
import json
from timezone_helper import get_german_now, convert_to_german_tz

# Team-ID für TuS Viktoria Buchholz
TEAM_ID = "011MI9UHGG000000VTVG0001VTR8C1K7"
SAISON = "2425"  # Saison 2024/25
CACHE_FILE = "team_data_cache.json"
CSV_FILE = "bezirksliga_tabelle.csv"

# User-Agent Header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_table_data(soup):
    """Extrahiert Tabellendaten aus HTML mit BeautifulSoup"""
    table = soup.find('table')
    if not table:
        return []
    
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        if cells:  # Nur nicht-leere Zeilen
            rows.append(cells)
    
    return rows

def get_cache_info():
    """Lädt Cache-Informationen"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_cache_info(data):
    """Speichert Cache-Informationen"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def is_cache_valid():
    """Prüft ob der Cache noch gültig ist (weniger als 24 Stunden alt)"""
    cache_info = get_cache_info()
    if not cache_info:
        return False
    
    try:
        last_update = datetime.fromisoformat(cache_info['last_update'])
        last_update_german = convert_to_german_tz(last_update)
        now = get_german_now()
        return (now - last_update_german).total_seconds() < 86400  # 24 Stunden
    except:
        return False

def scrape_team_data():
    """Scraped aktuelle Teamdaten von fussball.de"""
    try:
        # Staffel-Tabelle laden
        url_table = f"https://www.fussball.de/ajax.team.table/-/saison/{SAISON}/team-id/{TEAM_ID}"
        response = requests.get(url_table, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table_data = extract_table_data(soup)
            
            if table_data:
                # Header finden
                header = None
                data_rows = []
                
                for i, row in enumerate(table_data):
                    # Suche nach Zeile mit typischen Tabellen-Spalten
                    if any(keyword in str(row).lower() for keyword in ['platz', 'verein', 'team', 'pkt', 'punkte']):
                        header = row
                        data_rows = table_data[i+1:]
                        break
                
                if not header and table_data:
                    # Fallback: Erste Zeile als Header
                    header = table_data[0]
                    data_rows = table_data[1:]
                
                if data_rows:
                    # DataFrame erstellen
                    max_cols = max(len(row) for row in [header] + data_rows) if header else max(len(row) for row in data_rows)
                    
                    # Zeilen auf gleiche Länge bringen
                    if header:
                        while len(header) < max_cols:
                            header.append(f"Spalte_{len(header)+1}")
                    else:
                        header = [f"Spalte_{i+1}" for i in range(max_cols)]
                    
                    for row in data_rows:
                        while len(row) < max_cols:
                            row.append("")
                    
                    df_table = pd.DataFrame(data_rows, columns=header[:max_cols])
                    
                    # CSV speichern
                    df_table.to_csv(CSV_FILE, index=False, encoding='utf-8')
                    
                    # Viktoria Buchholz Position finden
                    viktoria_info = extract_viktoria_info(df_table)
                    
                    # Cache-Info speichern
                    cache_data = {
                        'last_update': get_german_now().isoformat(),
                        'viktoria_info': viktoria_info,
                        'total_teams': len(df_table),
                        'source': 'fussball.de'
                    }
                    save_cache_info(cache_data)
                    
                    return viktoria_info
        
        return None
        
    except Exception as e:
        print(f"Scraping-Fehler: {e}")
        return None

def extract_viktoria_info(df_table):
    """Extrahiert spezifische Informationen zu Viktoria Buchholz"""
    viktoria_info = {
        'platz': '?',
        'punkte': '?',
        'spiele': '?',
        'siege': '?',
        'unentschieden': '?',
        'niederlagen': '?',
        'tore_geschossen': '?',
        'tore_erhalten': '?',
        'tordifferenz': '?'
    }
    
    try:
        for idx, row in df_table.iterrows():
            row_str = str(row).lower()
            if 'viktoria buchholz' in row_str or 'buchholz' in row_str:
                # Versuche typische Spalten zu identifizieren
                row_values = [str(val).strip() for val in row.values if str(val).strip()]
                
                # Struktur nach Filtern:
                # ['8.', 'TuS Viktoria Buchholz', '31', '12', '8', '11', '61 : 62', '-1', '44']
                # Index: 0      1                  2     3     4    5     6          7     8
                
                if len(row_values) >= 8:  # Mindestens 8 Elemente erwartet
                    try:
                        # Platz (Index 0): "8."
                        viktoria_info['platz'] = row_values[0] if len(row_values) > 0 else '?'
                        
                        # Spiele (Index 2): "31" 
                        viktoria_info['spiele'] = row_values[2] if len(row_values) > 2 and row_values[2].isdigit() else '?'
                        
                        # Siege (Index 3): "12"
                        viktoria_info['siege'] = row_values[3] if len(row_values) > 3 and row_values[3].isdigit() else '?'
                        
                        # Unentschieden (Index 4): "8"
                        viktoria_info['unentschieden'] = row_values[4] if len(row_values) > 4 and row_values[4].isdigit() else '?'
                        
                        # Niederlagen (Index 5): "11"
                        viktoria_info['niederlagen'] = row_values[5] if len(row_values) > 5 and row_values[5].isdigit() else '?'
                        
                        # Torverhältnis (Index 6): "61 : 62"
                        if len(row_values) > 6 and ':' in row_values[6]:
                            tore_parts = row_values[6].split(':')
                            if len(tore_parts) == 2:
                                viktoria_info['tore_geschossen'] = tore_parts[0].strip()
                                viktoria_info['tore_erhalten'] = tore_parts[1].strip()
                        
                        # Tordifferenz (Index 7): "-1"
                        viktoria_info['tordifferenz'] = row_values[7] if len(row_values) > 7 else '?'
                        
                        # Punkte (Index 8): "44" - Das ist der wichtigste Wert!
                        viktoria_info['punkte'] = row_values[8] if len(row_values) > 8 and row_values[8].isdigit() else '?'
                        
                    except Exception as e:
                        print(f"Fehler beim Parsen der Viktoria-Zeile: {e}")
                
                break
        
        return viktoria_info
        
    except Exception as e:
        print(f"Fehler beim Extrahieren der Viktoria-Info: {e}")
        return viktoria_info

def get_fallback_data():
    """Lädt Fallback-Daten aus Cache oder Standard-Werte"""
    cache_info = get_cache_info()
    if cache_info and 'viktoria_info' in cache_info:
        return cache_info['viktoria_info']
    
    # Standard-Fallback-Werte basierend auf aktueller CSV
    return {
        'platz': '8.',
        'punkte': '44',
        'spiele': '31',
        'siege': '12',
        'unentschieden': '8',
        'niederlagen': '11',
        'tore_geschossen': '61',
        'tore_erhalten': '62',
        'tordifferenz': '-1'
    }

@st.cache_data(ttl=86400)  # Cache für 24 Stunden
def get_team_data():
    """Hauptfunktion zum Abrufen der Teamdaten mit intelligentem Caching"""
    
    # Prüfe ob gültiger Cache vorhanden ist
    if is_cache_valid():
        cache_info = get_cache_info()
        if cache_info and 'viktoria_info' in cache_info:
            return cache_info['viktoria_info'], "Cache"
    
    # Versuche neue Daten zu scrapen
    scraped_data = scrape_team_data()
    if scraped_data:
        return scraped_data, "Live Scraping"
    
    # Fallback auf letzte bekannte oder Standard-Daten
    fallback_data = get_fallback_data()
    return fallback_data, "Fallback"

def format_team_info(viktoria_info, data_source):
    """Formatiert die Teaminfos für die Anzeige"""
    
    # Berechne Torverhältnis
    tore_string = "?"
    if (viktoria_info['tore_geschossen'] != '?' and 
        viktoria_info['tore_erhalten'] != '?' and
        viktoria_info['tore_geschossen'] != '' and 
        viktoria_info['tore_erhalten'] != ''):
        tore_string = f"{viktoria_info['tore_geschossen']}:{viktoria_info['tore_erhalten']}"
    
    formatted_info = f"""
    **Saison 2024/25**
    - Liga: Bezirksliga
    - Tabellenplatz: {viktoria_info['platz']}
    - Punkte: {viktoria_info['punkte']}
    - Torverhältnis: {tore_string}
    """
    
    return formatted_info 