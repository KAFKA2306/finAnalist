from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


class InvestmentSimulator:
    """Alpha Vantageのraw closeを使う単純な買持ち記述バックテスト。"""

    @staticmethod
    def _close_series(record: Mapping[str, Any]) -> pd.Series:
        payload = record.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError("Invalid market-data payload")
        raw = payload.get("Time Series (Daily)")
        if not isinstance(raw, Mapping) or not raw:
            raise ValueError("Missing Time Series (Daily)")
        observations = {}
        for date, values in raw.items():
            if not isinstance(values, Mapping):
                continue
            try:
                close = float(values["4. close"])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(close) and close > 0:
                observations[pd.Timestamp(date)] = close
        series = pd.Series(observations, dtype=float).sort_index()
        if series.index.has_duplicates or len(series) < 2:
            raise ValueError("At least two unique close observations are required")
        return series

    def simulate_investment_strategies(
        self, stock_price_data: Mapping[str, Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        results = []
        for symbol, record in sorted(stock_price_data.items()):
            close = self._close_series(record)
            returns = close.pct_change(fill_method=None).dropna()
            wealth = (1 + returns).cumprod()
            drawdown = wealth / wealth.cummax() - 1
            annualized_volatility = float(returns.std(ddof=0) * np.sqrt(252))
            results.append(
                {
                    "symbol": symbol,
                    "strategy": "buy_and_hold_raw_close",
                    "first_date": close.index.min().date().isoformat(),
                    "last_date": close.index.max().date().isoformat(),
                    "observations": int(len(close)),
                    "total_price_return": float(close.iloc[-1] / close.iloc[0] - 1),
                    "annualized_volatility": annualized_volatility,
                    "max_drawdown": float(drawdown.min()),
                    "price_semantics": record.get(
                        "price_semantics", "raw_unadjusted_close"
                    ),
                    "dividends_included": False,
                    "splits_adjusted": False,
                }
            )
        return results

    def evaluate_strategies(self, simulation_results):
        output = []
        for row in simulation_results:
            evaluated = dict(row)
            evaluated["evaluation_status"] = "descriptive_not_recommendation"
            evaluated["selection_status"] = "no_strategy_optimization_performed"
            output.append(evaluated)
        return output

    def save_simulation_results(self, results, file_path: str) -> None:
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
