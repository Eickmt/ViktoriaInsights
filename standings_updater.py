#!/usr/bin/env python3
"""
ViktoriaInsights - Tabellen-Updater
Lädt aktuelle Tabellendaten und speichert sie in Supabase
"""

import sys
import logging
from datetime import datetime
from scraper_service import scraper_service
from database_helper import db

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für das geplante Tabellen-Update"""
    
    logger.info("🚀 ViktoriaInsights Tabellen-Update gestartet")
    
    try:
        # Prüfen ob Update notwendig ist
        is_current = db.is_standings_data_current()
        
        if is_current:
            last_update = db.get_standings_last_update()
            logger.info(f"📊 Tabellendaten sind aktuell (letztes Update: {last_update})")
            logger.info("✅ Kein Update erforderlich")
            return
        
        logger.info("📱 Lade aktuelle Tabellendaten...")
        
        # Daten aktualisieren
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
    
    logger.info("🎉 Tabellen-Update erfolgreich abgeschlossen")

if __name__ == "__main__":
    main()