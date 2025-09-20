"""Utility script to pre-generate daily facts and example questions for ViktoriaInsights."""
from __future__ import annotations

import os
import re
import html
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv() -> None:  # type: ignore[redefinition]
        """Fallback noop if python-dotenv isn't installed."""

        return None
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_sql_agent import build_agent, get_schema_overview
from supabase import Client, create_client

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
GERMAN_TZ = ZoneInfo("Europe/Berlin")

DEFAULT_SAMPLE_QUESTIONS: List[str] = [
    "Wie viele Tore hat TuS Viktoria Buchholz in dieser Saison insgesamt erzielt?",
    "Welcher Spieler hat die meisten Einsätze in der laufenden Saison absolviert?",
    "Wie hoch ist die Gesamtsumme aller Mannschafts-Strafen in der aktuellen Saison?",
]

DEFAULT_FACTS: List[Dict[str, str]] = [
    {
        "question": "Wie viele Tore hat TuS Viktoria Buchholz in dieser Saison erzielt?",
        "answer": "Zurzeit können keine aktuellen Tordaten geladen werden.",
    },
    {
        "question": "Welcher Spieler hat bisher die meisten Minuten absolviert?",
        "answer": "Aktuell stehen keine Einsatzminuten zur Verfügung.",
    },
    {
        "question": "Wie viele unterschiedliche Torschützen hat das Team in dieser Saison?",
        "answer": "Noch keine Informationen zu Torschützen abrufbar.",
    },
]

CARD_TERMS = ["spieler", "mannschaft", "viktoria", "buchholz", "tus"]
PAST_SEASON_TERMS = [
    "letzte saison",
    "vergangene saison",
    "vorherige saison",
    "vorjahr",
    "saison 2024",
    "saison 2023",
    "saison 2022",
    "saison 21",
    "saison 22",
    "saison 23",
]


@dataclass
class GeneratedFact:
    question: str
    answer: str
    raw_answer: Optional[str] = None

    def as_payload(self) -> Dict[str, str]:
        return {
            "question": self.question,
            "answer": self.answer,
            "raw_answer": self.raw_answer or self.answer,
        }


def _validate_question(text: str) -> bool:
    lower = text.lower()
    if "siegquote" in lower:
        return False
    if any(term in lower for term in ["kommenden gegner", "kommender gegner", "nächsten gegner", "nächster gegner", "nächste gegner", "nächste spiele"]):
        return False
    if "[" in text or "]" in text:
        return False
    if "karten" in lower and any(term in lower for term in CARD_TERMS):
        return False
    if any(term in lower for term in PAST_SEASON_TERMS):
        return False
    return True


def _clean_answer_text(raw: str) -> str:
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\r", "")

    segments: List[str] = []
    for segment in text.split("\n"):
        cleaned = re.sub(r"\s+", " ", segment).strip()
        if cleaned:
            segments.append(cleaned)

    if segments:
        first_segment = segments[0]
        if first_segment.lower().startswith("antwort:"):
            stripped_first = first_segment.split(":", 1)[-1].strip()
            if stripped_first:
                segments[0] = stripped_first
            else:
                segments = segments[1:]

    if not segments:
        segments = ["Keine Daten verfügbar."]

    return "\n".join(segments)


def _limit_to_three_unique(items: List[str], fallback: List[str]) -> List[str]:
    unique: List[str] = []
    seen = set()
    for item in items:
        normalized = item.strip()
        if not normalized or normalized.lower() in seen:
            continue
        if not _validate_question(normalized):
            continue
        unique.append(normalized)
        seen.add(normalized.lower())
        if len(unique) == 3:
            break
    if len(unique) < 3:
        for backup in fallback:
            if backup.lower() not in seen:
                unique.append(backup)
                seen.add(backup.lower())
            if len(unique) == 3:
                break
    return unique[:3]


def _create_llm() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY ist nicht gesetzt.")
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.3, api_key=api_key)


def generate_example_questions(schema_overview: str) -> List[str]:
    llm = _create_llm()
    prompt = (
        "Du bist ein hilfreicher Assistent für Fußballstatistiken von TuS Viktoria Buchholz. "
        "Nutze das folgende Datenbankschema, um drei konkrete deutsche Fragen zu erzeugen, "
        "die ein Trainer dem Statistik-Assistenten stellen könnte. Jede Frage in einer eigenen Zeile, "
        "ohne Aufzählungszeichen. Stelle keine Fragen zu zukünftigen oder kommenden Gegnern, "
        "verwende keine Fragen zur Siegquote und verzichte strikt auf Platzhalter wie Namen in eckigen Klammern. "
        "Beschränke dich auf die aktuelle Saison und stelle keine Fragen zu vergangenen Spielzeiten. "
        "Wenn du die Saison filterst, verwende unbedingt das Schemaformat matches.season = '25/26'. Die Werte sind in der Datenbank als 25/26 gespeichert. "
        "Erzeuge genau drei Fragen: Zwei davon müssen auf Spielevents (Tabellen matches, events, lineups oder team_standings) basieren, "
        "die dritte Frage muss sich auf Strafen oder Training (Tabellen fact_penalty, fact_training_win, dim_penalty_type, dim_player oder dim_date) stützen. "
        "Wenn du Tordaten analysierst, joine events mit matches über match_id und berücksichtige nur Tore, bei denen (team_side = 'home' UND matches.home_team = 'TuS Viktoria Buchholz') "
        "ODER (team_side = 'away' UND matches.away_team = 'TuS Viktoria Buchholz'). "
        "Fragen dürfen sich nicht darauf beziehen, wie viele Karten eine bestimmte Mannschaft oder ein einzelner Spieler erhalten hat; "
        "allgemeine Auswertungen zu Karten (z. B. nach Zeitpunkten oder Farben) sind erlaubt. "
        "Fragen müssen vollständig konkret formuliert sein. Schema:\n" + schema_overview
    )
    response = llm.invoke(prompt)  # type: ignore[arg-type]
    if isinstance(response, str):
        raw_text = response
    else:
        raw_text = getattr(response, "content", "")
        if isinstance(raw_text, list):
            raw_text = "\n".join(str(part) for part in raw_text)
    lines = [line.strip("- ") for line in raw_text.splitlines() if line.strip()]
    return _limit_to_three_unique(lines, DEFAULT_SAMPLE_QUESTIONS)


