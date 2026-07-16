from datetime import date
import re
import unicodedata

CURRENT_STANDINGS_SEASON = "2627"
CURRENT_MATCH_SEASON = "26/27"
SEASON_DISPLAY = "2026/27"
TRAINING_SEASON_START = date(2026, 7, 1)
SEASON_MATCH_START = date(2026, 8, 16)

EXPECTED_GROUP_TEAMS = [
    "TuS Viktoria Buchholz",
    "MH-Styrum",
    "GSG Duisburg",
    "Mülheimer SV II",
    "FC Taxi",
    "SC Croatia",
    "TuSpo Saarn",
    "Mündelheim",
    "DSC Preußen",
    "Bissingheim",
    "SV Duissern",
    "SV Heißen",
    "SG DU-Süd",
    "SV Wanheim",
    "Dümpten",
]

_EXPECTED_TEAM_ALIASES = {
    "TuS Viktoria Buchholz": ["v buchholz", "viktoria buchholz", "tus viktoria buchholz"],
    "MH-Styrum": ["mh styrum", "mh-styrum"],
    "GSG Duisburg": ["gsg duisburg"],
    "Mülheimer SV II": ["mulheimer sv ii", "muelheimer sv ii", "mulheimer sv 2", "muelheimer sv 2"],
    "FC Taxi": ["fc taxi", "fc taxi duisburg"],
    "SC Croatia": ["sc croatia"],
    "TuSpo Saarn": ["tuspo saarn"],
    "Mündelheim": ["mundelheim", "muendelheim"],
    "DSC Preußen": ["dsc preussen", "dsc preußen"],
    "Bissingheim": ["bissingheim"],
    "SV Duissern": ["sv duissern"],
    "SV Heißen": ["sv heissen", "sv heißen"],
    "SG DU-Süd": ["sg du sud", "sg du-sud", "sg du süd", "sg du-süd"],
    "SV Wanheim": ["sv wanheim"],
    "Dümpten": ["dumpten", "duempten"],
}


def normalize_team_name(team_name: str) -> str:
    """Normalize team names for resilient fussball.de group comparisons."""
    normalized = unicodedata.normalize("NFKD", str(team_name).casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.replace("ß", "ss")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


EXPECTED_GROUP_TEAM_KEYS = {
    normalize_team_name(alias)
    for aliases in _EXPECTED_TEAM_ALIASES.values()
    for alias in aliases
}


def get_expected_group_team_keys() -> set[str]:
    return set(EXPECTED_GROUP_TEAM_KEYS)


def validate_expected_group(standings_data: list[dict]) -> tuple[bool, str]:
    scraped_keys = {
        normalize_team_name(team.get("team_name", ""))
        for team in standings_data
        if team.get("team_name")
    }

    matched_expected = set()
    for expected_team, aliases in _EXPECTED_TEAM_ALIASES.items():
        alias_keys = {normalize_team_name(alias) for alias in aliases}
        if scraped_keys & alias_keys:
            matched_expected.add(expected_team)

    missing = [team for team in EXPECTED_GROUP_TEAMS if team not in matched_expected]
    unexpected = sorted(scraped_keys - EXPECTED_GROUP_TEAM_KEYS)

    if missing:
        return False, f"Erwartete 26/27-Teams fehlen: {', '.join(missing)}"

    if len(standings_data) != len(EXPECTED_GROUP_TEAMS):
        return (
            False,
            f"Teamanzahl passt nicht zur 26/27-Gruppe: {len(standings_data)} statt {len(EXPECTED_GROUP_TEAMS)}",
        )

    if unexpected:
        return False, f"Unerwartete Teams in der 26/27-Tabelle: {', '.join(unexpected)}"

    return True, "Teamliste passt zur 26/27-Gruppe"


def get_preseason_standings() -> list[dict]:
    return [
        {
            "position": index,
            "team_name": team_name,
            "games_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
            "match_day": 0,
        }
        for index, team_name in enumerate(EXPECTED_GROUP_TEAMS, start=1)
    ]


def get_preseason_viktoria_info() -> dict[str, str]:
    viktoria = get_preseason_standings()[0]
    return {
        "platz": f"{viktoria['position']}.",
        "punkte": str(viktoria["points"]),
        "spiele": str(viktoria["games_played"]),
        "siege": str(viktoria["wins"]),
        "unentschieden": str(viktoria["draws"]),
        "niederlagen": str(viktoria["losses"]),
        "tore_geschossen": str(viktoria["goals_for"]),
        "tore_erhalten": str(viktoria["goals_against"]),
        "tordifferenz": str(viktoria["goal_difference"]),
    }


def is_training_date_in_current_season(training_date: date) -> bool:
    return training_date >= TRAINING_SEASON_START
