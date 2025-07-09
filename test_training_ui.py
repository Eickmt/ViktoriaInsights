#!/usr/bin/env python3
"""
Test für neue Trainingsspielsiege UI-Funktionalität
"""

from database_helper import db
from datetime import date, datetime

def test_training_day_functions():
    print("🧪 Test Trainingstag-Funktionen")
    print("=" * 50)
    
    # Test-Datum
    test_datum = "2025-01-08"
    test_datum_display = "08.01.2025"
    
    print(f"📅 Test-Datum: {test_datum_display}")
    
    # Test-Spieler
    test_spieler = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
    test_gewinner = ["Alice", "Bob", "Charlie"]  # Team 1 gewinnt
    
    print(f"👥 Test-Spieler: {test_spieler}")
    print(f"🏆 Test-Gewinner: {test_gewinner}")
    
    # 1. Prüfe bestehende Einträge
    print(f"\n1️⃣ Prüfe bestehende Einträge für {test_datum}:")
    existing = db.get_training_day_entries(test_datum)
    print(f"   Gefunden: {len(existing)} Einträge")
    
    # 2. Lösche bestehende Einträge (falls vorhanden)
    if existing:
        print(f"\n2️⃣ Lösche bestehende Einträge:")
        success, message = db.delete_training_day(test_datum)
        print(f"   {message}")
    
    # 3. Füge neue Einträge hinzu
    print(f"\n3️⃣ Füge neue Einträge hinzu:")
    success, message = db.add_training_day_entries(
        datum=test_datum,
        spieler_mit_sieg=test_gewinner,
        alle_spieler=test_spieler
    )
    print(f"   {message}")
    
    if success:
        # 4. Prüfe gespeicherte Einträge
        print(f"\n4️⃣ Prüfe gespeicherte Einträge:")
        saved_entries = db.get_training_day_entries(test_datum)
        print(f"   Gespeichert: {len(saved_entries)} Einträge")
        
        gewinner = [e['spielername'] for e in saved_entries if e['hat_gewonnen']]
        verlierer = [e['spielername'] for e in saved_entries if not e['hat_gewonnen']]
        
        print(f"   🏆 Gewinner: {gewinner}")
        print(f"   😔 Verlierer: {verlierer}")
        
        # 5. Validierung
        print(f"\n5️⃣ Validierung:")
        print(f"   ✅ Alle Spieler erfasst: {set(test_spieler) == {e['spielername'] for e in saved_entries}}")
        print(f"   ✅ Gewinner korrekt: {set(test_gewinner) == set(gewinner)}")
        print(f"   ✅ Verlierer korrekt: {set(test_spieler) - set(test_gewinner) == set(verlierer)}")
        
        # 6. Update Test - ändere Gewinner
        print(f"\n6️⃣ Update Test - ändere Gewinner:")
        neue_gewinner = ["David", "Eve", "Frank"]  # Team 2 gewinnt jetzt
        success2, message2 = db.add_training_day_entries(
            datum=test_datum,
            spieler_mit_sieg=neue_gewinner,
            alle_spieler=test_spieler
        )
        print(f"   {message2}")
        
        if success2:
            updated_entries = db.get_training_day_entries(test_datum)
            neue_gewinner_db = [e['spielername'] for e in updated_entries if e['hat_gewonnen']]
            print(f"   🏆 Neue Gewinner: {neue_gewinner_db}")
            print(f"   ✅ Update erfolgreich: {set(neue_gewinner) == set(neue_gewinner_db)}")
    
    # 7. Aufräumen - Test-Daten löschen
    print(f"\n7️⃣ Aufräumen:")
    success, message = db.delete_training_day(test_datum)
    print(f"   {message}")
    
    print(f"\n✅ Test abgeschlossen!")

if __name__ == "__main__":
    test_training_day_functions() 