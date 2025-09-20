"""LangChain-Agent zum Ausführen read-only SQL-Abfragen über Gemini 2.5 Flash."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool

from timezone_helper import get_german_now
from langchain_google_genai import ChatGoogleGenerativeAI

try:  # pragma: no cover - Import für vorhandenes SQL-Tool
    from run_sql_tool import run_sql_readonly  # type: ignore
except ImportError as exc:  # noqa: F401
    raise ImportError(
        "Das Modul 'run_sql_tool' mit der Funktion 'run_sql_readonly' muss verfügbar sein."
    ) from exc


load_dotenv()


def _run_sql_tool(query: str) -> str:
    """Wrappt run_sql_readonly und gibt JSON als String zurück."""
    result: Dict[str, Any] = run_sql_readonly(query)
    return json.dumps(result, ensure_ascii=False)


def _format_rows(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "Keine Daten gefunden."
    keys = list(rows[0].keys())
    lines = [" | ".join(str(row.get(k, "")) for k in keys) for row in rows]
    header = " | ".join(keys)
    return "\n".join([header, "-" * len(header), *lines])


_SCHEMA_CACHE: str | None = None


def _describe_schema(_: str = "") -> str:
    """Lädt Schema-Infos aus der DB und cached sie."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE:
        return _SCHEMA_CACHE

    tables = [
        "dim_date",
        "dim_penalty_type",
        "dim_player",
        "fact_penalty",
        "fact_training_win",
        "team_standings",
        "events",
        "lineups",
        "matches",
    ]

    table_filter = "', '".join(tables)
    schema_query = (
        "SELECT table_name, column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' "
        f"AND table_name IN ('{table_filter}') "
        "ORDER BY table_name, ordinal_position"
    )

    responses = []
    result = run_sql_readonly(schema_query)
    if not result.get("ok"):
        responses.append(f"Schema: Fehler - {result.get('error')}")
    else:
        rows = result.get("rows", [])
        responses.append(f"Schema:\n{_format_rows(rows)}")

    examples = {
        "matches": "SELECT * FROM matches ORDER BY match_date DESC LIMIT 3",
        "events": "SELECT * FROM events ORDER BY minute ASC LIMIT 3",
        "lineups": "SELECT * FROM lineups LIMIT 3",
        "team_standings": "SELECT * FROM team_standings ORDER BY scraped_at DESC LIMIT 3",
        "dim_player": "SELECT * FROM dim_player LIMIT 3",
        "dim_penalty_type": "SELECT * FROM dim_penalty_type LIMIT 3",
        "fact_penalty": "SELECT * FROM fact_penalty ORDER BY created_at DESC LIMIT 3",
        "fact_training_win": "SELECT * FROM fact_training_win LIMIT 3",
        "dim_date": "SELECT * FROM dim_date LIMIT 3",
    }

    for name, query in examples.items():
        result = run_sql_readonly(query)
        label = f"Beispiele {name}"
        if not result.get("ok"):
            responses.append(f"{label}: Fehler - {result.get('error')}")
            continue
        rows = result.get("rows", [])
        responses.append(f"{label}:\n{_format_rows(rows)}")

    _SCHEMA_CACHE = "\n\n".join(responses)
    return _SCHEMA_CACHE


def get_schema_overview(force_refresh: bool = False) -> str:
    """Gibt das beschriebene Schema zurück und kann optional den Cache leeren."""

    global _SCHEMA_CACHE
    if force_refresh:
        _SCHEMA_CACHE = None
    return _describe_schema()


def _current_datetime(_: str = "") -> str:
    """Liefert das aktuelle Datum und die Uhrzeit in deutscher Zeitzone (ISO-Format)."""

    now = get_german_now()
    iso_value = now.isoformat()
    human = now.strftime("%d.%m.%Y %H:%M:%S %Z")
    return json.dumps({"iso": iso_value, "human": human})


RUN_SQL_TOOL = StructuredTool.from_function(
    func=_run_sql_tool,
    name="run_sql",
    description=(
        "Führt eine SELECT/WITH/EXPLAIN-Query gegen Postgres aus (read-only, LIMIT/Timeout enforced)."
    ),
)


DESCRIBE_SCHEMA_TOOL = StructuredTool.from_function(
    func=_describe_schema,
    name="describe_schema",
    description=(
        "Gibt einen Überblick über Tabellen und Beispielzeilen zurück. Bitte vor der ersten SQL-Abfrage aufrufen."
    ),
)


CURRENT_TIME_TOOL = StructuredTool.from_function(
    func=_current_datetime,
    name="current_datetime",
    description=(
        "Gibt das aktuelle Datum und Uhrzeit in Deutschland zurück. Nutze dieses Tool zur Berechnung von Zeiträumen."
    ),
)


SYSTEM_PROMPT = (
    "Du bist ein SQL-Assistent für TuS Viktoria Buchholz. Nutze zuerst describe_schema, um Tabelleninformationen zu erhalten. "
    "Wenn relative Zeitangaben vorkommen, verwende current_datetime. Führe gewünschte Abfragen eigenständig aus, ohne Rückfrage an den Nutzer. "
    "Erzeuge ausschließlich SELECT/WITH/EXPLAIN über die Tabelle matches und setze LIMIT 100."
)


def build_agent() -> AgentExecutor:
    """Erstellt einen LangChain-Agenten mit Gemini 2.5 Flash und dem run_sql Tool."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY ist nicht gesetzt. Prüfe deine .env Datei.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    tools = [DESCRIBE_SCHEMA_TOOL, CURRENT_TIME_TOOL, RUN_SQL_TOOL]
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def main() -> None:
    agent = build_agent()
    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:]).strip()
    else:
        try:
            query_text = input("Frage an den SQL-Agenten: ").strip()
        except EOFError:
            print("Keine Eingabe erhalten. Abbruch.")
            return

    if not query_text:
        print("Leere Eingabe. Agent wird nicht ausgeführt.")
        return

    response = agent.invoke({"input": query_text})
    print(response)


if __name__ == "__main__":
    main()
