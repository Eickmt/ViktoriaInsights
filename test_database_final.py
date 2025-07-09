#!/usr/bin/env python3
"""
Finaler Test für alle Supabase-Tabellen mit dem aktualisierten database_helper
"""

from database_helper import db
import pandas as pd

def test_all_tables():
    """Teste alle drei Haupttabellen"""
    print("🚀 Finaler Datenbanktest")
    print("=" * 50)
    
    # 1. Verbindungsinfo
    conn_info = db.get_connection_info()
    print("🔍 Verbindungsinfo:")
    for key, value in conn_info.items():
        print(f"   {key}: {value}")
    
    # 2. Geburtstage testen
    print("\n🎂 Teste Geburtstage:")
    try:
        birthdays = db.get_birthdays()
        if birthdays is not None and len(birthdays) > 0:
            print(f"   ✅ {len(birthdays)} Geburtstage geladen")
            print(f"   📊 Spalten: {list(birthdays.columns)}")
            print(f"   📋 Erste 3 Einträge:")
            for i, (_, row) in enumerate(birthdays.head(3).iterrows()):
                print(f"      {i+1}. {row['Name']} - {row['Geburtstag']}")
        else:
            print("   ❌ Keine Geburtstage gefunden")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # 3. Strafen testen
    print("\n💰 Teste Strafen:")
    try:
        penalties = db.get_penalties()
        if penalties is not None and len(penalties) > 0:
            print(f"   ✅ {len(penalties)} Strafen geladen")
            print(f"   📊 Spalten: {list(penalties.columns)}")
            print(f"   📋 Erste 3 Einträge:")
            for i, (_, row) in enumerate(penalties.head(3).iterrows()):
                print(f"      {i+1}. {row['Spieler']} - {row['Strafe']} ({row['Betrag']}€)")
        else:
            print("   ❌ Keine Strafen gefunden")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # 4. Trainingsspielsiege testen
    print("\n🏆 Teste Trainingsspielsiege:")
    try:
        victories = db.get_training_victories()
        if victories is not None and len(victories) > 0:
            print(f"   ✅ {len(victories)} Trainingseinträge geladen")
            print(f"   📊 Spalten: {list(victories.columns)}")
            
            # Statistiken
            siege_count = len(victories[victories['Sieg'] == True]) if 'Sieg' in victories.columns else 0
            print(f"   🏆 Davon Siege: {siege_count}")
        else:
            print("   ❌ Keine Trainingsspielsiege gefunden")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # 5. Test: Strafe hinzufügen (nur zum Testen)
    print("\n➕ Teste Strafe hinzufügen:")
    try:
        test_penalty = {
            'Datum': '08.01.2025',
            'Spieler': 'Test-Spieler',
            'Strafe': 'Test-Strafe',
            'Betrag': 5.0,
            'Zusatzinfo': 'Nur zum Testen'
        }
        
        success = db.add_penalty(test_penalty)
        if success:
            print("   ✅ Test-Strafe erfolgreich hinzugefügt")
            
            # Nochmal laden um zu überprüfen
            updated_penalties = db.get_penalties()
            if updated_penalties is not None:
                print(f"   📊 Strafen nach dem Hinzufügen: {len(updated_penalties)}")
        else:
            print("   ❌ Fehler beim Hinzufügen der Test-Strafe")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Testen: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test beendet")

if __name__ == "__main__":
    test_all_tables() 