import unittest

from lib.company_analysis import CompanyAnalyzer
from lib.data_collection import DataCollectionError, DataCollector
from lib.financial_analysis import FinancialAnalyzer
from lib.news_analysis import NewsAnalyzer
from lib.simulation import InvestmentSimulator


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.last_kwargs = None

    def get(self, *args, **kwargs):
        self.last_kwargs = kwargs
        return FakeResponse(self.payload)


class DataCollectorTests(unittest.TestCase):
    def test_news_key_is_sent_in_header_not_query(self) -> None:
        session = FakeSession({"status": "ok", "articles": []})
        collector = DataCollector(
            news_api_key="secret",
            alpha_vantage_api_key="alpha",
            session=session,
        )
        collector.collect_news_data("semiconductor")
        self.assertEqual(session.last_kwargs["headers"]["X-Api-Key"], "secret")
        self.assertNotIn("apiKey", session.last_kwargs["params"])

    def test_api_error_payload_fails_closed(self) -> None:
        session = FakeSession({"Note": "rate limit"})
        collector = DataCollector(alpha_vantage_api_key="alpha", session=session)
        with self.assertRaises(DataCollectionError):
            collector.collect_financial_data(["IBM"])


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.financial = {
            "IBM": {
                "provider": "alpha_vantage",
                "payload": {
                    "Symbol": "IBM",
                    "Name": "International Business Machines",
                    "MarketCapitalization": "1000",
                    "RevenueTTM": "500",
                    "ProfitMargin": "0.10",
                    "LatestQuarter": "2026-06-30",
                },
            }
        }

    def test_company_analysis_contains_no_dummy_text(self) -> None:
        result = CompanyAnalyzer().analyze_companies(["IBM"], self.financial)[0]
        self.assertEqual(result["symbol"], "IBM")
        self.assertNotIn("ダミー", str(result))

    def test_financial_analysis_parses_numbers(self) -> None:
        result = FinancialAnalyzer().analyze_financials(self.financial)[0]
        self.assertEqual(result["market_capitalization"], 1000.0)
        self.assertEqual(result["profit_margin"], 0.10)

    def test_unimplemented_sentiment_does_not_fake_result(self) -> None:
        with self.assertRaises(NotImplementedError):
            NewsAnalyzer().perform_sentiment_analysis([])

    def test_raw_close_backtest_is_labelled_non_recommendation(self) -> None:
        market = {
            "IBM": {
                "price_semantics": "raw_unadjusted_close",
                "payload": {
                    "Time Series (Daily)": {
                        "2026-01-02": {"4. close": "100"},
                        "2026-01-03": {"4. close": "110"},
                        "2026-01-04": {"4. close": "105"},
                    }
                },
            }
        }
        simulator = InvestmentSimulator()
        result = simulator.evaluate_strategies(
            simulator.simulate_investment_strategies(market)
        )[0]
        self.assertEqual(result["evaluation_status"], "descriptive_not_recommendation")
        self.assertFalse(result["dividends_included"])


if __name__ == "__main__":
    unittest.main()
