#!/usr/bin/env python3
"""
Test-Script für das neue Scraping-System
Testet alle Komponenten ohne Streamlit-Abhängigkeit
"""

import sys
import os

def test_imports():
    """Teste alle wichtigen Imports"""
    print("🔍 Teste Imports...")
    
    try:
        import requests
        print("✅ requests verfügbar")
    except ImportError:
        print("❌ requests fehlt: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup verfügbar")
    except ImportError:
        print("❌ BeautifulSoup fehlt: pip install beautifulsoup4")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas verfügbar")
    except ImportError:
        print("❌ pandas fehlt: pip install pandas")
        return False
    
    try:
        from timezone_helper import get_german_now
        print("✅ timezone_helper verfügbar")
    except ImportError:
        print("❌ timezone_helper.py fehlt oder defekt")
        return False
    
    return True

def test_scraping_only():
    """Teste nur das Scraping ohne Datenbank"""
    print("\n🕷️ Teste Web-Scraping...")
    
    try:
        # Direkt importieren ohne database_helper
        import requests
        from bs4 import BeautifulSoup
        
        # Team-ID für TuS Viktoria Buchholz
        TEAM_ID = "011MI9UHGG000000VTVG0001VTR8C1K7"
        SAISON = "2425"
        
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        url_table = f"https://www.fussball.de/ajax.team.table/-/saison/{SAISON}/team-id/{TEAM_ID}"
        print(f"📡 Teste URL: {url_table}")
        
        response = requests.get(url_table, headers=HEADERS, timeout=10)
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')
                print(f"✅ Tabelle gefunden mit {len(rows)} Zeilen")
                
                # Suche nach Viktoria Buchholz
                viktoria_found = False
                for row in rows:
                    row_text = row.get_text().lower()
                    if 'viktoria buchholz' in row_text or 'buchholz' in row_text:
                        print(f"🏆 Viktoria Buchholz gefunden: {row.get_text().strip()}")
                        viktoria_found = True
                        break
                
                if not viktoria_found:
                    print("⚠️ Viktoria Buchholz nicht in Tabelle gefunden")
                
                return True
            else:
                print("❌ Keine Tabelle im HTML gefunden")
                return False
        else:
            print(f"❌ HTTP-Fehler: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Scraping-Fehler: {e}")
        return False

def test_database_connection():
    """Teste Datenbankverbindung mit derselben Logik wie database_helper.py"""
    print("\n🗄️ Teste Datenbankverbindung...")
    
    try:
        # Versuche Supabase zu importieren
        from supabase import create_client, Client
        print("✅ Supabase-Client verfügbar")
        
        # Lade Credentials mit derselben Logik wie database_helper.py
        supabase_url = None
        supabase_key = None
        
        # 1. Versuche Umgebungsvariablen
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if supabase_url and supabase_key:
            print("✅ Supabase-Credentials in Umgebungsvariablen gefunden")
        else:
            # 2. Versuche Streamlit Secrets (falls verfügbar)
            try:
                import streamlit as st
                if not supabase_url:
                    supabase_url = (
                        st.secrets.get("SUPABASE_URL") or
                        st.secrets.get("supabase", {}).get("SUPABASE_URL")
                    )
                if not supabase_key:
                    supabase_key = (
                        st.secrets.get("SUPABASE_ANON_KEY") or
                        st.secrets.get("supabase", {}).get("SUPABASE_ANON_KEY")
                    )
                
                if supabase_url and supabase_key:
                    print("✅ Supabase-Credentials in Streamlit Secrets gefunden")
                    
            except ImportError:
                print("⚠️ Streamlit nicht verfügbar für Secrets-Test")
            except Exception as e:
                print(f"⚠️ Streamlit Secrets nicht zugänglich: {e}")
        
        if supabase_url and supabase_key:
            try:
                supabase = create_client(supabase_url, supabase_key)
                print("✅ Supabase-Client erfolgreich erstellt")
                
                # Teste einfache Abfrage auf team_standings Tabelle
                response = supabase.table('team_standings').select('*').limit(1).execute()
                print(f"✅ Datenbankverbindung erfolgreich")
                print(f"📊 team_standings Tabelle: {len(response.data)} Datensätze gefunden")
                return True
                
            except Exception as e:
                print(f"❌ Datenbankverbindungsfehler: {e}")
                return False
        else:
            print("❌ Keine Supabase-Credentials gefunden")
            print("   Prüfe: SUPABASE_URL und SUPABASE_ANON_KEY")
            return False
            
    except ImportError:
        print("❌ Supabase-Client fehlt: pip install supabase")
        return False

def test_database_helper():
    """Teste die DatabaseHelper-Klasse direkt"""
    print("\n🔧 Teste DatabaseHelper-Klasse...")
    
    try:
        from database_helper import db
        print("✅ DatabaseHelper importiert")
        
        # Teste Verbindung
        db._ensure_connected()
        
        if db.connected:
            print("✅ DatabaseHelper erfolgreich verbunden")
            
            # Teste team_standings Methoden
            try:
                is_current = db.is_standings_data_current()
                print(f"📊 Daten-Aktualität: {'Aktuell' if is_current else 'Veraltet/Keine Daten'}")
                
                last_update = db.get_standings_last_update()
                if last_update:
                    print(f"🕒 Letztes Update: {last_update.strftime('%d.%m.%Y %H:%M')} Uhr")
                else:
                    print("🕒 Letztes Update: Keine Daten vorhanden")
                
                viktoria_data = db.get_latest_viktoria_data()
                if viktoria_data:
                    print(f"🏆 Viktoria-Daten gefunden: Platz {viktoria_data['platz']}, {viktoria_data['punkte']} Punkte")
                else:
                    print("🏆 Keine Viktoria-Daten in Datenbank")
                
                return True
                
            except Exception as e:
                print(f"❌ Fehler bei DatabaseHelper-Methoden: {e}")
                return False
        else:
            print("❌ DatabaseHelper konnte keine Verbindung herstellen")
            return False
            
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ DatabaseHelper-Fehler: {e}")
        return False

def main():
    """Haupttest-Funktion"""
    print("🚀 ViktoriaInsights - System-Test")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import-Test fehlgeschlagen!")
        sys.exit(1)
    
    # Test 2: Web-Scraping
    if not test_scraping_only():
        print("\n❌ Scraping-Test fehlgeschlagen!")
        sys.exit(1)
    
    # Test 3: Datenbank (optional)
    db_success = test_database_connection()
    
    # Test 4: DatabaseHelper (detailliert)
    db_helper_success = test_database_helper()
    
    print("\n" + "=" * 50)
    print("📋 Test-Zusammenfassung:")
    print("✅ Imports: Erfolgreich")
    print("✅ Web-Scraping: Erfolgreich")
    print(f"{'✅' if db_success else '⚠️'} Datenbank-Verbindung: {'Erfolgreich' if db_success else 'Nicht verfügbar'}")
    print(f"{'✅' if db_helper_success else '⚠️'} DatabaseHelper: {'Erfolgreich' if db_helper_success else 'Nicht verfügbar'}")
    
    if db_success and db_helper_success:
        print("\n🎉 Alle Tests erfolgreich! System ist bereit.")
    elif db_helper_success:
        print("\n✅ DatabaseHelper funktioniert! Das System sollte einsatzbereit sein.")
    else:
        print("\n⚠️ Scraping funktioniert, aber Datenbank nicht verfügbar.")
        print("   Für Vollbetrieb: Supabase-Credentials konfigurieren")

if __name__ == "__main__":
    main()