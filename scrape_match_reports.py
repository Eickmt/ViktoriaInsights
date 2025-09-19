#!/usr/bin/env python3
"""
README
======

pip install playwright
pip install fonttools
playwright install
python scrape_match_reports.py --file match_urls.txt
"""

import argparse
import asyncio
import ast
import io
import logging
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import unicodedata
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright
from fontTools.agl import toUnicode
from fontTools.ttLib import TTFont

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    import streamlit as st  # type: ignore
except ImportError:  # noqa: F401
    st = None

try:
    from supabase import Client, create_client

    SUPABASE_AVAILABLE = True
except ImportError:  # noqa: F401
    Client = None  # type: ignore
    create_client = None  # type: ignore
    SUPABASE_AVAILABLE = False

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
TIMEOUT_MS = 25_000
DELAY_RANGE = (0.5, 1.5)
TARGET_TEAM = "tus viktoria buchholz"
COMPETITION_KEYWORD = "bezirksliga"
SEASON_KEYWORD = "25/26"

MATCHES_HEADERS = [
    "match_id",
    "source_url",
    "competition",
    "season",
    "match_date",
    "home_team",
    "away_team",
    "score_home",
    "score_away",
]
EVENTS_HEADERS = [
    "match_id",
    "source_url",
    "minute",
    "phase",
    "type",
    "team_side",
    "player_primary",
    "player_id",
    "player_in",
    "player_id_in",
    "player_out",
    "player_id_out",
    "score_home",
    "score_away",
    "detail",
    "raw",
]
LINEUPS_HEADERS = [
    "match_id",
    "source_url",
    "team_side",
    "team_name",
    "role",
    "number",
    "name",
    "player_id",
    "is_captain",
    "is_goalkeeper",
]

SUPABASE_CLIENT: Optional["Client"] = None
NUMERIC_FIELDS = {
    "matches": {"score_home", "score_away"},
    "events": {"minute", "score_home", "score_away"},
    "lineups": set(),
}


def _resolve_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if st is not None:
        try:
            supabase_url = supabase_url or st.secrets.get("SUPABASE_URL")
        except Exception:  # noqa: BLE001
            pass
        try:
            supabase_key = supabase_key or st.secrets.get("SUPABASE_ANON_KEY")
        except Exception:  # noqa: BLE001
            pass
        try:
            nested = st.secrets.get("supabase", {})
            if isinstance(nested, dict):
                supabase_url = supabase_url or nested.get("SUPABASE_URL")
                supabase_key = supabase_key or nested.get("SUPABASE_ANON_KEY")
        except Exception:  # noqa: BLE001
            pass

    return supabase_url, supabase_key


def get_supabase_client() -> "Client":
    if not SUPABASE_AVAILABLE or create_client is None:
        raise RuntimeError(
            "Supabase-Client ist nicht installiert. Bitte 'pip install supabase' ausführen."
        )

    global SUPABASE_CLIENT
    if SUPABASE_CLIENT is not None:
        return SUPABASE_CLIENT

    supabase_url, supabase_key = _resolve_supabase_credentials()
    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Supabase-Zugangsdaten fehlen. Bitte SUPABASE_URL und SUPABASE_ANON_KEY setzen."
        )

    SUPABASE_CLIENT = create_client(supabase_url, supabase_key)
    return SUPABASE_CLIENT

MINUTE_PATTERN = re.compile(r"(\d+)(?:\+(\d+))?")
SCORE_PATTERN = re.compile(r"(\d+)\s*[:/-]\s*(\d+)")
DATE_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"(\d{1,2}\.\d{1,2}\.\d{4})"), "%d.%m.%Y"),
    (re.compile(r"(\d{1,2}\.\d{1,2}\.\d{2})"), "%d.%m.%y"),
]

FONT_URL_TEMPLATE = "https://www.fussball.de/export.fontface/-/format/ttf/id/{}/type/font"
REFERER_HEADER = {"Referer": "https://www.fussball.de/"}


def extract_match_id(url: str) -> str:
    match = re.search(r"/-/spiel/([A-Za-z0-9]+)", url)
    if match:
        return match.group(1)
    return ""


def format_season_code(code: str) -> str:
    if not code:
        return ""
    code = code.strip()
    if "/" in code:
        return code
    if len(code) == 4 and code.isdigit():
        return f"{code[:2]}/{code[2:]}"
    return code


