from datetime import date
import unittest

from memento_mori_calendar import calculate_life_stats


class LifeStatsTest(unittest.TestCase):
    def test_age_on_may_15_2026(self) -> None:
        stats = calculate_life_stats(today=date(2026, 5, 15), lifespan_years=90)

        self.assertEqual(stats.age_years, 26)
        self.assertEqual(stats.age_days_after_birthday, 29)
        self.assertEqual(stats.birth_date, date(2000, 4, 16))
        self.assertEqual(stats.next_birthday, date(2027, 4, 16))
        self.assertEqual(stats.total_weeks, 4680)


if __name__ == "__main__":
    unittest.main()
