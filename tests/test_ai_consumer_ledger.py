import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))
SPEC = importlib.util.spec_from_file_location("update_ai_consumer", ROOT / "research" / "update_ai_consumer.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class AiConsumerLedgerTest(unittest.TestCase):
    def test_three_primary_providers_and_full_metric_contract(self):
        MODULE.validate_records()
        self.assertEqual({row["provider"] for row in MODULE.METRICS}, {"OpenAI", "Google", "Meta"})
        for row in MODULE.METRICS:
            self.assertTrue(row["definition"])
            self.assertTrue(row["geography"])
            self.assertTrue(row["period"])
            self.assertTrue(row["source_url"].startswith("https://"))

    def test_history_spans_more_than_twelve_months(self):
        dates = sorted(date.fromisoformat(row["as_of"]) for row in MODULE.METRICS)
        self.assertGreaterEqual((dates[-1] - dates[0]).days, 365)

    def test_usage_and_feature_events_are_separate(self):
        self.assertTrue(MODULE.METRICS)
        self.assertTrue(MODULE.FEATURES)
        self.assertTrue(all("metric" in row and "capability" not in row for row in MODULE.METRICS))
        self.assertTrue(all("capability" in row and "metric" not in row for row in MODULE.FEATURES))

    def test_feature_events_expose_availability_and_surfaces(self):
        allowed = {"announced", "experiment", "rolling_out", "generally_available"}
        self.assertTrue(all(row["availability_state"] in allowed for row in MODULE.FEATURES))
        self.assertTrue(all(isinstance(row["surfaces"], list) and row["surfaces"] for row in MODULE.FEATURES))
        self.assertTrue(any(row["published_at"].startswith("2026-") for row in MODULE.FEATURES))

    def test_comparison_never_converts_weekly_to_monthly(self):
        view = MODULE.comparison_view()
        openai = [row for row in view["observations"] if row["provider"] == "OpenAI"]
        metrics = {row["metric"] for row in openai}
        self.assertIn("weekly_active_users", metrics)
        self.assertNotIn("monthly_active_users", metrics)
        self.assertIn("never converted", view["rule"])

    def test_semantic_diff_ignores_retrieval_only_refresh(self):
        previous = {
            "retrieved_at": "2026-08-21T00:00:00+00:00",
            "events": [dict(MODULE.FEATURES[0])],
        }
        current = {
            "retrieved_at": "2026-08-23T00:00:00+00:00",
            "events": [dict(MODULE.FEATURES[0])],
        }
        diff = MODULE.semantic_diff(previous, current, kind="feature")
        self.assertEqual(diff, [])

    def test_semantic_diff_reports_added_feature(self):
        previous = {"retrieved_at": "2026-08-21T00:00:00+00:00", "events": []}
        current = {
            "retrieved_at": "2026-08-23T00:00:00+00:00",
            "events": [dict(MODULE.FEATURES[0])],
        }
        diff = MODULE.semantic_diff(previous, current, kind="feature")
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0]["change_type"], "added")
        self.assertEqual(diff[0]["record"]["capability"], MODULE.FEATURES[0]["capability"])

    def test_only_official_source_domains_are_used(self):
        urls = {row["source_url"] for row in MODULE.METRICS + MODULE.FEATURES}
        self.assertFalse(any("similarweb" in url or "statista" in url or "semrush" in url for url in urls))
        self.assertTrue(any(url.startswith("https://openai.com/") or url.startswith("https://help.openai.com/") for url in urls))
        self.assertTrue(any(url.startswith("https://blog.google/") for url in urls))
        self.assertTrue(any(url.startswith("https://about.fb.com/") for url in urls))


if __name__ == "__main__":
    unittest.main()