def clean_text(value: str) -> str:
    if not value:
        return ""
    return " ".join(value.replace("\xa0", " ").split())


class ObfuscationDecoder:
    def __init__(self, request_context) -> None:
        self._request = request_context
        self._cache: Dict[str, Dict[str, str]] = {}

    async def decode_text(self, text: str, font_id: Optional[str]) -> str:
        if not text or not font_id:
            return text or ""
        mapping = await self._get_mapping(font_id)
        if not mapping:
            return text
        return "".join(mapping.get(char, char) for char in text)

    async def decode_fragments(self, fragments: List[Dict[str, Optional[str]]]) -> str:
        parts: List[str] = []
        for fragment in fragments:
            value = fragment.get("text", "")
            font_id = fragment.get("fontId")
            if font_id:
                value = await self.decode_text(value, font_id)
            parts.append(value)
        return "".join(parts)

    async def _get_mapping(self, font_id: str) -> Dict[str, str]:
        if font_id in self._cache:
            return self._cache[font_id]
        url = FONT_URL_TEMPLATE.format(font_id)
        try:
            response = await self._request.get(url, headers=REFERER_HEADER)
        except Exception as exc:  # noqa: BLE001
            logging.warning("Failed to download font %s: %s", font_id, exc)
            self._cache[font_id] = {}
            return {}
        if response.status != 200:
            logging.warning("Font request for %s returned status %s", font_id, response.status)
            self._cache[font_id] = {}
            return {}
        data = await response.body()
        try:
            font = TTFont(io.BytesIO(data))
        except Exception as exc:  # noqa: BLE001
            logging.warning("Unable to parse font %s: %s", font_id, exc)
            self._cache[font_id] = {}
            return {}
        mapping: Dict[str, str] = {}
        cmap = font.getBestCmap()
        for codepoint, glyph_name in cmap.items():
            if codepoint < 32:
                continue
            replacement = toUnicode(glyph_name)
            if not replacement:
                continue
            normalized = unicodedata.normalize("NFKD", replacement)
            cleaned = "".join(ch for ch in normalized if not unicodedata.combining(ch))
            if not cleaned:
                cleaned = replacement
            mapping[chr(codepoint)] = cleaned
        self._cache[font_id] = mapping
        return mapping


def random_delay() -> float:
    return random.uniform(*DELAY_RANGE)


async def dismiss_cookie_banner(page) -> None:
    selectors = [
        "button[data-testid='uc-accept-all-button']",
        "button:has-text('Alle akzeptieren')",
        "button:has-text('Akzeptieren')",
    ]
    for selector in selectors:
        try:
            button = page.locator(selector)
            if await button.count():
                try:
                    await button.first.click(timeout=2000)
                    await asyncio.sleep(random_delay())
                    break
                except PlaywrightTimeoutError:
                    continue
        except PlaywrightTimeoutError:
            continue
    # Attempt to click within shadow DOM if present
    try:
        await page.evaluate(
            """
            () => {
                const root = document.querySelector('#usercentrics-root');
                if (!root) return;
                const search = node => {
                    if (!node) return null;
                    if (node.querySelector) {
                        const btn = node.querySelector('button[data-testid="uc-accept-all-button"]');
                        if (btn) return btn;
                    }
                    if (node.shadowRoot) {
                        return search(node.shadowRoot);
                    }
                    return null;
                };
                const button = search(root) || (root.shadowRoot ? search(root.shadowRoot) : null);
                if (button) {
                    button.click();
                }
                if (root && root.parentElement) {
                    root.style.display = 'none';
                    root.style.pointerEvents = 'none';
                }
            }
            """
        )
        await asyncio.sleep(random_delay())
    except Exception:  # noqa: BLE001
        pass
    try:
        await page.evaluate(
            """
            () => {
                if (document.body) {
                    document.body.classList.remove('overflowHidden');
                    document.body.style.pointerEvents = '';
                }
                const root = document.querySelector('#usercentrics-root');
                if (root) {
                    root.style.display = 'none';
                    root.style.pointerEvents = 'none';
                }
            }
            """
        )
    except Exception:  # noqa: BLE001
        pass


