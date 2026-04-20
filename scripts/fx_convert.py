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
import sys
import urllib.request
from datetime import date


def fetch_rate(currency: str, on_date: str) -> tuple[float, str]:
    currency = currency.upper()
    if currency == "HKD":
        return 1.0, on_date
    url = f"https://api.frankfurter.app/{on_date}?from={currency}&to=HKD"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    rate = data["rates"]["HKD"]
    return float(rate), data["date"]


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
