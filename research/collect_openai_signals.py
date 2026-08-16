#!/usr/bin/env python3
"""Download and inventory the official OpenAI Signals consumer-data CSV bundle."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://cdn.openai.com/signals/data-download-csv.zip"
SOURCE_PAGE = "https://openai.com/signals/data-download/"
LICENSE = "CC BY 4.0"


def download() -> bytes:
    req = Request(URL, headers={"User-Agent": "ai-consumer/1.0 github.com/KAFKA2306/finAnalist"})
    with urlopen(req, timeout=120) as response:
        return response.read()


def csv_metadata(name: str, raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        header = []
        rows = 0
    else:
        rows = sum(1 for _ in reader)
    return {
        "name": name,
        "columns": header,
        "rows": rows,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def collect(raw_zip: bytes) -> dict[str, object]:
    files = []
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/") or not name.lower().endswith(".csv"):
                continue
            files.append(csv_metadata(name, archive.read(name)))
    if not files:
        raise ValueError("OpenAI Signals bundle contained no CSV files")
    return {
        "schema_version": 1,
        "publisher": "OpenAI",
        "dataset": "OpenAI Signals consumer data",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_page": SOURCE_PAGE,
        "download_url": URL,
        "license": LICENSE,
        "bundle_sha256": hashlib.sha256(raw_zip).hexdigest(),
        "bundle_bytes": len(raw_zip),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/ai-consumer/openai-signals-manifest.json"))
    parser.add_argument("--archive", type=Path, help="optional path to an already-downloaded official ZIP")
    args = parser.parse_args()
    raw = args.archive.read_bytes() if args.archive else download()
    payload = collect(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"indexed {len(payload['files'])} CSV files -> {args.output}")


if __name__ == "__main__":
    main()
