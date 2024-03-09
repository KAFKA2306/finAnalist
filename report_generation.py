
import matplotlib.pyplot as plt
import plotly.express as px

class ReportGenerator:
    def __init__(self):
        pass

    def generate_markdown_report(self, analysis_results):
        report = "# Investment Theme Analysis Report\n\n"
        
        # ニュース分析結果
        report += "## News Analysis\n\n"
        for i, result in enumerate(analysis_results['news_analysis'], start=1):
            report += f"### Article {i}\n\n"
            report += result + "\n\n"
        
        # 企業分析結果
        report += "## Company Analysis\n\n"
        for name, result in analysis_results['company_analysis'].items():
            report += f"### {name}\n\n"
            report += result + "\n\n"
        
        # 財務分析結果
        report += "## Financial Analysis\n\n"
        for name, result in analysis_results['financial_analysis'].items():
            report += f"### {name}\n\n"
            report += f"- Valuation Metrics: {result['valuation_metrics']}\n"
            report += f"- Industry Comparison: {result['industry_comparison']}\n"
            report += f"- DCF Valuation: {result['dcf_valuation']}\n"
            report += f"- Anomalies: {result['anomalies']}\n\n"
        
        # 投資判断の提示
        report += "## Investment Suggestions\n\n"
        for suggestion in analysis_results['investment_suggestions']:
            report += f"- {suggestion}\n"
        
        return report

    def generate_visualizations(self, analysis_results):
        visualizations = []
        
        # 企業の財務指標の推移
        for name, result in analysis_results['financial_analysis'].items():
            revenue = result['revenue']
            profit = result['profit']
            fig = px.line(x=list(range(len(revenue))), y=[revenue, profit], labels={'x': 'Year', 'y': 'Amount'},
                        title=f"{name} - Revenue and Profit")
            fig.update_layout(legend_title_text='Metric')
            fig.update_traces(textposition="bottom right")
            visualizations.append(fig)
        
        return visualizations

    def generate_interactive_report(self, markdown_report, visualizations):
        # Plotlyを使用してインタラクティブなレポートを生成
        report = markdown_report
        for fig in visualizations:
            report += f"\n\n{fig.to_html(full_html=False)}\n\n"
        
        with open("investment_theme_report.html", "w") as file:
            file.write(report)

    def provide_investment_suggestions(self, analysis_results):
        suggestions = []
        
        # ニュース分析に基づく提案
        positive_news = [result for result in analysis_results['news_analysis'] if "positive" in result.lower()]
        if len(positive_news) > 0:
            suggestions.append("Consider investing in companies with positive news sentiment.")
        
        # 企業分析に基づく提案
        for name, result in analysis_results['company_analysis'].items():
            if "strong financial performance" in result.lower():
                suggestions.append(f"Consider investing in {name} due to its strong financial performance.")
        
        # バリュエーション分析に基づく提案
        for name, result in analysis_results['financial_analysis'].items():
            if result['valuation_metrics']['pe_ratio'] < 15 and result['valuation_metrics']['ps_ratio'] < 1.5:
                suggestions.append(f"{name} appears undervalued based on its P/E and P/S ratios.")
        
        return suggestions
