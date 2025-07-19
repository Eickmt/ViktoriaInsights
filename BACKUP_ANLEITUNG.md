# 🛡️ ViktoriaInsights Automatisches Backup System

## 📋 Überblick

Dieses System erstellt **automatisch jeden Tag um 2 Uhr nachts** Backups Ihrer ViktoriaInsights-Datenbank. Die Backups werden als Excel-Dateien gespeichert und 30 Tage lang aufbewahrt.

## ⚡ Schnell-Anleitung

### 1. GitHub Secrets einrichten (WICHTIG!)

1. **GitHub.com** öffnen → Ihr **ViktoriaInsights Repository**
2. **Settings** (Einstellungen) → **Secrets and variables** → **Actions**
3. **"New repository secret"** klicken

**Erstes Secret:**
- **Name:** `SUPABASE_URL`
- **Value:** Ihre Supabase-URL (z.B. `https://xyz.supabase.co`)

**Zweites Secret:**  
- **Name:** `SUPABASE_ANON_KEY`
- **Value:** Ihr Supabase Anonymous Key

> ⚠️ **WICHTIG:** Ohne diese Secrets funktioniert das Backup nicht!

### 2. Code committen und pushen

```bash
git add .
git commit -m "🛡️ Automatisches Backup-System hinzugefügt"
git push
```

### 3. Erstes Backup testen

1. **GitHub.com** → Ihr Repository → **Actions**
2. **"🛡️ ViktoriaInsights Datenbank-Backup"** auswählen
3. **"Run workflow"** → **"Run workflow"** (grüner Button)
4. Warten bis ✅ grün wird (~2-3 Minuten)

### 4. Backup herunterladen

1. **Auf das erfolgreiche Backup klicken**
2. **Runterscrollen** zu "Artifacts"
3. **"viktoria-backup-xyz"** herunterladen
4. **ZIP-Datei entpacken** → Excel-Dateien sind da! 📊

---

## 🔧 Detaillierte Anleitung

### Supabase-Credentials finden

