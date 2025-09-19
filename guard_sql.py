"""SQL-Governor für read-only Abfragen des LangChain-Agents."""

from __future__ import annotations

import re
from typing import Set

import sqlparse
from sqlparse.tokens import DML, Keyword

ALLOWED_TOP: Set[str] = {"SELECT", "WITH", "EXPLAIN"}
FORBIDDEN_WORDS = re.compile(
    r"\b(UPDATE|DELETE|INSERT|UPSERT|MERGE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|COMMENT|VACUUM|"
    r"COPY|CALL|DO|EXECUTE|PREPARE|LISTEN|NOTIFY|SET\s+ROLE|SET\s+SESSION|RESET|SHOW|LOCK|"
    r"REFRESH\s+MATERIALIZED|ANALYZE|CLUSTER|REINDEX|SECURITY\s+DEFINER)\b",
    re.IGNORECASE,
)

def strip_comments(sql: str) -> str:
    """Entfernt Zeilen- und Blockkommentare."""

    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def is_single_statement(sql: str) -> bool:
    """Stellt sicher, dass nur ein Statement übergeben wurde."""

    statements = [stmt for stmt in sqlparse.parse(sql) if stmt.tokens and not stmt.is_whitespace]
    return len(statements) == 1


def top_keyword(sql: str) -> str:
    """Liefert das erste Schlüsselwort (SELECT/WITH/EXPLAIN)."""

    parsed = sqlparse.parse(sql)[0]
    for token in parsed.flatten():
        if token.ttype in (DML, Keyword):
            return token.value.upper()
    return ""


def enforce_limit(sql: str, default_limit: int = 100) -> str:
    """Ergänzt LIMIT {default_limit}, falls nicht vorhanden."""

    if re.search(r"\blimit\s+\d+\b", sql, re.IGNORECASE):
        return sql
    sql_no_semi = sql.rstrip().rstrip(";")
    return f"{sql_no_semi} LIMIT {default_limit};"


def guard_sql(raw_sql: str, default_limit: int = 100) -> tuple[bool, str, str]:
    """Validiert und härtet eine SQL-Query ab."""

    sql = strip_comments(raw_sql)

    if not is_single_statement(sql):
        return False, "Nur genau 1 Statement ist erlaubt.", sql
    if ";" in sql.strip()[:-1]:
        return False, "Statement-Chaining ist verboten.", sql

    if FORBIDDEN_WORDS.search(sql):
        return False, "Verbotenes Schlüsselwort gefunden.", sql

    top = top_keyword(sql)
    if top not in ALLOWED_TOP:
        return False, "Nur SELECT/WITH/EXPLAIN sind erlaubt.", sql

    safe = enforce_limit(sql, default_limit=default_limit)
    return True, "", safe
