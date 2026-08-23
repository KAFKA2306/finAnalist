#!/usr/bin/env python3
"""Validate canonical consumer-AI API outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "api" / "v1" / "ai-consumer"
PROVIDERS = {"OpenAI", "Google", "Meta"}
AVAILABILITY_STATES = {"announced", "experiment", "rolling_out", "generally_available"}
DATASETS = {
    "metrics": "metrics.json",
    "features": "features.json",
    "changes": "changes.json",
    "comparison": "comparison.json",
    "openai_signals": "openai-signals.json",
}


def read(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> dict[str, int]:
    metric_payload = read(root, "metrics.json")
    feature_payload = read(root, "features.json")
    metrics = metric_payload["observations"]
    features = feature_payload["events"]
    changes = read(root, "changes.json")
    comparison = read(root, "comparison.json")
    signals = read(root, "openai-signals.json")
    manifest = read(root, "manifest.json")
    index = read(root, "index.json")

    assert {row["provider"] for row in metrics} == PROVIDERS
    assert {row["provider"] for row in features} == PROVIDERS
    assert len(metrics) >= 18
    assert len(features) >= 12
    dates = [date.fromisoformat(row["as_of"]) for row in metrics]
    assert (max(dates) - min(dates)).days >= 365
    assert all(all(row[key] for key in ("definition", "geography", "period", "source_url")) for row in metrics)
    assert all(all(row[key] for key in ("definition", "geography", "source_url", "published_at", "status", "availability_state", "surfaces")) for row in features)
    assert all(row["availability_state"] in AVAILABILITY_STATES for row in features)
    assert all(isinstance(row["surfaces"], list) and row["surfaces"] for row in features)
    assert max(row["published_at"] for row in features) >= "2026-08-20"
    assert "never converted" in comparison["rule"] and signals["files"]
    assert index["schema_version"] == 2 and index["datasets"] == DATASETS

    assert changes["schema_version"] == 1
    assert changes["status"] in {"verified_change", "no_verified_change"}
    assert changes["retrieved_at"] == metric_payload["retrieved_at"] == feature_payload["retrieved_at"]
    assert "Retrieval timestamps" in changes["rule"]
    for collection in ("feature_changes", "metric_changes"):
        assert isinstance(changes[collection], list)
        for item in changes[collection]:
            assert item["change_type"] in {"added", "removed", "corrected"}
            assert item["record"]["provider"] in PROVIDERS

    expected_urls = {row["source_url"] for row in metrics + features}
    manifest_urls = {item["url"] for item in manifest["sources"]}
    assert manifest["primary_source_count"] == len(expected_urls)
    assert manifest_urls == expected_urls

    blocked = 0
    for item in manifest["sources"]:
        assert item["claim_count"] > 0 and len(item["claim_sha256"]) == 64
        if urlparse(item["url"]).hostname == "openai.com" and item["retrieval_status"] == "origin_blocked_403":
            blocked += 1
            assert item["http_status"] == 403 and item["sha256"] is None and item["bytes"] is None
        else:
            assert item["retrieval_status"] == "ok"
            assert item["http_status"] == 200 and item["sha256"] and item["bytes"] > 0

    for name, metadata in manifest["files"].items():
        path = root / name
        assert path.is_file()
        assert path.stat().st_size == metadata["bytes"]
        assert digest(path) == metadata["sha256"]

    bundle = manifest["openai_signals_bundle"]
    assert bundle["sha256"] and bundle["bytes"] > 0 and bundle["url"].startswith("https://cdn.openai.com/")
    return {
        "metrics": len(metrics), "features": len(features),
        "feature_changes": len(changes["feature_changes"]),
        "metric_changes": len(changes["metric_changes"]),
        "primary_sources": manifest["primary_source_count"],
        "openai_blocked_pages": blocked, "signals_files": len(signals["files"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    print(json.dumps(validate(parser.parse_args().root), sort_keys=True))


if __name__ == "__main__":
    main()
