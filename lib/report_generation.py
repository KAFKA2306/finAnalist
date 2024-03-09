# -*- coding: utf-8 -*-
import markdown

class ReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, analysis_results):
        # 分析結果を基にレポートを生成
        report = "# 投資レポート\n\n"
        
        if analysis_results.get("sentiment_results"):
            report += "## センチメント分析結果\n"
            report += f"ポジティブ: {analysis_results['sentiment_results'].get('positive', 0)}\n"
            report += f"ネガティブ: {analysis_results['sentiment_results'].get('negative', 0)}\n"
            report += f"ニュートラル: {analysis_results['sentiment_results'].get('neutral', 0)}\n"
        
        # 他の分析結果も同様に追加
        return report

    def save_report(self, report, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(report)

    def save_visualizations(self, visualizations, folder_path):
        # ここでは、グラフの保存をスキップする例を示します。
        pass