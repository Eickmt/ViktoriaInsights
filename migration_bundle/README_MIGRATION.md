# ViktoriaInsights Automation Migration

Dieses Bundle enthaelt die Dateien, die fuer die Migration der zwei GitHub-Actions-Automationen noetig sind.

## Zielstruktur im neuen Repo

Empfohlene Struktur:

```text
.github/workflows/
automation/viktoria-insights/
```

Die Workflows liegen bereits unter `.github/workflows/`.
Die Python-Skripte und Datendateien liegen unter `automation/viktoria-insights/`.

## Enthaltene Workflows

- `.github/workflows/viktoria_backup.yml`
  - taegliches Supabase-Backup
  - manuell per `workflow_dispatch` startbar
  - benoetigt `SUPABASE_URL` und `SUPABASE_ANON_KEY`

- `.github/workflows/viktoria_standings_update.yml`
  - taegliches Tabellen-Update
  - synchronisiert ausserdem Spielberichte
  - manuell per `workflow_dispatch` startbar
  - benoetigt `SUPABASE_URL` und `SUPABASE_ANON_KEY`

## GitHub Secrets im Ziel-Repo

Unter `Settings -> Secrets and variables -> Actions` setzen:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
```

## Nach der Migration testen

1. Bundle im Ziel-Repo entpacken.
2. Pfade in den Workflows pruefen.
3. Secrets setzen.
4. Beide Workflows manuell ueber `workflow_dispatch` starten.
5. Pruefen:
   - Backup-Workflow erzeugt Artifacts.
   - Tabellen-Workflow aktualisiert Supabase.
   - Spielberichte werden ohne Fehler synchronisiert.

## Nach erfolgreichem Test

Im alten Repo die bisherigen Workflows deaktivieren oder loeschen, damit die Automationen nicht doppelt laufen.
