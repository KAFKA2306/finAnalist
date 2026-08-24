from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ALLOWED = {"company_reported", "media_reported", "third_party_estimate", "derived", "modeled"}
REQUIRED = {"provider", "metric", "value", "currency", "unit", "effective_at", "observed_at", "measurement_type", "source_name", "source_url", "methodology", "observation_id"}


def load_json(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> None:
    required_files = {"index.json", "observations.ndjson", "latest.json", "comparables.json", "sources.json", "candidates.json", "manifest.json"}
    missing = [name for name in required_files if not (root / name).exists()]
    assert not missing, f"missing files: {missing}"
    rows = [json.loads(line) for line in (root / "observations.ndjson").read_text().splitlines() if line.strip()]
    assert len(rows) >= 36, len(rows)
    ids = set()
    for row in rows:
        assert REQUIRED <= row.keys(), row
        assert row["measurement_type"] in ALLOWED, row
        assert isinstance(row["value"], (int, float)) and not isinstance(row["value"], bool), row
        assert row["observation_id"] not in ids, row["observation_id"]
        ids.add(row["observation_id"])
    for provider in ("OpenAI", "Anthropic"):
        provider_rows = [r for r in rows if r["provider"] == provider and r.get("product") is None]
        assert len({str(r["effective_at"]) for r in provider_rows}) >= 3, provider
        assert "company_reported" in {r["measurement_type"] for r in provider_rows}, provider
        assert "third_party_estimate" in {r["measurement_type"] for r in provider_rows}, provider
    latest = load_json(root / "latest.json")
    assert latest["series_key"] == ["provider", "product", "metric", "measurement_type"]
    assert all(row["observation_id"] in ids for row in latest["records"])
    comparables = load_json(root / "comparables.json")
    assert any(r["entity"] == "Microsoft" and r["metric"] == "productivity_and_business_processes_annualized_revenue" for r in comparables["records"])
    assert any(r["entity"] == "Adobe" and r["metric"] == "digital_media_arr" for r in comparables["records"])
    assert not any(r["entity"] == "SAP" and r.get("plot_eligible") for r in comparables["records"])
    sources = load_json(root / "sources.json")
    assert all(r.get("url") for r in sources["sources"])
    manifest = load_json(root / "manifest.json")
    for name, expected in manifest["files"].items():
        assert sha(root / name) == expected, name
    assert manifest["observation_count"] == len(rows)
    index = load_json(root / "index.json")
    assert index["observation_count"] == len(rows)
    candidates = load_json(root / "candidates.json")
    assert candidates["status"] == "discovery_only"


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "api/v1/ai-economics")
    validate(root)
    print(json.dumps({"status": "ok", "root": str(root)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
