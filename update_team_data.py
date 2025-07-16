#!/usr/bin/env python3
"""
Standalone-Skript zum manuellen oder geplanten Update der Teamdaten.
Kann über Cron/Task Scheduler täglich ausgeführt werden.

Verwendung:
- python update_team_data.py
- Kann in Windows Task Scheduler oder Linux Cron eingetragen werden
"""

import sys
import os
from datetime import datetime
from timezone_helper import get_german_now, format_german_datetime, convert_to_german_tz

# Team-Scraper Module importieren
try:
    import team_scraper
except ImportError:
    print("❌ team_scraper.py nicht gefunden!")
    print("Bitte sicherstellen, dass team_scraper.py im gleichen Verzeichnis liegt.")
    sys.exit(1)

def main():
    """Hauptfunktion für das Team-Daten Update"""
    print(f"🔄 Team-Daten Update gestartet - {format_german_datetime(get_german_now())}")
    print("=" * 60)
    
    # Aktuellen Cache-Status prüfen
    cache_info = team_scraper.get_cache_info()
    if cache_info:
        last_update = datetime.fromisoformat(cache_info['last_update'])
        last_update_german = convert_to_german_tz(last_update)
        age_hours = (get_german_now() - last_update_german).total_seconds() / 3600
        print(f"📋 Letzte Aktualisierung: {format_german_datetime(last_update_german)}")
        print(f"⏰ Alter der Daten: {age_hours:.1f} Stunden")
        
        if team_scraper.is_cache_valid():
            print("✅ Cache ist noch gültig (< 24 Stunden)")
            
            # Option für Force-Update
            if len(sys.argv) > 1 and sys.argv[1] == "--force":
                print("🔨 Force-Update angefordert...")
            else:
                print("💡 Verwende '--force' Parameter für Update trotz gültigem Cache")
                print("🔄 Update übersprungen")
                return
        else:
            print("⚠️ Cache ist veraltet (> 24 Stunden) - Update erforderlich")
    else:
        print("📭 Kein Cache vorhanden - Erstes Update")
    
    print("\n🌐 Starte Scraping von fussball.de...")
    
    # Scraping durchführen
    scraped_data = team_scraper.scrape_team_data()
    
    if scraped_data:
        print("✅ Scraping erfolgreich!")
        print(f"📊 Viktoria Buchholz Daten:")
        print(f"   - Platz: {scraped_data['platz']}")
        print(f"   - Punkte: {scraped_data['punkte']}")
        print(f"   - Tore: {scraped_data['tore_geschossen']}:{scraped_data['tore_erhalten']}")
        
        # CSV-Datei prüfen
        if os.path.exists(team_scraper.CSV_FILE):
            import pandas as pd
            try:
                df = pd.read_csv(team_scraper.CSV_FILE)
                print(f"📄 Tabelle gespeichert: {len(df)} Teams in {team_scraper.CSV_FILE}")
            except:
                print(f"⚠️ CSV-Datei erstellt, aber nicht lesbar: {team_scraper.CSV_FILE}")
        
        # Cache-Info ausgeben
        new_cache = team_scraper.get_cache_info()
        if new_cache:
            print(f"💾 Cache aktualisiert: {new_cache['last_update']}")
        
        print("\n🎉 Update erfolgreich abgeschlossen!")
        
    else:
        print("❌ Scraping fehlgeschlagen!")
        print("🔄 Versuche Fallback-Daten zu laden...")
        
        fallback_data = team_scraper.get_fallback_data()
        print(f"📋 Fallback-Daten geladen:")
        print(f"   - Platz: {fallback_data['platz']}")
        print(f"   - Punkte: {fallback_data['punkte']}")
        
        print("\n⚠️ Update mit Fallback-Daten abgeschlossen")
    
    print("=" * 60)
    print(f"🏁 Team-Daten Update beendet - {format_german_datetime(get_german_now())}")

def show_cache_info():
    """Zeigt detaillierte Cache-Informationen"""
    print("📋 Cache-Informationen:")
    print("=" * 40)
    
    cache_info = team_scraper.get_cache_info()
    if cache_info:
        print(f"📅 Letzte Aktualisierung: {cache_info['last_update']}")
        print(f"🏆 Teams in Tabelle: {cache_info.get('total_teams', '?')}")
        print(f"🌐 Datenquelle: {cache_info.get('source', '?')}")
        
        if 'viktoria_info' in cache_info:
            vinfo = cache_info['viktoria_info']
            print(f"\n⚽ Viktoria Buchholz:")
            print(f"   - Platz: {vinfo['platz']}")
            print(f"   - Punkte: {vinfo['punkte']}")
            print(f"   - Spiele: {vinfo['spiele']}")
            print(f"   - Tore: {vinfo['tore_geschossen']}:{vinfo['tore_erhalten']}")
        
        # Cache-Validität
        if team_scraper.is_cache_valid():
            print(f"\n✅ Cache ist gültig")
        else:
            print(f"\n⚠️ Cache ist veraltet")
    else:
        print("❌ Kein Cache vorhanden")
    
    # Datei-Info
    if os.path.exists(team_scraper.CACHE_FILE):
        size = os.path.getsize(team_scraper.CACHE_FILE)
        print(f"\n📄 Cache-Datei: {team_scraper.CACHE_FILE} ({size} Bytes)")
    
    if os.path.exists(team_scraper.CSV_FILE):
        size = os.path.getsize(team_scraper.CSV_FILE)
        print(f"📄 CSV-Datei: {team_scraper.CSV_FILE} ({size} Bytes)")

if __name__ == "__main__":
    # Kommandozeilen-Argumente verarbeiten
    if len(sys.argv) > 1:
        if sys.argv[1] == "--info":
            show_cache_info()
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("Team-Daten Update Skript")
            print("Verwendung:")
            print("  python update_team_data.py           # Normales Update")
            print("  python update_team_data.py --force   # Update erzwingen")
            print("  python update_team_data.py --info    # Cache-Info anzeigen")
            print("  python update_team_data.py --help    # Diese Hilfe")
            sys.exit(0)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Update durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        print("💡 Verwende '--info' um Cache-Status zu prüfen")
        sys.exit(1) 