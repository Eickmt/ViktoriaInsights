import base64
import os
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_sql_agent import build_agent, get_schema_overview

load_dotenv()


@st.cache_resource(show_spinner=False)
def get_agent():
    return build_agent()


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def get_example_questions(schema: str) -> List[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY ist nicht gesetzt.")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, api_key=api_key)
    prompt = (
        "Du bist ein hilfreicher Assistent für Fußballstatistiken von TuS Viktoria Buchholz. "
        "Nutze das folgende Datenbankschema, um drei konkrete deutsche Fragen zu erzeugen, "
        "die ein Trainer dem Statistik-Assistenten stellen könnte. Jede Frage in einer eigenen Zeile, "
        "ohne Aufzählungszeichen. Stelle keine Fragen zu zukünftigen oder kommenden Gegnern, "
        "verwende keine Fragen zur Siegquote und verzichte strikt auf Platzhalter wie Namen in eckigen Klammern. "
        "Beziehe dich ausschließlich auf die laufende Saison und stelle keine Fragen zu vergangenen Spielzeiten. "
        "Wenn du die Saison einschränkst, nutze unbedingt das Format wie im Schema (z. B. matches.season = '25/26'). Die Werte sind in der Datenbank als 25/26 gespeichert. "
        "Erzeuge genau drei Fragen: zwei davon müssen sich auf Spielevents (Tabellen matches, events, lineups oder team_standings) beziehen, "
        "die dritte Frage muss sich auf Strafen oder Training (Tabellen fact_penalty, fact_training_win, dim_penalty_type, dim_player oder dim_date) stützen. "
        "Wenn du Tordaten analysierst, joine events mit matches über match_id und filtere nur Tore, bei denen (team_side = 'home' UND matches.home_team = 'TuS Viktoria Buchholz') "
        "ODER (team_side = 'away' UND matches.away_team = 'TuS Viktoria Buchholz'). "
        "Fragen dürfen sich nicht darauf beziehen, wie viele Karten eine bestimmte Mannschaft oder ein einzelner Spieler erhalten hat; "
        "allgemeine Auswertungen zu Karten (z. B. nach Zeitpunkten oder Farben) sind erlaubt. "
        "Fragen müssen vollständig konkret formuliert sein. Schema:\n" + schema
    )
    response = llm.invoke(prompt)  # type: ignore[arg-type]
    if isinstance(response, str):
        raw_text = response
    else:
        raw_text = getattr(response, "content", "")
        if isinstance(raw_text, list):
            raw_text = "\n".join(str(part) for part in raw_text)
    questions = [line.strip("- ") for line in raw_text.splitlines() if line.strip()]

    valid_questions = [q for q in questions if _is_valid_question(q)]
    default_questions = [
        "Wie viele Tore hat TuS Viktoria Buchholz in dieser Saison insgesamt erzielt?",
        "Welcher Spieler hat die meisten Einsätze in der laufenden Saison absolviert?",
        "Wie hoch ist die Gesamtsumme aller Mannschafts-Strafen in der aktuellen Saison?",
    ]

    if len(valid_questions) < 3:
        # Ergänze mit bekannten validen Beispielfragen, ohne Duplikate
        for fallback in default_questions:
            if fallback not in valid_questions:
                valid_questions.append(fallback)
            if len(valid_questions) == 3:
                break

    return valid_questions[:3]


def _is_valid_question(question: str) -> bool:
    """Validate generated questions against business rules."""

    lower = question.lower()
    if "siegquote" in lower:
        return False
    if "kommenden gegner" in lower or "kommender gegner" in lower:
        return False
    if "nächsten gegner" in lower or "nächster gegner" in lower:
        return False
    if "nächste gegner" in lower or "nächste spiele" in lower:
        return False
    if "[" in question or "]" in question:
        return False
    if "karten" in lower and any(term in lower for term in ["spieler", "mannschaft", "viktoria", "buchholz", "tus"]):
        return False
    if any(term in lower for term in ["letzte saison", "vorherige saison", "saison 2024", "saison 23", "saison 2023", "saison 2022", "vergangene saison", "vorjahr"]):
        return False
    return True


@st.cache_data(show_spinner=False)
def _get_logo_base64() -> str:
    """Load the club logo once and cache it for reuse."""

    logo_path = Path(__file__).resolve().parent.parent / "VB_Logo.png"
    with logo_path.open("rb") as logo_file:
        return base64.b64encode(logo_file.read()).decode("utf-8")


def _init_state():
    if "buchholz_messages" not in st.session_state:
        st.session_state.buchholz_messages = []


def _add_message(role: str, content: str) -> None:
    st.session_state.buchholz_messages.append({"role": role, "content": content, "ts": datetime.utcnow().isoformat()})


def _run_agent(agent, text: str) -> str:
    try:
        result = agent.invoke({"input": text})
        answer = result.get("output") if isinstance(result, dict) else str(result)
    except Exception as exc:  # noqa: BLE001
        answer = f"Fehler bei der Ausführung: {exc}"
    return answer or "Keine Antwort erhalten."


def _chat_message(role: str, content: str):
    with st.chat_message(role):
        st.markdown(content)


def show():
    st.markdown(
        """
        <style>
            .question-pill button {
                background: linear-gradient(135deg, #f8f5f0, #f1ede7);
                color: #2e7d32;
                border: none;
                border-radius: 999px;
                padding: 0.6rem 1.8rem;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15);
            }
            .question-pill button:hover {
                background: linear-gradient(135deg, #ffffff, #f4eee7);
                color: #1b5e20;
            }
            .input-container {
                padding: 1.2rem 0;
            }
            .chat-container {
                padding: 1rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _init_state()
    agent = get_agent()
    schema_overview = get_schema_overview()
    try:
        example_questions = get_example_questions(schema_overview)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Beispielfragen konnten nicht geladen werden: {exc}")
        example_questions = []

    logo_base64 = _get_logo_base64()
    st.markdown(
        f"""
        <div style="display:flex;justify-content:center;margin-top:1rem;margin-bottom:0.75rem;">
            <img src="data:image/png;base64,{logo_base64}" alt="Viktoria Buchholz Logo" style="width:156px;display:block;" />
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<h2 style='text-align:center;margin-top:0;'>Buchholz KI-Assistent</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#2e7d32;'>Frage den Daten-Assistenten nach aktuellen Insights.</p>", unsafe_allow_html=True)

    cols = st.columns(3, gap="large")
    for idx, col in enumerate(cols):
        with col:
            label = example_questions[idx] if idx < len(example_questions) else f"Frage {idx + 1}"
            if st.button(label, key=f"sample_q_{idx}", use_container_width=True):
                _add_message("user", label)
                answer = _run_agent(agent, label)
                _add_message("assistant", answer)
                st.rerun()

    chat_box = st.container()
    with chat_box:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not st.session_state.buchholz_messages:
            st.info("Stelle eine Frage oder wähle eine der vorgeschlagenen Optionen.")
        for message in st.session_state.buchholz_messages:
            _chat_message("user" if message["role"] == "user" else "assistant", message["content"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    with st.form("buchholz_chat_form", clear_on_submit=True):
        user_input = st.text_input("Texteingabe", key="buchholz_input", label_visibility="collapsed")
        submitted = st.form_submit_button("Senden", use_container_width=True)
        if submitted and user_input.strip():
            text = user_input.strip()
            _add_message("user", text)
            with st.spinner("Agent denkt nach..."):
                answer = _run_agent(agent, text)
            _add_message("assistant", answer)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
