#!/usr/bin/env python3
"""
ViktoriaInsights - Intelligenter Tabellen-Updater
Lädt nur bei Änderungen neue Daten und vermeidet Duplikate
"""

import sys
import logging
from datetime import datetime, timedelta
from scraper_service import scraper_service
from database_helper import db

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def should_update():
    """
    Intelligente Update-Logik:
    - Update nur wenn > 6 Stunden alt
    - Oder wenn es der erste Lauf des Tages ist
    """
    last_update = db.get_standings_last_update()
    
    if not last_update:
        logger.info("📊 Keine vorherigen Daten gefunden - Update erforderlich")
        return True
    
    now = datetime.now(last_update.tzinfo)
    hours_since_update = (now - last_update).total_seconds() / 3600
    
    # Update wenn älter als 6 Stunden
    if hours_since_update > 6:
        logger.info(f"📅 Letztes Update vor {hours_since_update:.1f}h - Update erforderlich")
        return True
    
    # Oder wenn heute noch kein Update
    if last_update.date() < now.date():
        logger.info(f"📅 Heute noch kein Update - Update erforderlich")
        return True
    
    logger.info(f"⏳ Letztes Update vor {hours_since_update:.1f}h - noch aktuell")
    return False

def get_current_viktoria_data():
    """Lädt aktuelle Viktoria-Daten zum Vergleich"""
    try:
        success, teams_data = scraper_service.scrape_current_standings()
        if not success:
            return None
            
        for team in teams_data:
            if 'viktoria buchholz' in team.get('team_name', '').lower():
                return team
        return None
    except Exception as e:
        logger.error(f"Fehler beim Laden aktueller Daten: {e}")
        return None

def has_data_changed():
    """Prüft ob sich die Tabellendaten geändert haben"""
    current_viktoria = get_current_viktoria_data()
    if not current_viktoria:
        logger.warning("⚠️ Aktuelle Viktoria-Daten nicht verfügbar")
        return True  # Bei Unsicherheit: Update durchführen
    
    last_viktoria = db.get_latest_viktoria_data()
    if not last_viktoria:
        logger.info("📊 Keine DB-Daten vorhanden - Update erforderlich")
        return True
    
    # Vergleiche wichtige Werte
    current_position = current_viktoria.get('position', 0)
    current_points = current_viktoria.get('points', 0)
    current_games = current_viktoria.get('games_played', 0)
    
    last_position = int(last_viktoria.get('platz', '0').replace('.', '') or 0)
    last_points = int(last_viktoria.get('punkte', '0') or 0)
    last_games = int(last_viktoria.get('spiele', '0') or 0)
    
    if (current_position != last_position or 
        current_points != last_points or 
        current_games != last_games):
        logger.info(f"📈 Datenänderung erkannt: Platz {last_position}→{current_position}, "
                   f"Punkte {last_points}→{current_points}, Spiele {last_games}→{current_games}")
        return True
    
    logger.info("📊 Keine Datenänderungen - Update übersprungen")
    return False

def main():
    """Hauptfunktion für intelligentes Update"""
    
    logger.info("🚀 ViktoriaInsights Intelligenter Tabellen-Update gestartet")
    
    try:
        # 1. Zeitbasierte Prüfung
        if not should_update():
            logger.info("✅ Update übersprungen - zu früh für neues Update")
            return
        
        # 2. Datenbasierte Prüfung
        if not has_data_changed():
            logger.info("✅ Update übersprungen - keine Änderungen")
            return
        
        # 3. Update durchführen
        logger.info("📱 Führe Tabellen-Update durch...")
        success, message = scraper_service.update_standings_database()
        
        if success:
            logger.info(f"✅ {message}")
            
            # Viktoria-Daten zur Bestätigung laden
            viktoria_data = db.get_latest_viktoria_data()
            if viktoria_data:
                logger.info(f"🏆 TuS Viktoria Buchholz: Platz {viktoria_data['platz']}, {viktoria_data['punkte']} Punkte")
            
        else:
            logger.error(f"❌ {message}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {str(e)}")
        sys.exit(1)
    
    logger.info("🎉 Intelligenter Tabellen-Update erfolgreich abgeschlossen")

if __name__ == "__main__":
    main()