async def open_match_tab(page, keyword: str, label: Optional[str] = None) -> None:
    await dismiss_cookie_banner(page)
    tab_locator = page.locator(f"a[data-tracking-name*='{keyword}']")
    try:
        if await tab_locator.count():
            try:
                await tab_locator.first.click(timeout=2000)
                await asyncio.sleep(random_delay())
                await page.wait_for_load_state("networkidle")
                return
            except PlaywrightTimeoutError:
                pass
    except PlaywrightTimeoutError:
        pass
    if label:
        try:
            text_locator = page.locator(f"text=/{label}/i")
            if await text_locator.count():
                try:
                    await text_locator.first.click(timeout=2000)
                    await asyncio.sleep(random_delay())
                    await page.wait_for_load_state("networkidle")
                except PlaywrightTimeoutError:
                    pass
        except PlaywrightTimeoutError:
            pass


def normalize_record(
    headers: Iterable[str],
    row: Dict[str, str],
    numeric_fields: Optional[Iterable[str]] = None,
) -> Dict[str, Optional[object]]:
    prepared: Dict[str, Optional[object]] = {}
    for key in headers:
        value = row.get(key, "") if isinstance(row, dict) else ""
        if numeric_fields and key in numeric_fields:
            if value in ("", None):
                prepared[key] = None
            else:
                try:
                    prepared[key] = int(value)
                except (ValueError, TypeError):
                    try:
                        prepared[key] = float(value)
                    except (ValueError, TypeError):
                        prepared[key] = None
            continue
        if value == "":
            prepared[key] = None
        else:
            prepared[key] = value
    return prepared


def parse_minute(raw: str) -> Optional[int]:
    if not raw:
        return None
    cleaned = (
        raw.replace("\\xa0", " ")
        .replace("'", "")
        .replace("’", "")
        .replace("′", "")
        .replace("`", "")
        .replace(".", "")
        .strip()
    )
    if not cleaned:
        return None
    match = MINUTE_PATTERN.match(cleaned)
    if match:
        base = int(match.group(1))
        extra = int(match.group(2)) if match.group(2) else 0
        return base + extra
    # fallback: split manually if plus remains
    if "+" in cleaned:
        base_str, extra_str = cleaned.split("+", 1)
        try:
            base = int(base_str)
            extra = int(extra_str)
            return base + extra
        except ValueError:
            return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def parse_score(text: str) -> Tuple[str, str]:
    match = SCORE_PATTERN.search(text)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def has_final_score(match_row: Dict[str, str]) -> bool:
    score_home = match_row.get("score_home")
    score_away = match_row.get("score_away")
    return bool(score_home and score_away)


def parse_date(text: str) -> str:
    cleaned = text.replace("\\xa0", " ")
    for pattern, fmt in DATE_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            try:
                dt = datetime.strptime(match.group(1), fmt)
            except ValueError:
                continue
            return dt.strftime("%Y-%m-%d")
    return ""


async def decode_locator_text(locator, decoder: ObfuscationDecoder) -> str:
    try:
        if await locator.count() == 0:
            return ""
    except PlaywrightTimeoutError:
        return ""

    fragments = await locator.first.evaluate(
        """
        (el) => {
            const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
            const parts = [];
            while (walker.nextNode()) {
                const node = walker.currentNode;
                const parent = node.parentElement;
                let fontId = null;
                if (parent) {
                    fontId = parent.getAttribute('data-obfuscation');
                    if (!fontId && parent.className) {
                        const match = parent.className.match(/results-c-([a-z0-9]+)/i);
                        if (match) {
                            fontId = match[1];
                        }
                    }
                }
                parts.push({ text: node.textContent || '', fontId });
            }
            return parts;
        }
        """
    )
    decoded = await decoder.decode_fragments(fragments)
    return clean_text(decoded)


async def decode_locator_texts(locator, decoder: ObfuscationDecoder) -> List[str]:
    results: List[str] = []
    try:
        count = await locator.count()
    except PlaywrightTimeoutError:
        return results
    for idx in range(count):
        fragments = await locator.nth(idx).evaluate(
            """
            (el) => {
                const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
                const parts = [];
                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    const parent = node.parentElement;
                    let fontId = null;
                    if (parent) {
                        fontId = parent.getAttribute('data-obfuscation');
                        if (!fontId && parent.className) {
                            const match = parent.className.match(/results-c-([a-z0-9]+)/i);
                            if (match) {
                                fontId = match[1];
                            }
                        }
                    }
                    parts.push({ text: node.textContent || '', fontId });
                }
                return parts;
            }
            """
        )
        decoded = await decoder.decode_fragments(fragments)
        results.append(clean_text(decoded))
    return results


