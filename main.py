# -*- coding: utf-8 -*-
from lib.data_collection import DataCollector
from lib.news_analysis import NewsAnalyzer
from lib.company_analysis import CompanyAnalyzer
from lib.financial_analysis import FinancialAnalyzer
from lib.report_generation import ReportGenerator
from lib.simulation import InvestmentSimulator

def main():
    investment_theme = input("投資テーマを入力してください: ")

    data_collector = DataCollector()
    news_analyzer = NewsAnalyzer()
    company_analyzer = CompanyAnalyzer()
    financial_analyzer = FinancialAnalyzer()
    report_generator = ReportGenerator()
    investment_simulator = InvestmentSimulator()

    news_data = data_collector.collect_news_data(investment_theme)
    tweet_data = data_collector.collect_twitter_data(investment_theme)

    related_companies = news_analyzer.extract_related_companies(news_data)
    sentiment_results = news_analyzer.perform_sentiment_analysis(news_data)
    news_analyzer.save_analysis_results(sentiment_results, "data/news_analysis/sentiment.json")

    financial_data = data_collector.collect_financial_data(related_companies)
    stock_price_data = data_collector.collect_stock_price_data(related_companies)

    company_analysis_results = company_analyzer.analyze_companies(related_companies, financial_data)
    company_analyzer.save_analysis_results(company_analysis_results, "data/company_analysis/results.csv")

    financial_analysis_results = financial_analyzer.analyze_financials(financial_data)
    anomalies = financial_analyzer.detect_anomalies(financial_data)
    financial_analyzer.save_analysis_results(financial_analysis_results, "data/financial_analysis/results.csv")

    report = report_generator.generate_report({
        "sentiment_results": sentiment_results,
        "company_analysis_results": company_analysis_results,
        "financial_analysis_results": financial_analysis_results,
        "anomalies": anomalies
    })
    report_generator.save_report(report, "reports/investment_report.md")
    report_generator.save_visualizations({
        "sentiment_chart": sentiment_results,
        "financial_chart": financial_analysis_results
    }, "reports/visualizations")

    simulation_results = investment_simulator.simulate_investment_strategies(stock_price_data)
    evaluated_strategies = investment_simulator.evaluate_strategies(simulation_results)
    investment_simulator.save_simulation_results(evaluated_strategies, "data/simulations/results.csv")

if __name__ == "__main__":
    main()