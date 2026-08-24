import json
import tempfile
import unittest
from pathlib import Path

from research.update_ai_economics import build, normalize
from research.validate_ai_economics import validate


class AiEconomicsTest(unittest.TestCase):
    def test_source_classes_are_not_collapsed(self):
        raw = {"entity": "OpenAI", "product": None, "metric": "tracked_arr", "value": 44.3, "unit": "USD_billion_per_year", "qualifier": "estimate", "as_of": "2026-08-12", "measurement_type": "third_party_estimate", "source_name": "TickerTrends", "source_url": "https://example.com/source"}
        row = normalize(raw, "2026-08-24T00:00:00Z")
        self.assertEqual(row["measurement_type"], "third_party_estimate")
        self.assertEqual(row["currency"], "USD")

    def test_range_and_native_currency_are_preserved(self):
        ranged = normalize({"entity": "DeepSeek", "metric": "annualized_revenue_run_rate", "value_min": 0.4, "value_max": 0.5, "unit": "USD_billion_per_year", "qualifier": "reported_range", "as_of": "2026-07", "measurement_type": "media_reported", "source_name": "Reuters", "source_url": "https://example.com/deepseek"}, "2026-08-24T00:00:00Z")
        self.assertIsNone(ranged["value"])
        self.assertEqual((ranged["value_min"], ranged["value_max"]), (0.4, 0.5))
        self.assertEqual(ranged["currency"], "USD")
        native = normalize({"entity": "Zhipu AI (Z.ai)", "metric": "annual_revenue", "value": 0.724, "unit": "CNY_billion", "qualifier": "reported", "as_of": "2025", "measurement_type": "media_reported", "source_name": "Reuters", "source_url": "https://example.com/zhipu"}, "2026-08-24T00:00:00Z")
        self.assertEqual(native["currency"], "CNY")
        self.assertEqual(native["value"], 0.724)

    def test_build_is_idempotent_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            build(first, fetch_sources=False)
            validate(first)
            build(second, previous=first, fetch_sources=False)
            validate(second)
            names = ["index.json", "observations.ndjson", "latest.json", "comparables.json", "sources.json", "candidates.json", "manifest.json"]
            for name in names:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)

    def test_gaps_are_not_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "out"
            build(root, fetch_sources=False)
            rows = [json.loads(line) for line in (root / "observations.ndjson").read_text().splitlines() if line]
            providers = {row["provider"] for row in rows}
            self.assertNotIn("Google DeepMind / Gemini", providers)
            self.assertNotIn("Meta AI", providers)


if __name__ == "__main__":
    unittest.main()
