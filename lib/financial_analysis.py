from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Mapping


class FinancialAnalyzer:
    METRICS = {
        "market_capitalization": "MarketCapitalization",
        "pe_ratio": "PERatio",
        "price_to_book_ratio": "PriceToBookRatio",
        "return_on_equity_ttm": "ReturnOnEquityTTM",
        "revenue_ttm": "RevenueTTM",
        "profit_margin": "ProfitMargin",
        "quarterly_revenue_growth_yoy": "QuarterlyRevenueGrowthYOY",
        "quarterly_earnings_growth_yoy": "QuarterlyEarningsGrowthYOY",
        "dividend_yield": "DividendYield",
        "beta": "Beta",
    }

    @staticmethod
    def _optional_number(value: Any) -> float | None:
        if value in {None, "", "None", "-"}:
            return None
        try:
            result = float(value)
        except (TypeError, ValueError):
            return None
        return result if math.isfinite(result) else None

    def analyze_financials(
        self, financial_data: Mapping[str, Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        results = []
        for symbol, record in sorted(financial_data.items()):
            payload = record.get("payload")
            if not isinstance(payload, Mapping):
                raise ValueError(f"Invalid financial payload for {symbol}")
            row: dict[str, Any] = {
                "symbol": symbol,
                "provider": record.get("provider"),
                "observation_quarter": payload.get("LatestQuarter"),
                "analysis_status": "descriptive_provider_fields_only",
            }
            for output_name, provider_name in self.METRICS.items():
                row[output_name] = self._optional_number(payload.get(provider_name))
            results.append(row)
        return results

    def detect_anomalies(
        self, financial_data: Mapping[str, Mapping[str, Any]]
    ) -> list[dict[str, str]]:
        flags: list[dict[str, str]] = []
        for row in self.analyze_financials(financial_data):
            symbol = str(row["symbol"])
            required = ("market_capitalization", "revenue_ttm", "profit_margin")
            for field in required:
                if row[field] is None:
                    flags.append(
                        {
                            "symbol": symbol,
                            "field": field,
                            "flag": "missing_provider_value",
                            "severity": "warning",
                        }
                    )
            market_cap = row["market_capitalization"]
            revenue = row["revenue_ttm"]
            if market_cap is not None and market_cap < 0:
                flags.append(
                    {
                        "symbol": symbol,
                        "field": "market_capitalization",
                        "flag": "negative_value",
                        "severity": "error",
                    }
                )
            if revenue is not None and revenue < 0:
                flags.append(
                    {
                        "symbol": symbol,
                        "field": "revenue_ttm",
                        "flag": "negative_value",
                        "severity": "error",
                    }
                )
        return flags

    def save_analysis_results(self, results, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = list(results)
        fieldnames = sorted({key for row in rows for key in row}) if rows else []
        with path.open("w", newline="", encoding="utf-8") as file:
            if not fieldnames:
                return
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
