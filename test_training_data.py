#!/usr/bin/env python3
"""
Test für Trainingsspielsiege-Daten
Überprüft ob Siege korrekt berechnet werden
"""

from database_helper import db
import pandas as pd

def test_training_data():
    print("🏆 Test Trainingsspielsiege-Daten")
    print("=" * 50)
    
    # Daten laden
    try:
        df = db.get_training_victories()
        
        if df is None or len(df) == 0:
            print("❌ Keine Trainingsdaten gefunden!")
            return
        
        print(f"✅ {len(df)} Trainingseinträge geladen")
        print(f"📊 Spalten: {list(df.columns)}")
        
        # Datentypen prüfen
        print(f"\n📋 Datentypen:")
        for col in df.columns:
            print(f"   {col}: {df[col].dtype}")
        
        # Sieg-Spalte analysieren
        if 'Sieg' in df.columns:
            print(f"\n🏆 Sieg-Spalte Analyse:")
            print(f"   Unique Werte: {df['Sieg'].unique()}")
            print(f"   Anzahl True: {len(df[df['Sieg'] == True])}")
            print(f"   Anzahl False: {len(df[df['Sieg'] == False])}")
            print(f"   Siegquote: {len(df[df['Sieg'] == True]) / len(df) * 100:.1f}%")
        
        # Spieler-Analyse
        print(f"\n👥 Spieler-Analyse:")
        spieler_stats = df.groupby('Spieler').agg({
            'Sieg': ['count', 'sum']
        }).round(2)
        spieler_stats.columns = ['Teilnahmen', 'Siege']
        spieler_stats['Siegquote'] = (spieler_stats['Siege'] / spieler_stats['Teilnahmen'] * 100).round(1)
        spieler_stats = spieler_stats.sort_values('Siege', ascending=False)
        
        print(spieler_stats.head(10))
        
        # Datums-Analyse
        print(f"\n📅 Datums-Analyse:")
        print(f"   Trainingstage: {df['Datum'].nunique()}")
        print(f"   Zeitraum: {df['Datum'].min()} bis {df['Datum'].max()}")
        
        # Tägliche Statistiken
        daily_stats = df.groupby('Datum').agg({
            'Spieler': 'count',  # Teilnahmen
            'Sieg': 'sum'       # Siege
        }).rename(columns={'Spieler': 'Teilnahmen', 'Sieg': 'Siege'})
        daily_stats['Siegquote'] = (daily_stats['Siege'] / daily_stats['Teilnahmen'] * 100).round(1)
        
        print(f"\n📊 Tägliche Statistiken (letzte 5 Trainings):")
        print(daily_stats.tail())
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    test_training_data() 