def detect_team_side(classes: str) -> str:
    lowered = classes.lower()
    if any(key in lowered for key in ["home", "heim", "left"]):
        return "home"
    if any(key in lowered for key in ["away", "gast", "right"]):
        return "away"
    return "null"


def classify_event(text: str) -> str:
    lowered = text.lower()
    if "gelb-rot" in lowered or "gelbrot" in lowered:
        return "yellow_red"
    if "rote karte" in lowered or "platzverweis" in lowered or lowered.startswith("rot"):
        return "red"
    if "gelbe karte" in lowered or lowered.startswith("gelb"):
        return "yellow"
    if "tor" in lowered or "trifft" in lowered:
        return "goal"
    if "einwechsl" in lowered or "kommt" in lowered:
        return "sub_on"
    if "auswechsl" in lowered or "geht" in lowered:
        return "sub_off"
    return "other"


async def first_non_empty_text(locator_candidates: List) -> str:
    for locator in locator_candidates:
        try:
            count = await locator.count()
        except PlaywrightTimeoutError:
            continue
        if count == 0:
            continue
        text = (await locator.first.inner_text(timeout=1000)).strip()
        if text:
            return text
    return ""


async def extract_match_core(page, decoder: ObfuscationDecoder, url: str) -> Dict[str, str]:
    try:
        page_title = (await page.title()) or ""
    except PlaywrightTimeoutError:
        page_title = ""

    try:
        await page.wait_for_selector(".stage-header", timeout=5000)
    except PlaywrightTimeoutError:
        logging.debug("stage-header not found for %s", url)

    data_vars = await page.evaluate(
        """
        () => ({
            home: window.edHeimmannschaftName || '',
            away: window.edGastmannschaftName || '',
            competition: window.edSpielklasseName || '',
            season: window.edSaison || ''
        })
        """
    )

    competition_header = await decode_locator_text(page.locator(".stage-header .competition"), decoder)
    competition_raw = competition_header or data_vars.get("competition") or ""
    competition = clean_text(competition_raw)
    if not competition:
        competition = clean_text(page_title.split(" Ergebnis:")[0]) if "Ergebnis:" in page_title else competition

    date_text = await decode_locator_text(page.locator(".stage-header .date"), decoder)
    match_date = parse_date(date_text or competition_header)
    if not match_date:
        match_date = parse_date(page_title)

    home_team = data_vars.get("home") or await decode_locator_text(page.locator(".stage-body .team-home .team-name"), decoder)
    away_team = data_vars.get("away") or await decode_locator_text(page.locator(".stage-body .team-away .team-name"), decoder)

    if (not home_team or not away_team) and page_title:
        parts = [p.strip() for p in re.split(r"[-–]", page_title) if p.strip()]
        if len(parts) >= 2:
            home_team = home_team or parts[0]
            away_team = away_team or parts[1]

    score_text = await decode_locator_text(page.locator(".stage-body .end-result"), decoder)
    score_home, score_away = parse_score(score_text)

    if (not score_home or not score_away):
        half_result = await decode_locator_text(page.locator(".stage-body .half-result"), decoder)
        score_home, score_away = parse_score(half_result)
    if (not score_home or not score_away) and page_title:
        score_home, score_away = parse_score(page_title)

    season_formatted = format_season_code(data_vars.get("season", ""))

    return {
        "match_id": extract_match_id(url),
        "source_url": url,
        "competition": competition,
        "season": season_formatted,
        "match_date": match_date,
        "home_team": clean_text(home_team),
        "away_team": clean_text(away_team),
        "score_home": score_home,
        "score_away": score_away,
        "_filter_competition": competition.lower(),
        "_filter_season": (season_formatted or data_vars.get("season", "")).lower(),
    }


