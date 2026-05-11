#!/usr/bin/env python3
"""
fx_convert.py <amount> <currency> [--date yyyy-mm-dd]

Convert a given amount in <currency> to HKD.
Prints one tab-separated line: <hkd_amount>\t<fx_rate>\t<fx_date>
Non-zero exit on failure.

Uses frankfurter.app by default: free, no API key, ECB reference rates,
historical dates supported via /{date} path.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

# Cache file for frankfurter responses. ECB reference rates for past dates
# never change, so an indefinite TTL is safe; same-day rates also stabilize
# once published. Keyed by "<currency>_<on_date>" → {rate, fx_date}.
_CACHE_DIR = Path(
    os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
) / "autoacct"
_CACHE_PATH = _CACHE_DIR / "fx_cache.json"


def _load_cache() -> dict:
    if not _CACHE_PATH.exists():
        return {}
    try:
        return json.loads(_CACHE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, indent=2, sort_keys=True))
    tmp.replace(_CACHE_PATH)


def fetch_rate(currency: str, on_date: str) -> tuple[float, str]:
    currency = currency.upper()
    if currency == "HKD":
        return 1.0, on_date

    cache = _load_cache()
    key = f"{currency}_{on_date}"
    if key in cache:
        entry = cache[key]
        return float(entry["rate"]), entry["fx_date"]

    url = f"https://api.frankfurter.dev/v1/{on_date}?from={currency}&to=HKD"
    req = urllib.request.Request(url, headers={"User-Agent": "AutoACCT/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    rate = float(data["rates"]["HKD"])
    fx_date_resolved = data["date"]

    cache[key] = {"rate": rate, "fx_date": fx_date_resolved}
    _save_cache(cache)

    return rate, fx_date_resolved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("amount", type=float)
    ap.add_argument("currency")
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()

    rate, fx_date = fetch_rate(args.currency, args.date)
    hkd = round(args.amount * rate, 2)
    print(f"{hkd}\t{rate}\t{fx_date}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