def generate_fact_questions(schema_overview: str) -> List[str]:
    llm = _create_llm()
    prompt = (
        "Du bist ein datengetriebener Analyst für TuS Viktoria Buchholz. "
        "Formuliere drei konkrete, spannende Faktenfragen zur aktuellen Saison, "
        "die über das bereitgestellte Datenbankschema beantwortet werden können. "
        "Jede Frage in einer eigenen Zeile ohne Aufzählungszeichen. Vermeide Themen zu zukünftigen "
        "oder kommenden Gegnern, verzichte auf Fragen zur Siegquote und verwende keinerlei Platzhalter. "
        "Beschränke dich auf die laufende Saison und stelle keine Fragen zu vergangenen Spielzeiten. "
        "Wenn du auf eine Saison verweist, nutze das Format aus dem Schema (z. B. matches.season = '25/26'). "
        "Fragen dürfen nicht darauf abzielen, wie viele Karten eine bestimmte Mannschaft oder ein einzelner Spieler erhalten hat; "
        "allgemeine Analysen zu Karten (z. B. nach Spielzeit oder Kartenfarbe) sind erlaubt. "
        "Die Fragen müssen vollständig konkret sein. Schema:\n" + schema_overview
    )
    response = llm.invoke(prompt)  # type: ignore[arg-type]
    if isinstance(response, str):
        raw_text = response
    else:
        raw_text = getattr(response, "content", "")
        if isinstance(raw_text, list):
            raw_text = "\n".join(str(part) for part in raw_text)
    lines = [line.strip("- ") for line in raw_text.splitlines() if line.strip()]
    return _limit_to_three_unique(lines, [fact["question"] for fact in DEFAULT_FACTS])


def generate_facts(agent, questions: List[str]) -> List[GeneratedFact]:
    facts: List[GeneratedFact] = []
    for question in questions:
        try:
            result = agent.invoke({"input": question})
            if isinstance(result, dict):
                raw_answer = result.get("output", "")
            else:
                raw_answer = str(result)
        except Exception as exc:  # noqa: BLE001
            raw_answer = f"Fehler bei der Auswertung: {exc}"
        cleaned_answer = _clean_answer_text(raw_answer)
        facts.append(GeneratedFact(question=question, answer=cleaned_answer, raw_answer=raw_answer))
    return facts


def _create_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL oder SUPABASE_ANON_KEY fehlen.")
    return create_client(supabase_url, supabase_key)


def store_daily_content(
    supabase: Client,
    content_date: datetime,
    questions: List[str],
    facts: List[GeneratedFact],
) -> None:
    payload = []
    date_str = content_date.date().isoformat()

    for idx, question in enumerate(questions, start=1):
        payload.append(
            {
                "content_date": date_str,
                "content_type": "example_question",
                "position": idx,
                "question_text": question,
                "answer_text": None,
                "source_model": MODEL_NAME,
                "raw_payload": None,
            }
        )

    for idx, fact in enumerate(facts, start=1):
        payload.append(
            {
                "content_date": date_str,
                "content_type": "daily_fact",
                "position": idx,
                "question_text": fact.question,
                "answer_text": fact.answer,
                "source_model": MODEL_NAME,
                "raw_payload": fact.as_payload(),
            }
        )

    supabase.table("daily_generated_content").upsert(
        payload,
        on_conflict="content_date,content_type,position",
    ).execute()


def main() -> None:
    schema_overview = get_schema_overview()
    example_questions = generate_example_questions(schema_overview)
    fact_questions = generate_fact_questions(schema_overview)

    agent = build_agent()
    facts = generate_facts(agent, fact_questions)

    supabase = _create_supabase_client()
    generation_timestamp = datetime.now(tz=GERMAN_TZ)

    store_daily_content(
        supabase=supabase,
        content_date=generation_timestamp,
        questions=example_questions,
        facts=facts,
    )

    print("Gespeicherte Beispiel-Fragen:")
    for idx, question in enumerate(example_questions, start=1):
        print(f"  {idx}. {question}")

    print("\nGespeicherte Fakten des Tages:")
    for idx, fact in enumerate(facts, start=1):
        print(f"  {idx}. {fact.answer}")


if __name__ == "__main__":
    main()
