from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping


class CompanyAnalyzer:
    FIELDS = [
        "symbol",
        "name",
        "asset_type",
        "exchange",
        "currency",
        "country",
        "sector",
        "industry",
        "latest_quarter",
        "description",
        "provider",
        "analysis_status",
    ]

    def analyze_companies(
        self,
        companies,
        financial_data: Mapping[str, Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for raw_symbol in companies or []:
            symbol = str(raw_symbol).upper()
            if symbol not in financial_data:
                raise ValueError(f"No financial observation for {symbol}")
            results.append(self.analyze_company(symbol, financial_data[symbol]))
        return results

    def analyze_company(
        self, company: str, financial_record: Mapping[str, Any]
    ) -> dict[str, Any]:
        payload = financial_record.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError(f"Invalid company payload for {company}")
        return {
            "symbol": company,
            "name": payload.get("Name"),
            "asset_type": payload.get("AssetType"),
            "exchange": payload.get("Exchange"),
            "currency": payload.get("Currency"),
            "country": payload.get("Country"),
            "sector": payload.get("Sector"),
            "industry": payload.get("Industry"),
            "latest_quarter": payload.get("LatestQuarter"),
            "description": payload.get("Description"),
            "provider": financial_record.get("provider"),
            "analysis_status": "observed_fields_only_no_llm_inference",
        }

    def save_analysis_results(self, results, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
