#!/usr/bin/env python3
"""
ViktoriaInsights - Automatisches Datenbank-Backup
Erstellt Excel-Dateien aller wichtigen Tabellen aus der Supabase-Datenbank
"""

import os
import sys
import pandas as pd
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_backup():
    """Erstellt Backup aller wichtigen Datenbank-Tabellen als Excel-Dateien"""
    
    try:
        # Supabase importieren
        from supabase import create_client, Client
        logger.info("📦 Supabase-Client erfolgreich importiert")
        
    except ImportError as e:
        logger.error("❌ Fehler beim Importieren von Supabase:")
        logger.error(f"   {e}")
        logger.error("   Installieren Sie: pip install supabase")
        sys.exit(1)
    
    # Umgebungsvariablen prüfen
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Fehler: Supabase-Credentials nicht gefunden!")
        logger.error("   Setzen Sie die Umgebungsvariablen:")
        logger.error("   - SUPABASE_URL")
        logger.error("   - SUPABASE_ANON_KEY")
        sys.exit(1)
    
    logger.info("🔑 Supabase-Credentials gefunden")
    
    try:
        # Mit Supabase verbinden
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("🔗 Erfolgreich mit Supabase verbunden")
        
        # Timestamp für Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"📅 Backup-Timestamp: {timestamp}")
        
        # Liste der wichtigen Tabellen
        tabellen = [
            "dim_player",           # Spielerdaten
            "dim_penalty_type",     # Strafenkatalog
            "fact_penalty",         # Strafen
            "fact_training_win",    # Trainingssiege
            "dim_training_presence" # Trainingsanwesenheit (falls vorhanden)
        ]
        
        backup_count = 0
        
        for tabelle in tabellen:
            try:
                logger.info(f"📊 Lade Tabelle: {tabelle}")
                
                # Daten aus Tabelle abrufen
                response = supabase.table(tabelle).select("*").execute()
                
                if response.data:
                    # DataFrame erstellen
                    df = pd.DataFrame(response.data)
                    
                    # Excel-Datei speichern
                    dateiname = f"backup_{tabelle}_{timestamp}.xlsx"
                    df.to_excel(dateiname, index=False, engine='openpyxl')
                    
                    anzahl_zeilen = len(df)
                    logger.info(f"✅ {tabelle}: {anzahl_zeilen} Datensätze → {dateiname}")
                    backup_count += 1
                    
                else:
                    logger.warning(f"⚠️  {tabelle}: Keine Daten gefunden")
                    
            except Exception as e:
                logger.error(f"❌ Fehler bei Tabelle {tabelle}:")
                logger.error(f"   {e}")
                # Weiter mit nächster Tabelle
                continue
        
        # Zusammenfassung
        logger.info(f"🎉 Backup abgeschlossen!")
        logger.info(f"   📁 {backup_count} Tabellen gesichert")
        logger.info(f"   🕐 Timestamp: {timestamp}")
        
        # Backup-Übersicht erstellen
        erstelle_backup_uebersicht(timestamp, backup_count)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Backup:")
        logger.error(f"   {e}")
        sys.exit(1)


def erstelle_backup_uebersicht(timestamp, anzahl_tabellen):
    """Erstellt eine Übersichtsdatei über das Backup"""
    
    uebersicht = f"""
# ViktoriaInsights Backup-Übersicht

## Backup-Details
- **Datum/Zeit**: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S Uhr')}
- **Timestamp**: {timestamp}
- **Anzahl Tabellen**: {anzahl_tabellen}

## Gesicherte Dateien:
- backup_dim_player_{timestamp}.xlsx
- backup_dim_penalty_type_{timestamp}.xlsx  
- backup_fact_penalty_{timestamp}.xlsx
- backup_fact_training_win_{timestamp}.xlsx
- backup_dim_training_presence_{timestamp}.xlsx (falls vorhanden)

## Wiederherstellung:
1. Excel-Dateien herunterladen
2. In Supabase Dashboard gehen
3. Table Editor → Import
4. Excel-Datei auswählen und importieren

## Automatisches Backup:
Dieses Backup wurde automatisch durch GitHub Actions erstellt.
Nächstes Backup: Morgen um 02:00 Uhr
"""
    
    with open(f"backup_uebersicht_{timestamp}.md", 'w', encoding='utf-8') as f:
        f.write(uebersicht)
    
    logger.info(f"📋 Backup-Übersicht erstellt: backup_uebersicht_{timestamp}.md")


if __name__ == "__main__":
    logger.info("🛡️  ViktoriaInsights Backup gestartet")
    logger.info("=" * 50)
    
    success = create_backup()
    
    if success:
        logger.info("=" * 50)
        logger.info("🎉 Backup erfolgreich abgeschlossen!")
    else:
        logger.error("💥 Backup fehlgeschlagen!")
        sys.exit(1) 