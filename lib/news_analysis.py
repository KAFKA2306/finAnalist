from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


class NewsAnalyzer:
    """ニュースAPIの観測メタデータを記述集計する。

    企業抽出やセンチメント分類は、モデル・プロンプト・評価データ・出力スキーマが
    未実装のため行わない。古いtext-davinci-002/Claude complete呼出しへ暗黙に依存
    して分析結果を生成しない。
    """

    def summarize_articles(self, news_data: Iterable[dict[str, Any]]) -> dict[str, Any]:
        articles = [article for article in news_data if isinstance(article, dict)]
        sources = Counter()
        dated = 0
        missing_title = 0
        records = []
        for article in articles:
            source = article.get("source")
            source_name = source.get("name") if isinstance(source, dict) else None
            if source_name:
                sources[str(source_name)] += 1
            if article.get("publishedAt"):
                dated += 1
            if not article.get("title"):
                missing_title += 1
            records.append(
                {
                    "title": article.get("title"),
                    "source": source_name,
                    "published_at": article.get("publishedAt"),
                    "url": article.get("url"),
                    "description": article.get("description"),
                }
            )
        return {
            "article_count": len(records),
            "dated_article_count": dated,
            "missing_title_count": missing_title,
            "source_counts": dict(sorted(sources.items())),
            "records": records,
            "sentiment_status": "not_computed",
            "company_extraction_status": "not_computed",
        }

    def extract_related_companies(self, news_data):
        raise NotImplementedError(
            "Automatic company extraction is disabled. Supply verified market symbols "
            "explicitly until an evaluated entity-linking adapter is implemented."
        )

    def perform_sentiment_analysis(self, news_data):
        raise NotImplementedError(
            "Sentiment analysis is disabled until a labelled evaluation set, model "
            "version, prompt, confidence policy, and abstention rule are implemented."
        )

    def save_analysis_results(self, results: dict[str, Any], file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
