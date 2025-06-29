# 🔐 Authentifizierungssystem - ViktoriaInsights

## Übersicht

Das Authentifizierungssystem schützt die Strafen-Hinzufügen-Funktionalität vor unbefugtem Zugriff. Nur angemeldete Benutzer können neue Strafen hinzufügen.

## 🚀 Erste Einrichtung

### Standard-Admin-Account
Beim ersten Start wird automatisch ein Standard-Admin-Account erstellt:

- **Benutzername:** `admin`
- **Passwort:** `viktoria2024`

⚠️ **Wichtig:** Ändern Sie das Standard-Passwort nach der ersten Anmeldung!

## 👥 Benutzerrollen

### Admin
- Kann Strafen hinzufügen
- Kann neue Benutzer erstellen
- Kann Benutzer verwalten (löschen, Rollen ändern)
- Hat Zugriff auf alle Funktionen

### User
- Kann Strafen hinzufügen
- Kann eigene Daten einsehen
- Keine Benutzerverwaltung

## 🔧 Funktionen

### Anmeldung
1. Gehen Sie zum Tab "➕ Neue Strafe"
2. Geben Sie Benutzername und Passwort ein
3. Klicken Sie auf "🚀 Anmelden"

### Registrierung neuer Benutzer
1. Klicken Sie auf "📝 Registrieren" im Anmeldeformular
2. Füllen Sie alle Felder aus:
   - Benutzername (eindeutig)
   - Passwort (mindestens 6 Zeichen)
   - Passwort bestätigen
   - Vollständiger Name
3. Klicken Sie auf "✅ Benutzer erstellen"

### Benutzerverwaltung (nur für Admins)
1. Melden Sie sich als Admin an
2. Gehen Sie zum Tab "👥 Benutzerverwaltung"
3. Hier können Sie:
   - Alle Benutzer einsehen
   - Neue Benutzer hinzufügen
   - Benutzer löschen
   - Rollen verwalten

### Passwort ändern
1. Melden Sie sich an
2. Gehen Sie zur Benutzerverwaltung
3. Verwenden Sie die Passwort-Ändern-Funktion

## 📁 Dateien

### `auth.py`
Hauptmodul für die Authentifizierung mit folgenden Funktionen:
- `hash_password()` - Passwort-Hashing
- `verify_credentials()` - Anmeldedaten prüfen
- `add_user()` - Neuen Benutzer hinzufügen
- `show_login_form()` - Anmeldeformular anzeigen
- `show_user_management()` - Benutzerverwaltung

### `user_credentials.json`
Speichert die Benutzerdaten (wird automatisch erstellt):
```json
{
  "admin": {
    "password_hash": "gehashtes_passwort",
    "role": "admin",
    "name": "Administrator"
  }
}
```

## 🔒 Sicherheit

### Passwort-Hashing
- Alle Passwörter werden mit SHA-256 gehasht
- Keine Klartext-Passwörter in der Datei

### Session-Management
- Anmeldestatus wird in Streamlit Session State gespeichert
- Automatische Abmeldung bei Seitenneuladen

### Zugriffskontrolle
- Strafen-Hinzufügen nur für angemeldete Benutzer
- Benutzerverwaltung nur für Admins

## 🛠️ Wartung

### Backup der Benutzerdaten
```bash
# Sichern Sie regelmäßig die user_credentials.json
cp user_credentials.json user_credentials_backup.json
```

### Passwort zurücksetzen
Falls das Admin-Passwort vergessen wurde:
1. Löschen Sie `user_credentials.json`
2. Starten Sie die Anwendung neu
3. Der Standard-Admin-Account wird neu erstellt

### Neue Benutzer hinzufügen
```python
from auth import add_user

# Neuen Admin hinzufügen
add_user("neuer_admin", "sicheres_passwort", "admin", "Vollständiger Name")

# Neuen Benutzer hinzufügen
add_user("neuer_user", "sicheres_passwort", "user", "Vollständiger Name")
```

## 🚨 Troubleshooting

### "Benutzer nicht gefunden"
- Prüfen Sie die Schreibweise des Benutzernamens
- Stellen Sie sicher, dass der Benutzer existiert

### "Falsches Passwort"
- Prüfen Sie die Groß-/Kleinschreibung
- Stellen Sie sicher, dass keine Leerzeichen am Anfang/Ende sind

### "Keine Berechtigung"
- Melden Sie sich als Admin an
- Prüfen Sie die Benutzerrolle in der Benutzerverwaltung

### Datei nicht gefunden
- Stellen Sie sicher, dass `auth.py` im Hauptverzeichnis liegt
- Prüfen Sie die Dateiberechtigungen

## 📞 Support

Bei Problemen mit der Authentifizierung:
1. Prüfen Sie die Logs in der Konsole
2. Stellen Sie sicher, dass alle Dateien vorhanden sind
3. Versuchen Sie einen Neustart der Anwendung
4. Kontaktieren Sie den Administrator

---

**Hinweis:** Dieses System ist für interne Verwendung gedacht. Für Produktionsumgebungen sollten zusätzliche Sicherheitsmaßnahmen implementiert werden. 