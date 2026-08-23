#!/usr/bin/env python3
"""Validate canonical consumer-AI API outputs."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "api" / "v1" / "ai-consumer"


def load(root: Path, name: str) -> object:
    return json.loads((root / name).read_text(encoding="utf-8"))


def validate(root: Path) -> dict[str, int]:
    metrics_doc = load(root, "metrics.json")
    features_doc = load(root, "features.json")
    comparison = load(root, "comparison.json")
    signals = load(root, "openai-signals.json")
    manifest = load(root, "manifest.json")
    index = load(root, "index.json")

    metrics = metrics_doc["observations"]
    features = features_doc["events"]

    assert {row["provider"] for row in metrics} == {"OpenAI", "Google", "Meta"}
    assert {row["provider"] for row in features} == {"OpenAI", "Google", "Meta"}
    assert len(metrics) >= 18

    dates = sorted(date.fromisoformat(row["as_of"]) for row in metrics)
    assert (dates[-1] - dates[0]).days >= 365
    assert all(
        row["definition"] and row["geography"] and row["period"] and row["source_url"]
        for row in metrics
    )
    assert all(
        row["definition"] and row["geography"] and row["source_url"]
        and row["published_at"] and row["status"]
        for row in features
    )

    assert "never converted" in comparison["rule"]
    assert signals["files"]
    assert manifest["primary_source_count"] == 18

    openai_blocked = 0
    for item in manifest["sources"]:
        assert item["claim_count"] > 0 and len(item["claim_sha256"]) == 64
        host = urlparse(item["url"]).hostname
        if host == "openai.com":
            assert item["retrieval_status"] in {"ok", "origin_blocked_403"}
            if item["retrieval_status"] == "origin_blocked_403":
                openai_blocked += 1
                assert item["http_status"] == 403
                assert item["sha256"] is None and item["bytes"] is None
            else:
                assert item["http_status"] == 200
                assert item["sha256"] and item["bytes"] > 0
        else:
            assert item["retrieval_status"] == "ok"
            assert item["http_status"] == 200 and item["sha256"] and item["bytes"] > 0

    bundle = manifest["openai_signals_bundle"]
    assert bundle["sha256"] and bundle["bytes"] > 0
    assert bundle["url"].startswith("https://cdn.openai.com/")

    expected_datasets = {
        "metrics": "metrics.json",
        "features": "features.json",
        "comparison": "comparison.json",
        "openai_signals": "openai-signals.json",
    }
    assert index["datasets"] == expected_datasets

    return {
        "metrics": len(metrics),
        "features": len(features),
        "primary_sources": manifest["primary_source_count"],
        "openai_blocked_pages": openai_blocked,
        "signals_files": len(signals["files"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    print(json.dumps(validate(args.root), sort_keys=True))


if __name__ == "__main__":
    main()
