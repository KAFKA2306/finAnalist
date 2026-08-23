#!/usr/bin/env python3
"""Build consumer-AI adoption and capability ledgers from official sources only."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from collect_openai_signals import collect as collect_signals, download as download_signals

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "api" / "v1" / "ai-consumer"
UA = "ai-consumer/1.0 github.com/KAFKA2306/finAnalist"

METRICS: list[dict[str, Any]] = [
    {"provider":"OpenAI","product":"ChatGPT","metric":"weekly_active_users","value":250_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"weekly","as_of":"2024-10-02","definition":"People worldwide using ChatGPT each week.","source_url":"https://openai.com/index/scale-the-benefits-of-ai/"},
    {"provider":"OpenAI","product":"ChatGPT","metric":"weekly_active_users","value":300_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"weekly","as_of":"2025-02-04","definition":"Weekly active users worldwide.","source_url":"https://openai.com/index/openai-and-the-csu-system/"},
    {"provider":"OpenAI","product":"ChatGPT image generation","metric":"feature_users","value":130_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"first_week","as_of":"2025-04-23","definition":"Users who created images during the first week after ChatGPT image generation launch.","source_url":"https://openai.com/index/image-generation-api/"},
    {"provider":"OpenAI","product":"ChatGPT image generation","metric":"images_created","value":700_000_000,"unit":"images","qualifier":"greater_than","geography":"global","period":"first_week","as_of":"2025-04-23","definition":"Images created during the first week after ChatGPT image generation launch.","source_url":"https://openai.com/index/image-generation-api/"},
    {"provider":"OpenAI","product":"ChatGPT","metric":"weekly_active_users","value":700_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"weekly","as_of":"2025-09-29","definition":"People using ChatGPT each week.","source_url":"https://openai.com/index/buy-it-in-chatgpt/"},
    {"provider":"OpenAI","product":"ChatGPT","metric":"weekly_active_users","value":900_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"weekly","as_of":"2026-02-27","definition":"Weekly active ChatGPT users.","source_url":"https://openai.com/index/scaling-ai-for-everyone/"},
    {"provider":"OpenAI","product":"ChatGPT","metric":"consumer_subscribers","value":50_000_000,"unit":"subscribers","qualifier":"greater_than","geography":"global","period":"current_as_of_date","as_of":"2026-02-27","definition":"Consumer subscribers, explicitly distinguished from paying business users in the source.","source_url":"https://openai.com/index/scaling-ai-for-everyone/"},
    {"provider":"Google","product":"AI Overviews","metric":"monthly_active_users","value":1_000_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2024-10-28","definition":"Global users reached every month after expansion to more than 100 countries and territories.","source_url":"https://blog.google/products-and-platforms/products/search/ai-overviews-search-october-2024/"},
    {"provider":"Google","product":"AI Overviews","metric":"monthly_active_users","value":1_500_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2025-04-24","definition":"Users per month reported in Alphabet Q1 2025 CEO remarks.","source_url":"https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q1-2025/"},
    {"provider":"Google","product":"AI Mode","metric":"monthly_active_users","value":1_000_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2026-05-19","definition":"Monthly active users globally.","source_url":"https://blog.google/products-and-platforms/products/search/ai-mode-us-insights/"},
    {"provider":"Google","product":"AI Mode","metric":"planning_query_growth_relative_to_all_ai_mode_queries","value":80,"unit":"percent_faster_growth","qualifier":"reported","geography":"United States","period":"previous_6_months","as_of":"2026-05-19","definition":"Growth rate of planning-related AI Mode queries relative to overall AI Mode query growth.","source_url":"https://blog.google/products-and-platforms/products/search/ai-mode-us-insights/"},
    {"provider":"Google","product":"AI Overviews","metric":"monthly_active_users","value":2_500_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2026-06-03","definition":"Monthly active users.","source_url":"https://blog.google/products-and-platforms/products/search/new-controls-website-owners/"},
    {"provider":"Meta","product":"Meta AI","metric":"monthly_active_users","value":400_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2024-09-25","definition":"People using Meta AI monthly across Meta products.","source_url":"https://about.fb.com/news/2024/09/metas-ai-product-news-connect/"},
    {"provider":"Meta","product":"Meta AI","metric":"weekly_active_users","value":185_000_000,"unit":"users","qualifier":"reported","geography":"global","period":"weekly","as_of":"2024-09-25","definition":"People using Meta AI across Meta products each week.","source_url":"https://about.fb.com/news/2024/09/metas-ai-product-news-connect/"},
    {"provider":"Meta","product":"Meta AI","metric":"monthly_active_users","value":500_000_000,"unit":"users","qualifier":"nearly","geography":"global","period":"monthly","as_of":"2024-10-09","definition":"Active users monthly after expansion to additional countries and languages.","source_url":"https://about.fb.com/news/2024/07/meta-ai-is-now-multilingual-more-creative-and-smarter/"},
    {"provider":"Meta","product":"Meta AI","metric":"monthly_active_users","value":600_000_000,"unit":"users","qualifier":"nearly","geography":"global","period":"monthly","as_of":"2024-12-27","definition":"Monthly active users reported in Meta's 2024 year review.","source_url":"https://about.fb.com/news/2024/12/our-year-in-review-metas-2024-highlights/"},
    {"provider":"Meta","product":"Meta AI","metric":"monthly_active_users","value":700_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2025-03-19","definition":"Monthly active users reported at the start of the European rollout.","source_url":"https://about.fb.com/news/2025/03/europe-meet-your-newest-assistant-meta-ai/"},
    {"provider":"Meta","product":"Meta AI","metric":"monthly_active_users","value":1_000_000_000,"unit":"users","qualifier":"greater_than","geography":"global","period":"monthly","as_of":"2025-10-01","definition":"People using Meta AI every month.","source_url":"https://about.fb.com/news/2025/10/improving-your-recommendations-apps-ai-meta/"},
]

FEATURES: list[dict[str, Any]] = [
    {"provider":"OpenAI","product":"ChatGPT","capability":"native_image_generation","event_type":"feature_launch","status":"launched","availability_state":"rolling_out","geography":"global","surfaces":["ChatGPT"],"published_at":"2025-03-25","definition":"4o image generation began rolling out in ChatGPT to Plus, Pro, Team and Free users.","source_url":"https://openai.com/index/introducing-4o-image-generation/"},
    {"provider":"OpenAI","product":"ChatGPT","capability":"instant_checkout","event_type":"commerce_launch","status":"launched","availability_state":"generally_available","geography":"United States","surfaces":["ChatGPT"],"published_at":"2025-09-29","definition":"U.S. Plus, Pro and Free users could buy from U.S. Etsy sellers directly in chat; additional merchants were announced as coming soon.","source_url":"https://openai.com/index/buy-it-in-chatgpt/"},
    {"provider":"OpenAI","product":"ChatGPT","capability":"interactive_quizzes","event_type":"feature_expansion","status":"launched","availability_state":"generally_available","geography":"supported_markets","surfaces":["ChatGPT web","ChatGPT mobile"],"published_at":"2026-08-14","definition":"Interactive quizzes became available to all consumer ChatGPT plans and Edu plans on web and mobile.","source_url":"https://openai.com/products/release-notes/"},
    {"provider":"OpenAI","product":"ChatGPT","capability":"apple_messages_plugin","event_type":"plugin_launch","status":"launched","availability_state":"generally_available","geography":"not_specified_by_source","surfaces":["ChatGPT desktop app for macOS"],"published_at":"2026-08-20","definition":"The Apple Messages plugin became available on all plans in the ChatGPT desktop app for macOS.","source_url":"https://openai.com/products/release-notes/"},
    {"provider":"Google","product":"AI Mode","capability":"reasoning_search","event_type":"product_stage","status":"experiment","availability_state":"experiment","geography":"United States","surfaces":["AI Mode in Google Search"],"published_at":"2025-03-05","definition":"AI Mode introduced as an experimental Search experience.","source_url":"https://blog.google/products-and-platforms/products/search/ai-mode-search/"},
    {"provider":"Google","product":"AI Mode","capability":"general_us_availability","event_type":"rollout","status":"launched","availability_state":"rolling_out","geography":"United States","surfaces":["AI Mode in Google Search"],"published_at":"2025-05-20","definition":"AI Mode began rolling out to everyone in the United States.","source_url":"https://blog.google/products-and-platforms/products/search/google-search-ai-mode-update/"},
    {"provider":"Google","product":"AI Mode","capability":"agentic_tasks_and_shopping","event_type":"capability_announcement","status":"announced","availability_state":"announced","geography":"United States","surfaces":["AI Mode in Google Search"],"published_at":"2025-05-20","definition":"Google announced agentic capabilities for tickets, reservations, appointments and shopping; announced capabilities are not recorded as actual usage.","source_url":"https://blog.google/products-and-platforms/products/search/google-search-ai-mode-update/"},
    {"provider":"Google","product":"AI Mode","capability":"connected_apps","event_type":"feature_expansion","status":"rolling_out","availability_state":"rolling_out","geography":"United States","surfaces":["AI Mode in Google Search"],"published_at":"2026-07-16","definition":"Connected apps including Instacart, Canva and YouTube Music started rolling out in AI Mode in the United States.","source_url":"https://blog.google/products-and-platforms/products/search/connected-apps/"},
    {"provider":"Meta","product":"Meta AI","capability":"voice_and_photo_multimodal","event_type":"feature_expansion","status":"launched","availability_state":"rolling_out","geography":"multiple_markets","surfaces":["Meta AI"],"published_at":"2024-09-25","definition":"Voice interaction and photo sharing/editing capabilities expanded in Meta AI.","source_url":"https://about.fb.com/news/2024/09/metas-ai-product-news-connect/"},
    {"provider":"Meta","product":"Meta AI","capability":"europe_chat_rollout","event_type":"rollout","status":"rolling_out","availability_state":"rolling_out","geography":"41 European countries and 21 overseas territories","surfaces":["Facebook","Instagram","WhatsApp","Messenger"],"published_at":"2025-03-19","definition":"Meta AI chat began rolling out in Europe through Facebook, Instagram, WhatsApp and Messenger.","source_url":"https://about.fb.com/news/2025/03/europe-meet-your-newest-assistant-meta-ai/"},
    {"provider":"Meta","product":"Meta AI","capability":"standalone_app","event_type":"product_launch","status":"launched","availability_state":"generally_available","geography":"supported_markets","surfaces":["Meta AI app","meta.ai","Meta AI glasses"],"published_at":"2025-04-29","definition":"First standalone Meta AI app launched, connected to meta.ai and Meta AI glasses.","source_url":"https://about.fb.com/news/2025/04/introducing-meta-ai-app-new-way-access-ai-assistant/"},
    {"provider":"Meta","product":"Meta AI","capability":"agentic_tasks_connected_apps","event_type":"feature_expansion","status":"rolling_out","availability_state":"rolling_out","geography":"select_markets","surfaces":["Meta AI app","meta.ai"],"published_at":"2026-07-24","definition":"Planning, email and calendar connections, research, slides and recurring tasks started rolling out in select markets.","source_url":"https://about.fb.com/news/2026/07/meta-ai-muse-spark-doesnt-just-think-it-acts/"},
]

ALLOWED_HOSTS = {"openai.com", "blog.google", "about.fb.com"}
AVAILABILITY_STATES = {"announced", "experiment", "rolling_out", "generally_available"}
FEATURE_SEMANTIC_FIELDS = (
    "provider", "product", "capability", "event_type", "status", "geography",
    "published_at", "definition", "source_url",
)
METRIC_SEMANTIC_FIELDS = (
    "provider", "product", "metric", "value", "unit", "qualifier", "geography",
    "period", "as_of", "definition", "source_url",
)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = response.read()
    if not raw:
        raise ValueError(f"empty official source: {url}")
    return raw


def validate_records() -> None:
    providers = {row["provider"] for row in METRICS}
    if providers != {"OpenAI", "Google", "Meta"}:
        raise ValueError(f"expected OpenAI/Google/Meta, got {providers}")
    required = {"provider","product","metric","value","unit","qualifier","geography","period","as_of","definition","source_url"}
    for row in METRICS:
        if required - row.keys():
            raise ValueError(f"metric missing fields: {row}")
        if not row["source_url"].startswith("https://"):
            raise ValueError(f"non-https source: {row['source_url']}")
    feature_required = {"provider","product","capability","event_type","status","availability_state","geography","surfaces","published_at","definition","source_url"}
    for row in FEATURES:
        if feature_required - row.keys():
            raise ValueError(f"feature missing fields: {row}")
        if row["availability_state"] not in AVAILABILITY_STATES:
            raise ValueError(f"invalid availability state: {row}")
        if not isinstance(row["surfaces"], list) or not row["surfaces"]:
            raise ValueError(f"feature surfaces missing: {row}")
    dates = [date.fromisoformat(row["as_of"]) for row in METRICS]
    if (max(dates) - min(dates)).days < 365:
        raise ValueError("official metric history must span at least 12 months")


def claim_records(url: str) -> list[dict[str, Any]]:
    records = [row for row in METRICS + FEATURES if row["source_url"] == url]
    return sorted(
        records,
        key=lambda row: (
            row["provider"],
            str(row.get("metric", row.get("capability", ""))),
            str(row.get("as_of", row.get("published_at", ""))),
        ),
    )


def source_manifest() -> list[dict[str, object]]:
    urls = sorted({row["source_url"] for row in METRICS + FEATURES})
    items: list[dict[str, object]] = []
    for url in urls:
        host = urlparse(url).hostname or ""
        if host not in ALLOWED_HOSTS:
            raise ValueError(f"non-primary source domain: {url}")
        claims = claim_records(url)
        item: dict[str, object] = {
            "url": url,
            "claim_count": len(claims),
            "claim_sha256": sha256(canonical_json(claims)),
        }
        try:
            raw = fetch(url)
        except urllib.error.HTTPError as exc:
            if host == "openai.com" and exc.code == 403:
                item.update({
                    "retrieval_status": "origin_blocked_403",
                    "http_status": 403,
                    "bytes": None,
                    "sha256": None,
                })
            else:
                raise
        else:
            item.update({
                "retrieval_status": "ok",
                "http_status": 200,
                "bytes": len(raw),
                "sha256": sha256(raw),
            })
        items.append(item)
    return items


def comparison_view() -> dict[str, object]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in METRICS:
        key = (row["provider"], row["metric"])
        if key not in latest or row["as_of"] > latest[key]["as_of"]:
            latest[key] = row
    return {
        "schema_version": 1,
        "rule": "Latest disclosed observation per provider and metric definition; weekly and monthly user metrics are never converted into each other.",
        "observations": [latest[key] for key in sorted(latest)],
    }


def _rows(payload: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return list(payload.get("events" if kind == "feature" else "observations", []))


def _key(row: dict[str, Any], kind: str) -> tuple[str, ...]:
    if kind == "feature":
        return (row["provider"], row["product"], row["capability"], row["published_at"])
    if kind == "metric":
        return (row["provider"], row["product"], row["metric"], row["as_of"])
    raise ValueError(f"unsupported semantic diff kind: {kind}")


def _semantic(row: dict[str, Any], kind: str) -> dict[str, Any]:
    fields = FEATURE_SEMANTIC_FIELDS if kind == "feature" else METRIC_SEMANTIC_FIELDS
    return {field: row.get(field) for field in fields}


def semantic_diff(previous: dict[str, Any], current: dict[str, Any], *, kind: str) -> list[dict[str, Any]]:
    """Compare claims only; retrieval timestamps and source-page hashes never create a change."""
    before = {_key(row, kind): row for row in _rows(previous, kind)}
    after = {_key(row, kind): row for row in _rows(current, kind)}
    changes: list[dict[str, Any]] = []
    for key in sorted(set(before) | set(after)):
        if key not in before:
            changes.append({"change_type": "added", "record": after[key]})
        elif key not in after:
            changes.append({"change_type": "removed", "record": before[key]})
        elif _semantic(before[key], kind) != _semantic(after[key], kind):
            changes.append({"change_type": "corrected", "before": before[key], "record": after[key]})
    date_field = "published_at" if kind == "feature" else "as_of"
    return sorted(changes, key=lambda item: item["record"][date_field], reverse=True)


def _read_previous(root: Path | None, name: str, collection: str) -> dict[str, Any]:
    if root is None:
        return {collection: [], "retrieved_at": None}
    path = root / name
    if not path.exists():
        return {collection: [], "retrieved_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def write(output: Path, previous_root: Path | None = None) -> dict[str, object]:
    validate_records()
    if previous_root is None:
        previous_root = output if output.exists() else (DEFAULT_OUTPUT if DEFAULT_OUTPUT.exists() else None)
    previous_metrics = _read_previous(previous_root, "metrics.json", "observations")
    previous_features = _read_previous(previous_root, "features.json", "events")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    current_metrics = {"schema_version": 1, "retrieved_at": retrieved_at, "observations": METRICS}
    current_features = {"schema_version": 2, "retrieved_at": retrieved_at, "events": FEATURES}
    feature_changes = semantic_diff(previous_features, current_features, kind="feature")
    metric_changes = semantic_diff(previous_metrics, current_metrics, kind="metric")
    changes = {
        "schema_version": 1,
        "retrieved_at": retrieved_at,
        "compared_to_retrieved_at": previous_features.get("retrieved_at") or previous_metrics.get("retrieved_at"),
        "status": "verified_change" if feature_changes or metric_changes else "no_verified_change",
        "feature_changes": feature_changes,
        "metric_changes": metric_changes,
        "rule": "Only semantic canonical claim differences count as changes. Retrieval timestamps and raw source-page hash changes are verification evidence, not product changes.",
    }

    sources = source_manifest()
    signals_raw = download_signals()
    signals = collect_signals(signals_raw)
    output.mkdir(parents=True, exist_ok=True)
    payloads: dict[str, object] = {
        "metrics.json": current_metrics,
        "features.json": current_features,
        "changes.json": changes,
        "comparison.json": comparison_view(),
        "openai-signals.json": signals,
    }
    for name, payload in payloads.items():
        (output / name).write_bytes(canonical_json(payload))
    index = {
        "schema_version": 2,
        "retrieved_at": retrieved_at,
        "datasets": {
            "metrics": "metrics.json",
            "features": "features.json",
            "changes": "changes.json",
            "comparison": "comparison.json",
            "openai_signals": "openai-signals.json",
        },
    }
    (output / "index.json").write_bytes(canonical_json(index))
    manifest = {
        "schema_version": 2,
        "retrieved_at": retrieved_at,
        "primary_source_count": len(sources),
        "sources": sources,
        "openai_signals_bundle": {
            "url": signals["download_url"],
            "source_page": signals["source_page"],
            "sha256": signals["bundle_sha256"],
            "bytes": signals["bundle_bytes"],
        },
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())}
            for path in sorted(output.glob("*.json"))
            if path.name != "manifest.json"
        },
    }
    (output / "manifest.json").write_bytes(canonical_json(manifest))
    return {
        "metric_count": len(METRICS),
        "feature_count": len(FEATURES),
        "feature_changes": len(feature_changes),
        "metric_changes": len(metric_changes),
        "source_count": len(sources),
        "signals_files": len(signals["files"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--previous-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(write(args.output, args.previous_root), ensure_ascii=False))


if __name__ == "__main__":
    main()
