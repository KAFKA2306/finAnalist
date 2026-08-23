#!/usr/bin/env python3
"""Validate canonical consumer-AI API outputs."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "api" / "v1" / "ai-consumer"
PROVIDERS = {"OpenAI", "Google", "Meta"}
DATASETS = {
    "metrics": "metrics.json",
    "features": "features.json",
    "comparison": "comparison.json",
    "openai_signals": "openai-signals.json",
}


def read(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def validate(root: Path) -> dict[str, int]:
    metrics = read(root, "metrics.json")["observations"]
    features = read(root, "features.json")["events"]
    comparison = read(root, "comparison.json")
    signals = read(root, "openai-signals.json")
    manifest = read(root, "manifest.json")
    index = read(root, "index.json")

    assert {row["provider"] for row in metrics} == PROVIDERS
    assert {row["provider"] for row in features} == PROVIDERS
    assert len(metrics) >= 18
    dates = [date.fromisoformat(row["as_of"]) for row in metrics]
    assert (max(dates) - min(dates)).days >= 365
    assert all(all(row[key] for key in ("definition", "geography", "period", "source_url")) for row in metrics)
    assert all(all(row[key] for key in ("definition", "geography", "source_url", "published_at", "status")) for row in features)
    assert "never converted" in comparison["rule"] and signals["files"]
    assert manifest["primary_source_count"] == 18 and index["datasets"] == DATASETS

    blocked = 0
    for item in manifest["sources"]:
        assert item["claim_count"] > 0 and len(item["claim_sha256"]) == 64
        if urlparse(item["url"]).hostname == "openai.com" and item["retrieval_status"] == "origin_blocked_403":
            blocked += 1
            assert item["http_status"] == 403 and item["sha256"] is None and item["bytes"] is None
        else:
            assert item["retrieval_status"] == "ok"
            assert item["http_status"] == 200 and item["sha256"] and item["bytes"] > 0

    bundle = manifest["openai_signals_bundle"]
    assert bundle["sha256"] and bundle["bytes"] > 0 and bundle["url"].startswith("https://cdn.openai.com/")
    return {
        "metrics": len(metrics), "features": len(features),
        "primary_sources": manifest["primary_source_count"],
        "openai_blocked_pages": blocked, "signals_files": len(signals["files"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    print(json.dumps(validate(parser.parse_args().root), sort_keys=True))


if __name__ == "__main__":
    main()
