# ⚽ ViktoriaInsights

Eine moderne Streamlit-App für die erste Mannschaft von Viktoria Buchholz.

## 🎯 Funktionen

**ViktoriaInsights** bietet eine zentrale Plattform für alle wichtigen Teamaktivitäten:

### 🏠 Startseite
- Übersichtsdashboard mit aktuellen Statistiken
- Quick Actions für häufige Aufgaben
- Aktivitäts-Feed
- Teaminfos und Wetter

### 📅 Teamkalender
- Geburtstagskalender mit automatischer Berechnung der nächsten Termine
- Altersstatistiken und Geburtstagsverteilung
- Erinnerungseinstellungen
- Neue Geburtstage hinzufügen

### 💰 Mannschaftskasse
- Detaillierte Finanzübersicht
- Einnahmen- und Ausgabenverfolgung
- Kategorisierte Transaktionen
- Finanzstatistiken und Trends
- Kassenziele und Export-Funktionen

### 📊 Trainingsstatistiken
- Anwesenheitstracking für alle Spieler
- Individuelle und Team-Statistiken
- Trainings-Trends und Analysen
- Neues Training eintragen
- Belohnungssystem für gute Anwesenheit

### 🤡 Esel der Woche
- **Prominente Darstellung des aktuellen Esels**
- Strafenverfolgung und -verwaltung
- Strafen-Statistiken und Rankings
- Esel-Historie der letzten Wochen
- Schnelle Strafen-Eingabe

### ⭐ Team Gimmicks
- Zufalls-Generator für Teamentscheidungen
- Sprüche des Tages mit Voting-System
- Team-Umfragen und Abstimmungen
- Fotogalerie mit verschiedenen Kategorien
- Interaktive Spiele und Challenges

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Installer)

### 1. Repository klonen oder downloaden
```bash
git clone <repository-url>
cd ViktoriaInsights
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. App starten
```bash
streamlit run main.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

## 📦 Benötigte Bibliotheken

- **streamlit** >= 1.28.0 - Web-Framework
- **pandas** >= 2.0.0 - Datenverarbeitung
- **plotly** >= 5.15.0 - Interaktive Diagramme
- **datetime** - Datums- und Zeitfunktionen
- **pillow** >= 10.0.0 - Bildverarbeitung
- **streamlit-option-menu** >= 0.3.6 - Erweiterte Navigation

## 🏗️ Projektstruktur

```
ViktoriaInsights/
│
├── main.py                 # Haupteinstiegspunkt der App
├── requirements.txt        # Python-Abhängigkeiten
├── README.md              # Diese Datei
│
└── pages/                 # Modulare Seitenkomponenten
    ├── __init__.py
    ├── startseite.py      # Dashboard und Übersicht
    ├── teamkalender.py    # Geburtstagskalender
    ├── mannschaftskasse.py # Finanzverwaltung
    ├── trainingsstatistiken.py # Trainingsanalyse
    ├── esel_der_woche.py  # Strafenverwaltung
    └── gimmicks.py        # Spaß-Features
```

## 🎨 Features im Detail

### Moderne UI/UX
- Responsive Design
- Intuitive Navigation mit Icons
- Farbkodierung für bessere Übersicht
- Interaktive Diagramme und Visualisierungen

### Datenvisualisierung
- Plotly-Charts für Trends und Statistiken
- Farbkodierte Metriken
- Progress-Bars und Gauges
- Interaktive Tabellen

### Modular aufgebaut
- Jede Funktion in eigenem Modul
- Wiederverwendbare Komponenten
- Einfache Erweiterung möglich

## 🔧 Anpassung

### Spielerdaten ändern
Die Beispieldaten können in den jeweiligen Python-Dateien angepasst werden:
- Spielernamen in den Listen `spieler_namen`
- Beispieldaten in den DataFrame-Definitionen

### Styling anpassen
CSS-Anpassungen können in `main.py` im `st.markdown()`-Block vorgenommen werden.

### Neue Features hinzufügen
1. Neue Datei in `/pages/` erstellen
2. `show()`-Funktion implementieren
3. Import in `main.py` hinzufügen
4. Navigation erweitern

## 💡 Zukünftige Erweiterungen

- **Datenbank-Integration** für persistente Datenspeicherung
- **Benutzer-Authentifizierung** für verschiedene Rollen
- **Mobile App** als PWA
- **Email-Benachrichtigungen** für wichtige Events
- **Kalender-Integration** für Termine
- **WhatsApp-Bot** für Quick Actions
- **Foto-Upload** für Galerie
- **Export-Funktionen** (PDF, Excel)

## 🎯 Verwendung

### Erste Schritte
1. App starten (`streamlit run main.py`)
2. Navigation in der Sidebar verwenden
3. Mit den Beispieldaten experimentieren
4. Eigene Daten in den Formularen eingeben

### Tipps
- **Esel der Woche** wird automatisch prominent angezeigt
- Alle Eingaben werden aktuell nur in der Session gespeichert
- Für Produktivnutzung sollte eine Datenbank angebunden werden
- Mobile Nutzung wird unterstützt

## 🐛 Bekannte Limitierungen

- Daten werden nicht dauerhaft gespeichert (nur Session-basiert)
- Beispieldaten sind statisch
- Keine Benutzer-Authentifizierung
- Keine Email-Integration

## 📝 Lizenz

Dieses Projekt ist für den internen Gebrauch von Viktoria Buchholz erstellt.

## 👥 Kontakt

Bei Fragen oder Verbesserungsvorschlägen wenden Sie sich an die Mannschaftsleitung.

---

**⚽ Viktoria Buchholz - Erste Mannschaft**  
*"Ein Team, ein Traum, ein Ziel!"* 