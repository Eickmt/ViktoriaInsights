import unittest
from datetime import date

from season_config import (
    get_preseason_standings,
    is_training_date_in_current_season,
    validate_expected_group,
)


class SeasonSwitchTests(unittest.TestCase):
    def test_expected_2627_group_is_accepted(self):
        ok, message = validate_expected_group(get_preseason_standings())
        self.assertTrue(ok, message)

    def test_old_2526_group_is_rejected(self):
        old_group = [
            "FC Neukirchen-Vluyn",
            "Duisburger FV 08",
            "VfL Repelen",
            "Duisburger SV 1900",
            "Mülheimer SV 07",
            "TuS Viktoria Buchholz",
            "Rheinland Hamborn",
            "SC 1920 Oberhausen",
            "SuS 21 Oberhausen",
            "SV Genc Osman Duisburg",
            "Tus Asterlagen",
            "GSG Duisburg",
            "SuS 09 Dinslaken",
            "SV Rhenania Hamborn",
            "VFB Homberg II.",
            "Spvgg. Meiderich 06/95",
            "Schwarz-Weiss Alstaden",
            "1. FC Mülheim",
        ]
        standings = [{"team_name": team, "position": index} for index, team in enumerate(old_group, start=1)]
        ok, _ = validate_expected_group(standings)
        self.assertFalse(ok)

    def test_wrong_team_count_is_rejected(self):
        standings = get_preseason_standings()[:-1]
        ok, _ = validate_expected_group(standings)
        self.assertFalse(ok)

    def test_training_cutoff_includes_july_first(self):
        self.assertFalse(is_training_date_in_current_season(date(2026, 6, 30)))
        self.assertTrue(is_training_date_in_current_season(date(2026, 7, 1)))
        self.assertTrue(is_training_date_in_current_season(date(2026, 7, 2)))


if __name__ == "__main__":
    unittest.main()
