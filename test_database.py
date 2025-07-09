#!/usr/bin/env python3
"""
Einfaches Test-Skript für Supabase Datenbankverbindung
Testet das Laden der Geburtstage aus der Datenbank
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

def load_env_variables():
    """Lade Umgebungsvariablen aus verschiedenen Quellen"""
    # 1. .env Datei laden
    load_dotenv(override=True)
    
    # 2. Streamlit secrets.toml versuchen (falls vorhanden)
    secrets_file = ".streamlit/secrets.toml"
    if os.path.exists(secrets_file):
        try:
            import toml
            secrets = toml.load(secrets_file)
            
            # Prüfe verschiedene Strukturen
            if 'supabase' in secrets:
                # [supabase] Sektion
                os.environ.setdefault('SUPABASE_URL', secrets['supabase'].get('SUPABASE_URL', ''))
                os.environ.setdefault('SUPABASE_ANON_KEY', secrets['supabase'].get('SUPABASE_ANON_KEY', ''))
            else:
                # Root-Level
                os.environ.setdefault('SUPABASE_URL', secrets.get('SUPABASE_URL', ''))
                os.environ.setdefault('SUPABASE_ANON_KEY', secrets.get('SUPABASE_ANON_KEY', ''))
        except ImportError:
            print("⚠️ 'toml' Paket nicht installiert - überspringe secrets.toml")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden von secrets.toml: {e}")

def test_connection():
    """Teste die Datenbankverbindung"""
    print("🔍 Teste Supabase-Verbindung...")
    
    # Umgebungsvariablen laden
    load_env_variables()
    
    # Supabase-Konfiguration
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"📊 Konfiguration:")
    print(f"   SUPABASE_URL: {'✅ vorhanden' if url else '❌ fehlt'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ vorhanden' if key else '❌ fehlt'}")
    
    if not url or not key:
        print("❌ Supabase-Konfiguration unvollständig!")
        return None
    
    try:
        # Supabase-Client erstellen
        supabase: Client = create_client(url, key)
        print("✅ Supabase-Client erfolgreich erstellt")
        return supabase
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Supabase-Clients: {e}")
        return None

def get_available_tables(supabase):
    """Prüfe verfügbare Tabellen"""
    print("\n🔍 Prüfe verfügbare Tabellen...")
    
    # Liste der Tabellen die wir suchen
    test_tables = ['Geburtstage', 'geburtstage', 'birthdays', 'strafen', 'Strafen', 'penalties']
    
    available_tables = []
    for table_name in test_tables:
        try:
            print(f"   🔍 Teste Tabelle '{table_name}'...")
            response = supabase.table(table_name).select('*').limit(1).execute()
            print(f"   📊 Response für '{table_name}': {response}")
            
            if response.data is not None:
                available_tables.append(table_name)
                print(f"   ✅ Tabelle '{table_name}' gefunden - {len(response.data)} Zeilen")
            else:
                print(f"   ⚠️ Tabelle '{table_name}' - response.data ist None")
                
        except Exception as e:
            print(f"   ❌ Tabelle '{table_name}' nicht verfügbar:")
            print(f"      Fehler-Typ: {type(e).__name__}")
            print(f"      Fehler-Details: {str(e)}")
    
    return available_tables

def test_birthdays(supabase):
    """Teste das Laden der Geburtstage"""
    print("\n🎂 Teste Geburtstage-Abfrage...")
    
    # Verschiedene Tabellennamen probieren
    table_variants = ['Geburtstage', 'geburtstage', 'birthdays']
    
    for table_name in table_variants:
        try:
            print(f"   🔍 Versuche Tabelle '{table_name}'...")
            
            # Alle Geburtstage abrufen
            response = supabase.table(table_name).select('*').execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                print(f"   ✅ Erfolgreich! {len(df)} Einträge gefunden")
                print(f"   📊 Spalten: {list(df.columns)}")
                
                # Erste 3 Einträge anzeigen
                if len(df) > 0:
                    print("   📋 Erste Einträge:")
                    for i, row in df.head(3).iterrows():
                        print(f"      {i+1}. {dict(row)}")
                
                return df
            else:
                print(f"   ⚠️ Tabelle '{table_name}' ist leer")
                
        except Exception as e:
            print(f"   ❌ Fehler bei Tabelle '{table_name}': {e}")
    
    print("   ❌ Keine Geburtstage-Tabelle gefunden!")
    return None

def test_simple_query(supabase):
    """Teste einfache Abfrage mit spezifischen Spalten"""
    print("\n🧪 Teste einfache Abfrage...")
    
    # Teste verschiedene Spalten-Kombinationen
    test_cases = [
        # Fall 1: Alle Spalten
        ("Geburtstage", "*"),
        # Fall 2: Nur spezifische Spalten
        ("Geburtstage", "Name, Geburtstag"), 
        ("Geburtstage", "Name"),
        ("Geburtstage", "Geburtstag"),
        # Fall 3: Count
        ("Geburtstage", "count")
    ]
    
    for table_name, select_clause in test_cases:
        try:
            print(f"   🔍 Teste: SELECT {select_clause} FROM {table_name}")
            
            if select_clause == "count":
                response = supabase.table(table_name).select("*", count="exact").execute()
                print(f"   📊 Count Response: {response.count}")
            else:
                response = supabase.table(table_name).select(select_clause).limit(1).execute()
                print(f"   📊 Response: {response}")
                
                if response.data:
                    print(f"   ✅ Erfolgreich! Daten: {response.data}")
                else:
                    print(f"   ⚠️ Keine Daten zurückgegeben")
                    
        except Exception as e:
            print(f"   ❌ Fehler bei SELECT {select_clause}:")
            print(f"      {type(e).__name__}: {str(e)}")

def main():
    """Hauptfunktion"""
    print("🚀 Supabase-Datenbanktest")
    print("=" * 50)
    
    # 1. Verbindung testen
    supabase = test_connection()
    if not supabase:
        return
    
    # 2. Verfügbare Tabellen prüfen
    available_tables = get_available_tables(supabase)
    
    # 2.5. Einfache Abfrage testen
    test_simple_query(supabase)
    
    if not available_tables:
        print("\n❌ Keine Tabellen gefunden!")
        return
    
    # 3. Geburtstage testen
    birthdays_df = test_birthdays(supabase)
    
    if birthdays_df is not None:
        print(f"\n✅ Test erfolgreich! {len(birthdays_df)} Geburtstage geladen")
    else:
        print(f"\n❌ Test fehlgeschlagen!")
    
    print("\n" + "=" * 50)
    print("🏁 Test beendet")

if __name__ == "__main__":
    main() 