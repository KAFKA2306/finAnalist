from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


class ReportGenerator:
    def generate_report(self, analysis_results: Mapping[str, Any]) -> str:
        metadata = analysis_results.get("metadata", {})
        company_results = analysis_results.get("company_results", [])
        financial_results = analysis_results.get("financial_results", [])
        anomaly_flags = analysis_results.get("anomaly_flags", [])
        simulations = analysis_results.get("simulation_results", [])
        news_summary = analysis_results.get("news_summary")

        lines = [
            "# 投資テーマ記述レポート",
            "",
            "> 本レポートはAPI観測値の整理であり、投資助言、企業価値評価、将来予測、最適戦略の提案ではありません。",
            "",
            "## 実行情報",
            "",
            "```json",
            json.dumps(metadata, ensure_ascii=False, indent=2, default=str),
            "```",
            "",
        ]
        if news_summary is not None:
            lines.extend(
                [
                    "## ニュース取得結果",
                    "",
                    "センチメント分析と企業名の自動抽出は実施していません。",
                    "",
                    "```json",
                    json.dumps(news_summary, ensure_ascii=False, indent=2, default=str),
                    "```",
                    "",
                ]
            )

        for title, value in (
            ("企業基本情報", company_results),
            ("財務指標", financial_results),
            ("データ品質フラグ", anomaly_flags),
            ("買持ち記述バックテスト", simulations),
        ):
            lines.extend(
                [
                    f"## {title}",
                    "",
                    "```json",
                    json.dumps(value, ensure_ascii=False, indent=2, default=str),
                    "```",
                    "",
                ]
            )
        return "\n".join(lines)

    def save_report(self, report: str, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")

    def save_visualizations(self, visualizations, folder_path: str) -> None:
        raise NotImplementedError(
            "Visualization output is disabled until chart definitions include source, "
            "as-of date, units, and semantic validation."
        )
