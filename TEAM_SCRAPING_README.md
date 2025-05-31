# 🏆 Team-Scraping System für ViktoriaInsights

## Überblick

Das Team-Scraping System lädt automatisch aktuelle Teamdaten von fussball.de und zeigt sie auf der Startseite an. Das System verwendet intelligentes Caching, um Performance zu optimieren und Server-Last zu minimieren.

## ✨ Features

- **Automatisches Scraping**: Lädt täglich aktuelle Tabellendaten von fussball.de
- **Intelligentes Caching**: 24-Stunden-Cache verhindert überflüssige Anfragen
- **Fallback-System**: Zeigt letzte bekannte Daten bei Scraping-Fehlern
- **Status-Anzeige**: Visueller Indikator für Datenquelle (Live/Cache/Fallback)
- **Robuste Fehlerbehandlung**: Funktioniert auch bei temporären Server-Problemen

## 📁 Dateien

### Neue Dateien:
- `team_scraper.py` - Hauptmodul für Scraping und Caching
- `update_team_data.py` - Standalone-Skript für manuelle/geplante Updates
- `team_data_cache.json` - Cache-Datei (wird automatisch erstellt)
- `bezirksliga_tabelle.csv` - Komplette Ligatabelle (wird automatisch erstellt)

### Geänderte Dateien:
- `pages/startseite.py` - Integriert das neue Scraping-System
- `requirements.txt` - Neue Abhängigkeit: beautifulsoup4

## 🚀 Verwendung

### Automatisch in der App
Das System funktioniert automatisch bei jedem Besuch der Startseite:

1. **Erster Aufruf**: Scraped Live-Daten von fussball.de
2. **Folgeaufrufe**: Nutzt 24h-Cache für bessere Performance
3. **Nach 24h**: Scraped automatisch neue Daten
4. **Bei Fehlern**: Nutzt letzte bekannte Daten

### Manuelles Update
```bash
# Normales Update (nur wenn Cache älter als 24h)
python update_team_data.py

# Update erzwingen
python update_team_data.py --force

# Cache-Status anzeigen
python update_team_data.py --info

# Hilfe anzeigen
python update_team_data.py --help
```

## 📊 Status-Indikatoren

Die Teaminfos zeigen den Status der Datenquelle:

- 🔴 **Live Scraping**: Neue Daten von fussball.de geladen
- 🟡 **Cache**: Daten aus 24h-Cache (mit Zeitstempel)
- ⚪ **Fallback**: Letzte bekannte oder Standard-Daten

## ⚙️ Konfiguration

### Team-ID anpassen
In `team_scraper.py`:
```python
TEAM_ID = "011MI9UHGG000000VTVG0001VTR8C1K7"  # TuS Viktoria Buchholz
SAISON = "2425"  # Saison 2024/25
```

### Cache-Dauer ändern
```python
@st.cache_data(ttl=86400)  # 86400 = 24 Stunden
```

## 🔧 Automatisierung

### Windows Task Scheduler
1. Task Scheduler öffnen
2. "Einfache Aufgabe erstellen"
3. Name: "Viktoria Team Update"
4. Auslöser: "Täglich" um 06:00
5. Aktion: `python C:\Pfad\zu\update_team_data.py`

### Linux Cron
```bash
# Crontab bearbeiten
crontab -e

# Täglich um 06:00 ausführen
0 6 * * * cd /path/to/viktoria && python update_team_data.py
```

## 🛠️ Troubleshooting

### Häufige Probleme

**1. Scraping schlägt fehl**
- Prüfen Sie die Internetverbindung
- fussball.de könnte temporär nicht erreichbar sein
- User-Agent Header könnten blockiert werden

**2. Cache wird nicht erstellt**
- Schreibrechte im Verzeichnis prüfen
- Laufwerk mit genügend Speicherplatz

**3. Team nicht gefunden**
- Team-ID prüfen und aktualisieren
- Saison-Code aktualisieren

### Debug-Informationen
```python
# Cache-Status prüfen
python update_team_data.py --info

# Manuelle Tests
python -c "import team_scraper; print(team_scraper.get_team_data())"
```

## 📋 Datenstruktur

### Cache-Format (team_data_cache.json)
```json
{
  "last_update": "2024-12-24T10:30:00",
  "viktoria_info": {
    "platz": "8.",
    "punkte": "44",
    "spiele": "18",
    "siege": "13",
    "unentschieden": "5",
    "niederlagen": "0",
    "tore_geschossen": "61",
    "tore_erhalten": "62",
    "tordifferenz": "-1"
  },
  "total_teams": 16,
  "source": "fussball.de"
}
```

### CSV-Format (bezirksliga_tabelle.csv)
Standard-Ligatabelle mit allen Teams der Bezirksliga.

## 🔄 Update-Zyklus

1. **Streamlit App startet**: Prüft Cache-Validität
2. **Cache gültig** (<24h): Zeigt Cache-Daten
3. **Cache ungültig** (>24h): Startet Scraping
4. **Scraping erfolgreich**: Aktualisiert Cache und CSV
5. **Scraping fehlgeschlagen**: Nutzt Fallback-Daten

## 🚨 Wichtige Hinweise

- **Rate Limiting**: Das System macht max. 1 Request pro 24h
- **Robustheit**: Funktioniert auch bei temporären Server-Ausfällen
- **Performance**: Keine Verzögerung bei wiederholten Seitenaufrufen
- **Datenqualität**: Automatische Validierung der gescrapten Daten

## 📞 Support

Bei Problemen:
1. Debug-Informationen sammeln: `python update_team_data.py --info`
2. Cache-Dateien prüfen: `team_data_cache.json`, `bezirksliga_tabelle.csv`
3. Manuelle Tests durchführen: `python update_team_data.py --force` 