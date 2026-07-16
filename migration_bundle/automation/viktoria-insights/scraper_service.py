import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from timezone_helper import get_german_now
from database_helper import db

# Team-ID für TuS Viktoria Buchholz
TEAM_ID = "011MI9UHGG000000VTVG0001VTR8C1K7"
SAISON = "2526"  # Saison 2025/26

# User-Agent Header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class TeamScraperService:
    """Service-Klasse für das Scraping von Teamdaten von fussball.de"""
    
    def __init__(self):
        self.team_id = TEAM_ID
        self.season = SAISON
        
    def extract_table_data(self, soup):
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
    
    def parse_team_data(self, table_data):
        """
        Parst die Tabellendaten und konvertiert sie in ein standardisiertes Format
        
        Returns:
            list: Liste von Dictionaries mit Teamdaten
        """
        if not table_data:
            return []
        
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
        
        if not data_rows:
            return []
        
        # Standardisierte Teamdaten erstellen
        teams_data = []
        
        for row_values in data_rows:
            # Leere Zeilen überspringen
            if not any(str(val).strip() for val in row_values):
                continue
                
            row_values = [str(val).strip() for val in row_values if str(val).strip()]
            
            if len(row_values) >= 8:  # Mindestens 8 Elemente erwartet
                try:
                    # Struktur: ['8.', 'TuS Viktoria Buchholz', '31', '12', '8', '11', '61 : 62', '-1', '44']
                    team_data = {
                        'position': int(row_values[0].replace('.', '')) if row_values[0].replace('.', '').isdigit() else 0,
                        'team_name': row_values[1] if len(row_values) > 1 else '',
                        'games_played': int(row_values[2]) if len(row_values) > 2 and row_values[2].isdigit() else 0,
                        'wins': int(row_values[3]) if len(row_values) > 3 and row_values[3].isdigit() else 0,
                        'draws': int(row_values[4]) if len(row_values) > 4 and row_values[4].isdigit() else 0,
                        'losses': int(row_values[5]) if len(row_values) > 5 and row_values[5].isdigit() else 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'goal_difference': int(row_values[7]) if len(row_values) > 7 and row_values[7].lstrip('-').isdigit() else 0,
                        'points': int(row_values[8]) if len(row_values) > 8 and row_values[8].isdigit() else 0,
                        'match_day': None  # Kann später hinzugefügt werden
                    }
                    
                    # Torverhältnis parsen (Index 6): "61 : 62"
                    if len(row_values) > 6 and ':' in row_values[6]:
                        tore_parts = row_values[6].split(':')
                        if len(tore_parts) == 2:
                            try:
                                team_data['goals_for'] = int(tore_parts[0].strip())
                                team_data['goals_against'] = int(tore_parts[1].strip())
                            except ValueError:
                                pass
                    
                    teams_data.append(team_data)
                    
                except (ValueError, IndexError) as e:
                    print(f"Fehler beim Parsen der Zeile {row_values}: {e}")
                    continue
        
        return teams_data
    
    def scrape_current_standings(self):
        """
        Scraped aktuelle Tabellendaten von fussball.de
        
        Returns:
            tuple: (success: bool, data: list oder error_message: str)
        """
        try:
            # Staffel-Tabelle laden
            url_table = f"https://www.fussball.de/ajax.team.table/-/saison/{self.season}/team-id/{self.team_id}"
            response = requests.get(url_table, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table_data = self.extract_table_data(soup)
                
                if table_data:
                    teams_data = self.parse_team_data(table_data)
                    
                    if teams_data:
                        return True, teams_data
                    else:
                        return False, "Keine gültigen Teamdaten gefunden"
                else:
                    return False, "Keine Tabellendaten im HTML gefunden"
            else:
                return False, f"HTTP-Fehler: {response.status_code}"
                
        except Exception as e:
            return False, f"Scraping-Fehler: {str(e)}"
    
    def update_standings_database(self):
        """
        Lädt aktuelle Daten und speichert sie in der Datenbank
        
        Returns:
            tuple: (success: bool, message: str)
        """
        success, data = self.scrape_current_standings()
        
        if not success:
            return False, f"Scraping fehlgeschlagen: {data}"
        
        # In Datenbank speichern
        db_success, db_message = db.save_team_standings(data, self.season)
        
        if db_success:
            return True, f"✅ Tabelle erfolgreich aktualisiert: {db_message}"
        else:
            return False, f"❌ Datenbankfehler: {db_message}"

# Globale Instanz
scraper_service = TeamScraperService()