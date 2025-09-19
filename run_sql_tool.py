"""Hilfsmodul zum sicheren Ausführen read-only SQL-Abfragen gegen Supabase."""

from __future__ import annotations

import os
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv

try:  # pragma: no cover - optional dependency
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None  # type: ignore[assignment]
    dict_row = None  # type: ignore[assignment]

from guard_sql import guard_sql

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)
load_dotenv(override=True)  # Fallback: Umgebung/übergeordnete Pfade prüfen

DEFAULT_LIMIT = int(os.getenv("RUN_SQL_DEFAULT_LIMIT", "100"))
DEFAULT_TIMEOUT_MS = int(os.getenv("RUN_SQL_TIMEOUT_MS", "15000"))
_CONNECTION_ENV_VARS: Iterable[str] = (
    "SUPABASE_DB_URL",
    "SUPABASE_CONNECTION_STRING",
    "DATABASE_URL",
    "SUPABASE_DB_CONNECTION",
)


class RunSqlError(RuntimeError):
    """Ausnahme für Probleme beim Ausführen der SQL-Abfrage."""


def _require_psycopg() -> None:
    if psycopg is None or dict_row is None:
        raise ImportError(
            "Das Paket 'psycopg' wird benötigt, ist aber nicht installiert. "
            "Bitte 'pip install psycopg[binary]' ausführen."
        )


def _get_connection_string() -> str:
    for env_var in _CONNECTION_ENV_VARS:
        value = os.getenv(env_var)
        if value:
            return value
    raise RunSqlError(
        "Keine Datenbank-Verbindung gefunden. Setze z.B. SUPABASE_DB_URL in der .env-Datei."
    )


def _rows_to_serialisable(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialised: List[Dict[str, Any]] = []
    for row in rows:
        normalised = {}
        for key, value in row.items():
            if isinstance(value, (bytes, bytearray)):
                normalised[key] = value.decode("utf-8", errors="replace")
            elif isinstance(value, (datetime, date)):
                normalised[key] = value.isoformat()
            elif isinstance(value, time):
                normalised[key] = value.isoformat()
            elif isinstance(value, Decimal):
                normalised[key] = str(value)
            else:
                normalised[key] = value
        serialised.append(normalised)
    return serialised


def run_sql_readonly(query: str) -> Dict[str, Any]:
    """Validiert eine Query und führt sie read-only gegen Supabase Postgres aus."""

    _require_psycopg()

    ok, message, safe_sql = guard_sql(query, default_limit=DEFAULT_LIMIT)
    if not ok:
        return {
            "ok": False,
            "error": message,
            "query": safe_sql,
        }

    conninfo = _get_connection_string()

    try:
        with psycopg.connect(conninfo, autocommit=True, row_factory=dict_row) as conn:  # type: ignore[arg-type]
            conn.execute(f"SET statement_timeout TO {DEFAULT_TIMEOUT_MS}")
            conn.execute("SET default_transaction_read_only = on")
            rows = conn.execute(safe_sql).fetchall()
            result_rows = _rows_to_serialisable(rows)
    except Exception as exc:  # pragma: no cover - Fehlerpfad
        return {
            "ok": False,
            "error": f"Ausführung fehlgeschlagen: {exc}",
            "query": safe_sql,
        }

    return {
        "ok": True,
        "query": safe_sql,
        "row_count": len(result_rows),
        "rows": result_rows,
        "columns": list(result_rows[0].keys()) if result_rows else [],
    }
