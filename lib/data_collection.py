from __future__ import annotations

import os
import re
from typing import Any, Iterable

import requests


class DataCollectionError(RuntimeError):
    pass


class DataCollector:
    """NewsAPIとAlpha Vantageの観測値を出典別に取得する。

    異なるプロバイダーのJSONを同じ辞書へ上書き結合せず、API失敗時に空値や
    ダミーデータへ置換しない。
    """

    NEWS_URL = "https://newsapi.org/v2/everything"
    ALPHA_URL = "https://www.alphavantage.co/query"
    SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.:-]{1,24}$")

    def __init__(
        self,
        news_api_key: str | None = None,
        alpha_vantage_api_key: str | None = None,
        session: requests.Session | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.news_api_key = news_api_key or os.getenv("NEWS_API_KEY", "")
        self.alpha_vantage_api_key = alpha_vantage_api_key or os.getenv(
            "ALPHA_VANTAGE_API_KEY", ""
        )
        self.session = session or requests.Session()
        self.timeout_seconds = timeout_seconds
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    @staticmethod
    def _require_key(value: str, name: str) -> str:
        if not value:
            raise DataCollectionError(f"{name} is required")
        return value

    @classmethod
    def _symbol(cls, value: str) -> str:
        symbol = str(value).strip().upper()
        if not cls.SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError(f"Invalid market symbol: {value!r}")
        return symbol

    def _get_json(
        self,
        url: str,
        *,
        params: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise DataCollectionError(f"Non-JSON response from {url}") from exc
        if not isinstance(payload, dict):
            raise DataCollectionError(f"Unexpected payload type from {url}")

        error = (
            payload.get("Error Message")
            or payload.get("Information")
            or payload.get("Note")
        )
        if error:
            raise DataCollectionError(str(error))
        if payload.get("status") == "error":
            raise DataCollectionError(str(payload.get("message", "NewsAPI error")))
        return payload

    def collect_news_data(self, theme: str, page_size: int = 20) -> list[dict[str, Any]]:
        query = str(theme).strip()
        if not query:
            raise ValueError("theme must not be empty")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        key = self._require_key(self.news_api_key, "NEWS_API_KEY")
        payload = self._get_json(
            self.NEWS_URL,
            params={
                "q": query,
                "searchIn": "title,description",
                "sortBy": "publishedAt",
                "pageSize": page_size,
                "language": "en",
            },
            headers={"X-Api-Key": key},
        )
        articles = payload.get("articles")
        if not isinstance(articles, list):
            raise DataCollectionError("NewsAPI response has no articles list")
        return [article for article in articles if isinstance(article, dict)]

    def collect_twitter_data(self, theme: str) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "Twitter/X collection is disabled until an authenticated API adapter, "
            "rate-limit policy, and provenance schema are implemented."
        )

    def _alpha(self, function: str, symbol: str, **extra: Any) -> dict[str, Any]:
        key = self._require_key(
            self.alpha_vantage_api_key, "ALPHA_VANTAGE_API_KEY"
        )
        return self._get_json(
            self.ALPHA_URL,
            params={
                "function": function,
                "symbol": self._symbol(symbol),
                "apikey": key,
                **extra,
            },
        )

    def collect_financial_data(
        self, companies: Iterable[str]
    ) -> dict[str, dict[str, Any]]:
        output: dict[str, dict[str, Any]] = {}
        for raw_symbol in companies:
            symbol = self._symbol(raw_symbol)
            overview = self._alpha("OVERVIEW", symbol)
            if not overview or overview.get("Symbol") not in {None, symbol}:
                raise DataCollectionError(f"Invalid OVERVIEW response for {symbol}")
            output[symbol] = {
                "provider": "alpha_vantage",
                "function": "OVERVIEW",
                "payload": overview,
            }
        return output

    def collect_stock_price_data(
        self, companies: Iterable[str], outputsize: str = "full"
    ) -> dict[str, dict[str, Any]]:
        if outputsize not in {"compact", "full"}:
            raise ValueError("outputsize must be compact or full")
        output: dict[str, dict[str, Any]] = {}
        for raw_symbol in companies:
            symbol = self._symbol(raw_symbol)
            payload = self._alpha(
                "TIME_SERIES_DAILY", symbol, outputsize=outputsize
            )
            series = payload.get("Time Series (Daily)")
            if not isinstance(series, dict) or not series:
                raise DataCollectionError(
                    f"TIME_SERIES_DAILY response missing observations for {symbol}"
                )
            output[symbol] = {
                "provider": "alpha_vantage",
                "function": "TIME_SERIES_DAILY",
                "price_semantics": "raw_unadjusted_close",
                "payload": payload,
            }
        return output