async def extract_events(
    page,
    decoder: ObfuscationDecoder,
    url: str,
    match_id: str,
    player_lookup: Dict[str, str],
) -> List[Dict[str, str]]:
    await open_match_tab(page, "spiel_spielverlauf", "Spielverlauf")

    events: List[Dict[str, str]] = []

    meta_locator = page.locator("[data-match-events]")
    meta_entries: List[Dict[str, str]] = []
    section_phase = {
        "first-half": "1H",
        "second-half": "2H",
        "extra-time": "ET",
        "penalty": "PEN",
    }
    try:
        if await meta_locator.count():
            attr = await meta_locator.first.get_attribute("data-match-events")
            if attr:
                parsed = ast.literal_eval(attr)
                for key, phase in section_phase.items():
                    section = parsed.get(key)
                    if isinstance(section, dict):
                        for meta in section.get("events", []):
                            if isinstance(meta, dict):
                                meta_entries.append({**meta, "phase": phase})
    except Exception as exc:  # noqa: BLE001
        logging.debug("Failed to parse match events meta for %s: %s", url, exc)

    row_locator = page.locator(".match-course .row-event")
    try:
        row_count = await row_locator.count()
    except PlaywrightTimeoutError:
        row_count = 0

    type_map = {
        "goal": "goal",
        "yellow-card": "yellow_card",
        "yellowred-card": "yellow_red_card",
        "yellow-red-card": "yellow_red_card",
        "red-card": "red_card",
        "substitute": "substitution",
    }

    for idx in range(row_count):
        row = row_locator.nth(idx)
        meta = meta_entries[idx] if idx < len(meta_entries) else {}
        classes = (await row.get_attribute("class") or "")
        team_side = meta.get("team") or detect_team_side(classes)
        if team_side not in {"home", "away"}:
            team_side = detect_team_side(classes)
        team_side = team_side if team_side in {"home", "away"} else "null"

        minute_text = clean_text(" ".join(await decode_locator_texts(row.locator(".column-time"), decoder)))
        if not minute_text:
            minute_text = meta.get("time", "")
        minute_val = parse_minute(minute_text)

        phase = meta.get("phase", "")
        if not phase and minute_val is not None:
            if minute_val <= 45:
                phase = "1H"
            elif minute_val <= 90:
                phase = "2H"
            elif minute_val <= 120:
                phase = "ET"
            else:
                phase = "PEN"

        player_text = clean_text(await decode_locator_text(row.locator(".column-player"), decoder))
        raw_text = clean_text(await decode_locator_text(row, decoder))
        detail_text = clean_text(await decode_locator_text(row.locator(".event-info"), decoder))

        meta_type = meta.get("type", "")
        event_type = type_map.get(meta_type, classify_event(raw_text))
        if event_type == "substitution" and not player_text:
            event_type = "substitution"

        score_home = ""
        score_away = ""
        score_text = clean_text(await decode_locator_text(row.locator(".column-event"), decoder))
        match_score = SCORE_PATTERN.search(score_text)
        if match_score:
            score_home, score_away = match_score.groups()

        player_primary = player_text
        player_in = ""
        player_out = ""
        player_id_primary = ""
        player_id_in = ""
        player_id_out = ""

        player_ids: List[str] = []
        anchors = row.locator(".column-player a")
        try:
            anchor_count = await anchors.count()
        except PlaywrightTimeoutError:
            anchor_count = 0
        for a_idx in range(anchor_count):
            href = await anchors.nth(a_idx).get_attribute("href") or ""
            id_match = re.search(r"/(?:player-id|userid)/([^/?#]+)", href, re.IGNORECASE)
            if id_match:
                player_ids.append(id_match.group(1))

        if player_ids:
            player_id_primary = player_ids[0]
        if event_type == "substitution":
            if player_ids:
                player_id_in = player_ids[0]
            if len(player_ids) > 1:
                player_id_out = player_ids[1]
        elif player_ids:
            player_id_in = player_ids[0]

        if event_type == "substitution":
            text_without_label = re.sub(r"(?i)auswechslung", "", player_text).strip()
            parts = re.split(r"(?i)\bfür\b", text_without_label)
            if len(parts) >= 2:
                player_in = clean_text(parts[0])
                player_out = clean_text("".join(parts[1:]))
            else:
                player_in = text_without_label
            player_primary = player_in

        if player_id_primary and player_lookup.get(player_id_primary):
            player_primary = player_lookup[player_id_primary]
        if player_id_in and player_lookup.get(player_id_in):
            player_in = player_lookup[player_id_in]
        if player_id_out and player_lookup.get(player_id_out):
            player_out = player_lookup[player_id_out]

        events.append(
            {
                "match_id": match_id,
                "source_url": url,
                "minute": str(minute_val) if minute_val is not None else "",
                "phase": phase,
                "type": event_type,
                "team_side": team_side,
                "player_primary": player_primary,
                "player_id": player_id_primary,
                "player_in": player_in,
                "player_id_in": player_id_in,
                "player_out": player_out,
                "player_id_out": player_id_out,
                "score_home": score_home,
                "score_away": score_away,
                "detail": detail_text,
                "raw": raw_text,
            }
        )

    return events


