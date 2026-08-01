from __future__ import annotations

import argparse
from datetime import datetime, timezone

from lib.company_analysis import CompanyAnalyzer
from lib.data_collection import DataCollector
from lib.financial_analysis import FinancialAnalyzer
from lib.news_analysis import NewsAnalyzer
from lib.report_generation import ReportGenerator
from lib.simulation import InvestmentSimulator


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Collect observed news and Alpha Vantage fields for explicitly supplied "
            "symbols. No sentiment, entity inference, valuation, forecast, or strategy "
            "optimization is performed."
        )
    )
    parser.add_argument("theme", help="News search theme")
    parser.add_argument(
        "--symbol",
        action="append",
        required=True,
        help="Verified market symbol. Repeat for multiple companies.",
    )
    parser.add_argument("--news-page-size", type=int, default=20)
    arguments = parser.parse_args()

    symbols = list(dict.fromkeys(symbol.upper() for symbol in arguments.symbol))
    collector = DataCollector()
    news_analyzer = NewsAnalyzer()
    company_analyzer = CompanyAnalyzer()
    financial_analyzer = FinancialAnalyzer()
    simulator = InvestmentSimulator()
    report_generator = ReportGenerator()

    news = collector.collect_news_data(
        arguments.theme, page_size=arguments.news_page_size
    )
    news_summary = news_analyzer.summarize_articles(news)
    news_analyzer.save_analysis_results(
        news_summary, "data/news_analysis/articles.json"
    )

    financial_data = collector.collect_financial_data(symbols)
    market_data = collector.collect_stock_price_data(symbols)

    company_results = company_analyzer.analyze_companies(symbols, financial_data)
    company_analyzer.save_analysis_results(
        company_results, "data/company_analysis/results.csv"
    )

    financial_results = financial_analyzer.analyze_financials(financial_data)
    anomaly_flags = financial_analyzer.detect_anomalies(financial_data)
    financial_analyzer.save_analysis_results(
        financial_results, "data/financial_analysis/results.csv"
    )
    financial_analyzer.save_analysis_results(
        anomaly_flags, "data/financial_analysis/quality_flags.csv"
    )

    simulation_results = simulator.evaluate_strategies(
        simulator.simulate_investment_strategies(market_data)
    )
    simulator.save_simulation_results(
        simulation_results, "data/simulations/results.csv"
    )

    report = report_generator.generate_report(
        {
            "metadata": {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "theme": arguments.theme,
                "symbols": symbols,
                "news_provider": "NewsAPI",
                "financial_provider": "Alpha Vantage OVERVIEW",
                "market_provider": "Alpha Vantage TIME_SERIES_DAILY",
                "market_price_semantics": "raw_unadjusted_close",
                "investment_advice": False,
            },
            "news_summary": news_summary,
            "company_results": company_results,
            "financial_results": financial_results,
            "anomaly_flags": anomaly_flags,
            "simulation_results": simulation_results,
        }
    )
    report_generator.save_report(report, "reports/investment_report.md")


if __name__ == "__main__":
    main()
