import os
from data_collection import DataCollector
from news_analysis import NewsAnalyzer
from company_analysis import CompanyAnalyzer
from financial_analysis import FinancialAnalyzer
from report_generation import ReportGenerator
from simulation import InvestmentSimulator

def main():
    # 必要なファイルの作成
    create_necessary_files()

    investment_theme = input("投資テーマを入力してください: ")

    data_collector = DataCollector()
    news_analyzer = NewsAnalyzer()
    company_analyzer = CompanyAnalyzer()
    financial_analyzer = FinancialAnalyzer()
    report_generator = ReportGenerator()
    investment_simulator = InvestmentSimulator()

    # データ収集
    news_data = data_collector.collect_news_data(investment_theme)
    company_names = news_analyzer.extract_companies(news_data)
    company_data = data_collector.collect_company_data(company_names)
    financial_data = data_collector.collect_financial_data(company_names)

    # ニュース分析
    news_analysis_results = news_analyzer.analyze_news_content(news_data)
    news_analyzer.save_news_analysis_results(news_analysis_results)

    # 企業分析
    company_analysis_results = company_analyzer.analyze_company_info(company_data)
    company_analyzer.analyze_financial_statements(financial_data)
    company_analyzer.save_company_analysis_results(company_analysis_results)

    # 財務分析
    valuation_metrics = financial_analyzer.calculate_valuation_metrics(financial_data)
    financial_analyzer.compare_with_industry_average(valuation_metrics)
    dcf_valuation_results = financial_analyzer.perform_dcf_valuation(financial_data, growth_forecast)
    anomalies = financial_analyzer.detect_anomalies(financial_data)
    financial_analyzer.save_financial_analysis_results(financial_analysis_results)

    # レポート生成
    markdown_report = report_generator.generate_markdown_report(analysis_results)
    visualizations = report_generator.generate_visualizations(analysis_results)
    interactive_report = report_generator.generate_interactive_report(markdown_report, visualizations)
    investment_suggestions = report_generator.provide_investment_suggestions(analysis_results)

    # 投資シミュレーション
    historical_data = investment_simulator.load_historical_price_data(company_names)
    backtest_results = investment_simulator.backtest_investment_strategies(historical_data, strategies)
    risk_return_evaluation = investment_simulator.evaluate_risk_return(backtest_results)
    optimal_strategy = investment_simulator.propose_optimal_strategy(risk_return_evaluation)

    # レポートの共有
    share_report_on_slack(interactive_report)

if __name__ == "__main__":
    main()