async def go_to_lineup_tab(page) -> None:
    await open_match_tab(page, "spiel_aufstellung", "Aufstellung")


async def extract_lineups(page, decoder: ObfuscationDecoder, url: str, match_info: Dict[str, str]) -> List[Dict[str, str]]:
    await go_to_lineup_tab(page)
    try:
        await page.wait_for_selector("#match_course_body .match-lineup", timeout=8000)
    except PlaywrightTimeoutError:
        logging.debug("Lineup container not found for %s", url)

    lineups: List[Dict[str, str]] = []

    home_name = match_info.get("home_team", "")
    away_name = match_info.get("away_team", "")

    async def collect_from_section(section_selector: str, role: str) -> None:
        clubs = page.locator(section_selector)
        try:
            count = await clubs.count()
        except PlaywrightTimeoutError:
            count = 0
        for idx in range(count):
            club = clubs.nth(idx)
            team_side = "home" if idx == 0 else "away"
            team_name = home_name if team_side == "home" else away_name
            players = club.locator(".player-wrapper")
            try:
                player_count = await players.count()
            except PlaywrightTimeoutError:
                player_count = 0
            for p_idx in range(player_count):
                player = players.nth(p_idx)
                first_name = clean_text(await decode_locator_text(player.locator(".firstname"), decoder))
                last_name = clean_text(await decode_locator_text(player.locator(".lastname"), decoder))
                combined = " ".join(filter(None, [first_name, last_name]))
                name = combined or clean_text(await decode_locator_text(player.locator(".player-name"), decoder))
                number = clean_text(await decode_locator_text(player.locator(".player-number"), decoder))
                captain_flag = False
                goalkeeper_flag = False
                try:
                    if await player.locator(".captain").count():
                        text = clean_text(await decode_locator_text(player.locator(".captain"), decoder)).upper()
                        captain_flag = "C" in text
                        goalkeeper_flag = "T" in text or "TW" in text
                except PlaywrightTimeoutError:
                    pass
                if not name:
                    continue
                href = await player.get_attribute("href") or ""
                player_id = ""
                if href:
                    id_match = re.search(r"/(?:player-id|userid)/([^/?#]+)", href, re.IGNORECASE)
                    if id_match:
                        player_id = id_match.group(1)
                lineups.append(
                    {
                        "match_id": match_info.get("match_id", ""),
                        "source_url": url,
                        "team_side": team_side,
                        "team_name": team_name,
                        "role": role,
                        "number": number,
                        "name": name,
                        "player_id": player_id,
                        "is_captain": "1" if captain_flag else "0",
                        "is_goalkeeper": "1" if goalkeeper_flag else "0",
                    }
                )

    await collect_from_section("#match_course_body .starting.container .club", "start")
    await collect_from_section("#match_course_body .substitutes .club", "bench")

    return lineups


def passes_filters(match_info: Dict[str, str]) -> bool:
    competition_text = (match_info.get("_filter_competition") or match_info.get("competition") or "").lower()
    if COMPETITION_KEYWORD not in competition_text:
        return False

    season_text = match_info.get("season") or match_info.get("_filter_season", "")
    season_text = season_text.lower()
    normalized = season_text.replace("/", "")
    target = SEASON_KEYWORD.replace("/", "").lower()
    if target not in normalized:
        return False
    home = (match_info.get("home_team") or "").lower()
    away = (match_info.get("away_team") or "").lower()
    if TARGET_TEAM not in home and TARGET_TEAM not in away:
        return False
    return True


