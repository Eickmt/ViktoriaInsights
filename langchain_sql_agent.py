"""LangChain-Agent zum Ausführen read-only SQL-Abfragen über Gemini 2.5 Flash."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
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


RUN_SQL_TOOL = StructuredTool.from_function(
    func=_run_sql_tool,
    name="run_sql",
    description=(
        "Führt eine SELECT/WITH/EXPLAIN-Query gegen Postgres aus (read-only, LIMIT/Timeout enforced)."
    ),
)


SYSTEM_PROMPT = (
    "Du bist ein SQL-Assistent. Erzeuge ausschließlich SELECT/WITH/EXPLAIN über die Tabelle matches. "
    "Setze LIMIT 100."
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

    agent = create_tool_calling_agent(llm=llm, tools=[RUN_SQL_TOOL], prompt=prompt)
    return AgentExecutor(agent=agent, tools=[RUN_SQL_TOOL], verbose=True)


def main() -> None:
    agent = build_agent()
    query_text = "Zeige mir die neuesten Spiele"
    response = agent.invoke({"input": query_text})
    print(response)


if __name__ == "__main__":
    main()
