from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "research/data/ai-economics/seed_observations.ndjson"
INVENTORY = ROOT / "research/data/ai-economics/source_inventory.json"
COMPARABLES = ROOT / "research/data/ai-economics/comparables.json"
OUTPUT = ROOT / "api/v1/ai-economics"
ALLOWED = {"company_reported", "media_reported", "third_party_estimate", "derived", "modeled"}
DISCOVERY = [
    {"name": "TickerTrends", "url": "https://blog.tickertrends.io/feed", "kind": "rss", "required": False},
    {"name": "OpenAI News", "url": "https://openai.com/news/", "kind": "html", "required": True},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news", "kind": "html", "required": True},
    {"name": "ARK Invest newsletters", "url": "https://www.ark-invest.com/newsletters", "kind": "html", "required": False},
]
KEYWORDS = ("arr", "annual recurring revenue", "annualized revenue", "revenue run rate", "run-rate revenue", "claude code", "codex", "openai", "anthropic")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def read_json(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text()) if path.exists() else default


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def write_ndjson(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def infer_currency(unit: str) -> str | None:
    prefix = unit.split("_", 1)[0].upper() if unit else ""
    return prefix if prefix in {"USD", "EUR", "CNY", "JPY", "GBP"} else None


def normalize(raw: dict[str, Any], observed_at: str) -> dict[str, Any]:
    kind = raw.get("measurement_type")
    if kind not in ALLOWED:
        raise ValueError(f"unsupported measurement_type: {kind}")
    unit = str(raw.get("unit") or "")
    currency = raw.get("currency") or infer_currency(unit)
    value = raw.get("value")
    value_min = raw.get("value_min")
    value_max = raw.get("value_max")
    has_scalar = is_number(value)
    has_range = is_number(value_min) and is_number(value_max) and value_min <= value_max
    if not (has_scalar or has_range):
        raise ValueError(f"observation needs numeric value or ordered numeric range: {raw}")
    row = {
        "provider": raw.get("entity") or raw.get("provider"),
        "product": raw.get("product"),
        "metric": raw.get("metric"),
        "value": value if has_scalar else None,
        "value_min": value_min if has_range else None,
        "value_max": value_max if has_range else None,
        "currency": currency,
        "unit": unit,
        "qualifier": raw.get("qualifier"),
        "effective_at": raw.get("as_of") or raw.get("effective_at"),
        "observed_at": raw.get("observed_at") or observed_at,
        "source_published_at": raw.get("source_published_at"),
        "measurement_type": kind,
        "source_name": raw.get("source_name"),
        "source_url": raw.get("source_url"),
        "methodology": raw.get("methodology") or "source-attributed observation; missing values are not inferred",
        "notes": raw.get("notes") or raw.get("evidence_summary"),
        "confidence": raw.get("confidence"),
    }
    required = ("provider", "metric", "currency", "unit", "effective_at", "observed_at", "source_name", "source_url")
    missing = [key for key in required if row.get(key) in (None, "")]
    if missing:
        raise ValueError(f"missing {missing}: {raw}")
    identity = {key: row.get(key) for key in ("provider", "product", "metric", "value", "value_min", "value_max", "currency", "unit", "qualifier", "effective_at", "measurement_type", "source_url")}
    row["observation_id"] = sha(stable(identity))
    return row


def latest(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: dict[tuple[str, str | None, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["provider"], row.get("product"), row["metric"], row["measurement_type"])
        if key not in out or str(row["effective_at"]) > str(out[key]["effective_at"]):
            out[key] = row
    return sorted(out.values(), key=lambda r: (r["provider"], r.get("product") or "", r["metric"], r["measurement_type"]))


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.href = None; self.parts: list[str] = []; self.links: list[tuple[str, str]] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a": self.href = dict(attrs).get("href"); self.parts = []
    def handle_data(self, data: str) -> None:
        if self.href is not None: self.parts.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.href is not None:
            text = " ".join(" ".join(self.parts).split())
            if text: self.links.append((self.href, text))
            self.href = None; self.parts = []


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "finAnalist-ai-economics/1.0", "Accept": "text/html,application/xml,text/xml;q=0.9,*/*;q=0.8"})
    with urlopen(req, timeout=20) as response:
        return response.read()


def relevant(text: str) -> bool:
    text = text.lower()
    return any(key in text for key in KEYWORDS)


def discover(source: dict[str, Any], data: bytes) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if source["kind"] == "rss":
        root = ET.fromstring(data)
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip(); url = (item.findtext("link") or "").strip()
            body = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
            if url and relevant(title + " " + body):
                found.append({"source_name": source["name"], "url": url, "title": title or url, "published_at": (item.findtext("pubDate") or "").strip() or None, "matched_by": "rss_keyword"})
    else:
        parser = Links(); parser.feed(data.decode(errors="replace")); seen: set[str] = set()
        for href, text in parser.links:
            if relevant(text):
                url = urljoin(source["url"], href)
                if url not in seen:
                    seen.add(url); found.append({"source_name": source["name"], "url": url, "title": text, "published_at": None, "matched_by": "html_link_keyword"})
    for row in found:
        row["candidate_id"] = sha(stable({"source": row["source_name"], "url": row["url"]}))
    return found[:100]


def registry(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        url = row["source_url"]
        item = out.setdefault(url, {"name": row["source_name"], "url": url, "kind": "evidence", "measurement_types": [], "required": False})
        if row["measurement_type"] not in item["measurement_types"]: item["measurement_types"].append(row["measurement_type"])
        item["required"] = item["required"] or row["measurement_type"] == "company_reported"
    for row in DISCOVERY:
        out.setdefault(row["url"], {**row, "measurement_types": ["discovery"]})
    return sorted(out.values(), key=lambda r: (r["kind"], r["name"], r["url"]))


def source_health(items: list[dict[str, Any]], previous: dict[str, Any], do_fetch: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    old = {row["url"]: row for row in previous.get("sources", []) if row.get("url")}; checked = now_iso(); output = []; candidates = []
    for item in items:
        row = dict(item); prior = old.get(item["url"], {})
        if not do_fetch:
            row.update({key: prior.get(key) for key in ("status", "retrieved_at", "sha256", "bytes", "error")}); row["status"] = row["status"] or "not_checked"; output.append(row); continue
        try:
            data = fetch(item["url"]); digest = sha(data); same = prior.get("status") == "ok" and prior.get("sha256") == digest
            row.update({"status": "ok", "retrieved_at": prior.get("retrieved_at") if same else checked, "sha256": digest, "bytes": len(data), "error": None})
            if item["kind"] in {"rss", "html"}: candidates.extend(discover(item, data))
        except Exception as exc:
            row.update({"status": "error", "retrieved_at": prior.get("retrieved_at"), "sha256": prior.get("sha256"), "bytes": prior.get("bytes"), "error": f"{type(exc).__name__}: {exc}"})
            if item.get("required"): raise RuntimeError(f"required source unavailable: {item['url']}: {exc}") from exc
        output.append(row)
    return output, candidates


def digest_files(files: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for name in sorted(files): h.update(name.encode() + b"\0" + files[name] + b"\0")
    return h.hexdigest()


def build(output: Path, previous: Path | None = None, fetch_sources: bool = False) -> dict[str, Any]:
    inventory = read_json(INVENTORY, {}); observed_at = inventory.get("collected_at") or now_iso()
    rows = [normalize(row, observed_at) for row in read_ndjson(SEED)]; rows = list({row["observation_id"]: row for row in rows}.values())
    rows.sort(key=lambda r: (r["provider"], r.get("product") or "", str(r["effective_at"]), r["metric"], r["measurement_type"]))
    prev_sources = read_json(previous / "sources.json", {}) if previous else {}; prev_candidates = read_json(previous / "candidates.json", {}) if previous else {}; prev_manifest = read_json(previous / "manifest.json", {}) if previous else {}
    sources, new_candidates = source_health(registry(rows), prev_sources, fetch_sources)
    candidate_map = {row["candidate_id"]: row for row in prev_candidates.get("candidates", []) if row.get("candidate_id")}
    candidate_map.update({row["candidate_id"]: row for row in new_candidates}); candidates = sorted(candidate_map.values(), key=lambda r: (r.get("published_at") or "", r["source_name"], r["url"]))
    output.mkdir(parents=True, exist_ok=True)
    write_ndjson(output / "observations.ndjson", rows)
    write_json(output / "latest.json", {"schema_version": 1, "series_key": ["provider", "product", "metric", "measurement_type"], "records": latest(rows)})
    write_json(output / "comparables.json", read_json(COMPARABLES, {"schema_version": 1, "records": []}))
    write_json(output / "sources.json", {"schema_version": 1, "policy": {"reported_vs_estimated": "never collapse source classes", "discovery": "candidate discovery does not create canonical observations"}, "sources": sources})
    write_json(output / "candidates.json", {"schema_version": 1, "status": "discovery_only", "candidates": candidates})
    names = ("observations.ndjson", "latest.json", "comparables.json", "sources.json", "candidates.json"); payloads = {name: (output / name).read_bytes() for name in names}; content_digest = digest_files(payloads)
    updated_at = prev_manifest.get("updated_at") if prev_manifest.get("content_digest") == content_digest else now_iso(); updated_at = updated_at or now_iso()
    manifest = {"schema_version": 1, "updated_at": updated_at, "content_digest": content_digest, "seed": {"path": "research/data/ai-economics/seed_observations.ndjson", "sha256": sha(SEED.read_bytes()), "record_count": len(read_ndjson(SEED))}, "inventory": {"path": "research/data/ai-economics/source_inventory.json", "sha256": sha(INVENTORY.read_bytes())}, "comparables_source": {"path": "research/data/ai-economics/comparables.json", "sha256": sha(COMPARABLES.read_bytes())}, "files": {name: sha(data) for name, data in payloads.items()}, "observation_count": len(rows), "candidate_count": len(candidates), "coverage": inventory.get("entities", [])}
    write_json(output / "manifest.json", manifest)
    index = {"schema_version": 1, "updated_at": updated_at, "datasets": {"observations": "observations.ndjson", "latest": "latest.json", "comparables": "comparables.json", "sources": "sources.json", "candidates": "candidates.json", "manifest": "manifest.json"}, "observation_count": len(rows), "candidate_count": len(candidates)}
    write_json(output / "index.json", index); return index


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=OUTPUT); parser.add_argument("--previous-root", type=Path); parser.add_argument("--fetch-sources", action="store_true"); args = parser.parse_args()
    previous = args.previous_root or (args.output if args.output.exists() else None); temp = args.output.with_name(args.output.name + ".tmp")
    if temp.exists(): shutil.rmtree(temp)
    build(temp, previous, args.fetch_sources)
    if args.output.exists(): shutil.rmtree(args.output)
    temp.replace(args.output); print(json.dumps(read_json(args.output / "index.json"), ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
