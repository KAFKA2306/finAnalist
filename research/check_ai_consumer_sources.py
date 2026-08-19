#!/usr/bin/env python3
from __future__ import annotations

import urllib.error
import urllib.request

from update_ai_consumer import FEATURES, METRICS

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"

for url in sorted({row["source_url"] for row in METRICS + FEATURES}):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(req, timeout=60) as response:
            sample = response.read(1024)
            print(f"OK {response.status} {len(sample)}+ {url}", flush=True)
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code} {url}", flush=True)
    except Exception as exc:
        print(f"ERROR {type(exc).__name__}: {exc} {url}", flush=True)