#### Schritt 1: Supabase Dashboard öffnen
- Gehen Sie zu [supabase.com](https://supabase.com)
- Loggen Sie sich ein
- Wählen Sie Ihr **ViktoriaInsights-Projekt**

#### Schritt 2: API-Settings öffnen
- **Settings** → **API**

#### Schritt 3: Werte kopieren
- **Project URL** → Das ist Ihre `SUPABASE_URL`
- **anon/public key** → Das ist Ihr `SUPABASE_ANON_KEY`

### GitHub Secrets einrichten (detailliert)

#### Schritt 1: Repository Settings
1. GitHub.com → Ihr ViktoriaInsights Repository
2. **Settings** (rechts oben im Repository)
3. **Secrets and variables** (links im Menü)
4. **Actions** auswählen

#### Schritt 2: Erstes Secret erstellen
1. **"New repository secret"** klicken
2. **Name:** `SUPABASE_URL` (exakt so schreiben!)
3. **Secret:** Ihre Project URL aus Supabase einfügen
4. **"Add secret"** klicken

#### Schritt 3: Zweites Secret erstellen  
1. **"New repository secret"** klicken
2. **Name:** `SUPABASE_ANON_KEY` (exakt so schreiben!)
3. **Secret:** Ihren anon/public key aus Supabase einfügen
4. **"Add secret"** klicken

> ✅ **Resultat:** Sie sollten 2 Secrets sehen: `SUPABASE_URL` und `SUPABASE_ANON_KEY`

---

## 🚀 System testen

### Manuelles Backup starten

1. **GitHub.com** → Repository → **Actions**
2. **"🛡️ ViktoriaInsights Datenbank-Backup"** klicken
3. **"Run workflow"** (rechts) → **"Run workflow"** (grüner Button)

### Backup-Status prüfen

- ⏳ **Gelb/Orange:** Läuft gerade (~2-3 Minuten)
- ✅ **Grün:** Erfolgreich
- ❌ **Rot:** Fehler aufgetreten

### Bei Fehlern (❌)

1. **Auf das rote Backup klicken**
2. **"backup"** → **"🛡️ Datenbank-Backup erstellen"** anklicken
3. **Fehlermeldung lesen:**
   - `SUPABASE_URL` fehlt → Secret falsch eingerichtet
   - `SUPABASE_ANON_KEY` fehlt → Secret falsch eingerichtet
   - `Connection error` → Supabase-Daten prüfen

---

## 📥 Backups herunterladen

### Schritt 1: Zu Actions gehen
- GitHub.com → Repository → **Actions**

### Schritt 2: Erfolgreiche Backups finden
- **Grüne ✅ Backups** anklicken
- **Neueste zuerst** (ganz oben)

### Schritt 3: Artifact herunterladen
- **Nach unten scrollen** zu "Artifacts"
- **"viktoria-backup-XYZ"** anklicken
- **ZIP-Datei** wird heruntergeladen

### Schritt 4: Excel-Dateien extrahieren
- **ZIP-Datei entpacken**
- **Excel-Dateien öffnen:**
  - `backup_dim_player_YYYYMMDD_HHMMSS.xlsx`
  - `backup_dim_penalty_type_YYYYMMDD_HHMMSS.xlsx`
  - `backup_fact_penalty_YYYYMMDD_HHMMSS.xlsx`
  - `backup_fact_training_win_YYYYMMDD_HHMMSS.xlsx`

---

## ⏰ Automatischer Betrieb

### Wann läuft das Backup?
- **Täglich um 02:00 Uhr** (deutsche Zeit: 03:00/04:00 Uhr)
- **Automatisch** - Sie müssen nichts tun!

### Aufbewahrung
- **30 Tage** werden Backups gespeichert
- **Danach automatisch gelöscht** (Speicherplatz sparen)

### Benachrichtigungen
- **GitHub schickt E-Mails** bei Fehlern
- **Erfolgreiche Backups** werden nicht gemeldet (weniger Spam)

---

## 🔧 Erweiterte Einstellungen

### Backup-Zeit ändern

Datei `.github/workflows/backup.yml` bearbeiten:

```yaml
schedule:
  - cron: '0 2 * * *'  # 02:00 Uhr UTC
```

**Beispiele:**
- `'0 1 * * *'` = 01:00 Uhr UTC (02:00/03:00 deutsche Zeit)
- `'30 3 * * *'` = 03:30 Uhr UTC (04:30/05:30 deutsche Zeit)
- `'0 2 * * 1'` = Nur Montags um 02:00 Uhr

### Aufbewahrungszeit ändern

```yaml
retention-days: 30  # Auf gewünschte Tage ändern
```

### Tabellen hinzufügen/entfernen

Datei `backup_script.py` bearbeiten:

```python
tabellen = [
    "dim_player",           # Spielerdaten
    "dim_penalty_type",     # Strafenkatalog
    "fact_penalty",         # Strafen
    "fact_training_win",    # Trainingssiege
    "neue_tabelle",         # Neue Tabelle hinzufügen
    # "alte_tabelle"        # Tabelle entfernen (auskommentieren)
]
```

---

## 🛠️ Fehlerbehebung

### "Secrets not found"
**Problem:** Supabase-Credentials nicht richtig eingerichtet  
**Lösung:** GitHub Secrets nochmal prüfen (`SUPABASE_URL`, `SUPABASE_ANON_KEY`)

### "Connection failed"  
**Problem:** Falsche Supabase-URL oder -Key  
**Lösung:** Credentials in Supabase Dashboard nochmal kopieren

### "Table not found"
**Problem:** Tabelle existiert nicht in der Datenbank  
**Lösung:** Tabellennamen in `backup_script.py` prüfen/anpassen

### "No artifacts"
**Problem:** Backup wurde nicht gespeichert  
**Lösung:** Backup-Logs prüfen → Actions → Backup anklicken → Fehlermeldung lesen

### "Permission denied"
**Problem:** GitHub Actions nicht aktiviert  
**Lösung:** Repository → Settings → Actions → "Allow all actions"

---

## 📊 Was wird gesichert?

| Tabelle | Inhalt | Wichtigkeit |
|---------|---------|-------------|
| `dim_player` | Spielerdaten (Namen, IDs) | ⭐⭐⭐⭐⭐ |
| `dim_penalty_type` | Strafenkatalog (Arten, Beträge) | ⭐⭐⭐⭐ |
| `fact_penalty` | Alle Strafen (wer, wann, was) | ⭐⭐⭐⭐⭐ |
| `fact_training_win` | Trainingssiege | ⭐⭐⭐ |
| `dim_training_presence` | Trainingsanwesenheit | ⭐⭐⭐ |

---

## 🔄 Daten wiederherstellen

### Bei Datenverlust:

1. **Backup herunterladen** (siehe oben)
2. **Supabase Dashboard** öffnen
3. **Table Editor** → **Import**
4. **Excel-Datei auswählen**
5. **Tabelle überschreiben** oder **neue erstellen**

### Bei einzelnen Fehlern:

1. **Excel-Datei öffnen**
2. **Korrekte Daten finden**
3. **Manuell in Supabase korrigieren**

---

## 💰 Kosten

### GitHub Actions (kostenlos)
- ✅ **2.000 Minuten/Monat** gratis
- ✅ **Backup dauert ~2 Minuten**
- ✅ **= 30+ Backups/Monat** möglich
- ✅ **Also täglich für immer kostenlos!**

### Speicher
- ✅ **500 MB** pro Repository gratis
- ✅ **Excel-Dateien ~1-5 MB** je Backup  
- ✅ **= 100+ Backups** speicherbar

---

## 🆘 Support

### Selbst testen:
1. **Manuelles Backup starten** (siehe oben)
2. **Logs anschauen** bei Fehlern
3. **Secrets prüfen**

### Bei Problemen:
- **GitHub Issues** im Repository erstellen
- **Fehlermeldung** + **Screenshots** anhängen
- **Backup-Logs** kopieren

---

## ✅ Checkliste - Ist alles richtig eingerichtet?

### Vor dem ersten Backup:
- [ ] **GitHub Secrets** erstellt (`SUPABASE_URL`, `SUPABASE_ANON_KEY`)
- [ ] **Code committet** und gepusht
- [ ] **Manuelles Backup** erfolgreich getestet
- [ ] **Backup heruntergeladen** und Excel-Dateien geprüft

### Täglich automatisch:
- [ ] **E-Mail-Benachrichtigungen** aktiviert (GitHub Settings)
- [ ] **Backup läuft** jeden Tag um 2 Uhr
- [ ] **Backup-Dateien** werden gespeichert
- [ ] **Alte Backups** werden automatisch gelöscht

### Im Notfall:
- [ ] **Backup-Download** funktioniert
- [ ] **Excel-Dateien** sind vollständig
- [ ] **Wiederherstellung** getestet

---

## 🎉 Herzlichen Glückwunsch!

**Sie haben ein professionelles, automatisches Backup-System eingerichtet!**

- 🤖 **Läuft vollautomatisch**
- 💰 **Komplett kostenlos**  
- 🛡️ **30 Tage Datenschutz**
- 📊 **Excel-Format** zum einfachen Öffnen
- ⚡ **Schneller Download**

**Ihr Verein ist jetzt gegen Datenverlust geschützt!** 🛡️⚽ 