async def process_match(context, decoder: ObfuscationDecoder, url: str) -> Tuple[Optional[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    page = await context.new_page()
    try:
        await asyncio.sleep(random_delay())
        await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
        await dismiss_cookie_banner(page)
        await asyncio.sleep(random_delay())
        match_info = await extract_match_core(page, decoder, url)
        if not passes_filters(match_info):
            logging.info("Skipping %s (does not match filters)", url)
            return None, [], []
        match_row = {key: match_info.get(key, "") for key in MATCHES_HEADERS}
        if not has_final_score(match_row):
            logging.info("Skipping %s (no final score yet)", url)
            return None, [], []
        lineups = await extract_lineups(page, decoder, url, match_row)
        player_lookup = {
            entry.get("player_id", ""): entry.get("name", "")
            for entry in lineups
            if entry.get("player_id") and entry.get("name")
        }
        events = await extract_events(
            page,
            decoder,
            url,
            match_row.get("match_id", ""),
            player_lookup,
        )
        return match_row, events, lineups
    except PlaywrightTimeoutError:
        logging.error("Timeout while processing %s", url)
        return None, [], []
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to process %s: %s", url, exc)
        return None, [], []
    finally:
        await page.close()


def persist_records(
    client: "Client",
    table: str,
    headers: Iterable[str],
    rows: Iterable[Dict[str, str]],
    match_id: str,
) -> None:
    if not match_id:
        logging.warning("Cannot persist records for table %s without match_id", table)
        return

    rows = list(rows)
    if not rows:
        return

    numeric_fields = set(NUMERIC_FIELDS.get(table, set()))
    payload = [normalize_record(headers, row, numeric_fields) for row in rows]
    try:
        client.table(table).insert(payload).execute()
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to insert into %s for match %s: %s", table, match_id, exc)


def read_urls_from_file(path: Path) -> List[str]:
    urls: List[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def load_existing_matches(client: "Client") -> Dict[str, Dict[str, str]]:
    existing: Dict[str, Dict[str, str]] = {}
    try:
        response = client.table("matches").select("match_id,score_home,score_away").execute()
    except Exception as exc:  # noqa: BLE001
        logging.warning("Unable to load existing matches from Supabase: %s", exc)
        return existing

    for row in response.data or []:  # type: ignore[attr-defined]
        match_id = (row.get("match_id") or "").strip()
        if not match_id:
            continue
        normalized = {key: ("" if value is None else str(value)) for key, value in row.items()}
        existing[match_id] = normalized
    return existing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape match reports from fussball.de")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--urls", nargs="+", help="Match URLs to scrape")
    group.add_argument("--file", type=str, help="Path to text file with match URLs")
    return parser.parse_args()


async def main_async(args: argparse.Namespace) -> None:
    if args.file:
        url_list = read_urls_from_file(Path(args.file))
    else:
        url_list = args.urls or []
    url_list = [url for url in url_list if url]
    if not url_list:
        logging.warning("No URLs to process")
        return

    supabase_client = get_supabase_client()
    existing_matches = load_existing_matches(supabase_client)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1280, "height": 720})
        context.set_default_timeout(TIMEOUT_MS)
        decoder = ObfuscationDecoder(context.request)
        try:
            for url in url_list:
                match_id = extract_match_id(url)
                if match_id and match_id in existing_matches:
                    logging.info("Skipping %s (already stored)", url)
                    continue
                logging.info("Processing %s", url)
                match_row, events, lineups = await process_match(context, decoder, url)
                if not match_row:
                    continue
                match_id = match_row.get("match_id", "")
                if not match_id:
                    logging.warning("Skipping persistence for %s: missing match_id", url)
                    continue
                persist_records(supabase_client, "matches", MATCHES_HEADERS, [match_row], match_id)
                persist_records(supabase_client, "events", EVENTS_HEADERS, events, match_id)
                persist_records(supabase_client, "lineups", LINEUPS_HEADERS, lineups, match_id)
                if has_final_score(match_row):
                    existing_matches[match_id] = match_row
        finally:
            await context.close()
            await browser.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except RuntimeError as exc:
        logging.error(str(exc))


if __name__ == "__main__":
    main()
