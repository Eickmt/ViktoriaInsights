import streamlit as st
from datetime import datetime
from database_helper import db
from scraper_service import scraper_service
from timezone_helper import get_german_now
from season_config import SEASON_DISPLAY, get_preseason_viktoria_info

# Fallback-Daten bis fussball.de die neue Saison ausliefert.
FALLBACK_DATA = get_preseason_viktoria_info()

@st.cache_data(ttl=3600)  # Cache für 1 Stunde (da DB bereits tägliches Update hat)
def get_team_data():
    """
    Hauptfunktion zum Abrufen der Teamdaten mit Supabase-Integration
    
    Returns:
        tuple: (viktoria_info: dict, data_source: str)
    """
    
    # 1. Versuche Daten aus Supabase zu laden
    viktoria_data = db.get_latest_viktoria_data()
    
    if viktoria_data:
        # Prüfe Aktualität der Daten
        is_current = db.is_standings_data_current()
        
        if is_current:
            return viktoria_data, "Supabase (aktuell)"
        else:
            last_update = db.get_standings_last_update()
            if last_update:
                hours_old = (get_german_now() - last_update).total_seconds() / 3600
                return viktoria_data, f"Supabase ({hours_old:.1f}h alt)"
            else:
                return viktoria_data, "Supabase (unbekanntes Alter)"
    
    # 2. Fallback: Versuche Live-Scraping (nur wenn keine DB-Daten vorhanden)
    try:
        success, message = scraper_service.update_standings_database()
        if success:
            viktoria_data = db.get_latest_viktoria_data()
            if viktoria_data:
                return viktoria_data, "Live Scraping"
    except Exception as e:
        print(f"Live-Scraping fehlgeschlagen: {e}")
    
    # 3. Letzter Fallback: Starttabelle der neuen Saison
    return FALLBACK_DATA, f"Starttabelle {SEASON_DISPLAY}"

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
    **Saison {SEASON_DISPLAY}**
    - Liga: Bezirksliga
    - Tabellenplatz: {viktoria_info['platz']}
    - Punkte: {viktoria_info['punkte']}
    - Torverhältnis: {tore_string}
    """
    
    return formatted_info

def get_data_status_info():
    """
    Gibt Informationen über den Status der Tabellendaten zurück
    
    Returns:
        dict: Status-Informationen
    """
    last_update = db.get_standings_last_update()
    is_current = db.is_standings_data_current()
    
    if last_update:
        hours_old = (get_german_now() - last_update).total_seconds() / 3600
        
        return {
            'last_update': last_update,
            'hours_old': hours_old,
            'is_current': is_current,
            'status_text': f"Letztes Update: {last_update.strftime('%d.%m.%Y %H:%M')} Uhr ({hours_old:.1f}h alt)"
        }
    else:
        return {
            'last_update': None,
            'hours_old': None,
            'is_current': False,
            'status_text': "Keine Daten verfügbar"
        }