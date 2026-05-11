#!/usr/bin/env python3
"""
append_row.py — append one expense row to the configured Google Sheet.

Reads config from ../config.json.
Reads a single JSON object from stdin. Keys (all optional; missing -> ""):
    date, merchant, category, amount, currency,
    amount_hkd, fx_rate, fx_date, payment_method,
    line_items, raw_ocr, note, receipt

`logged_at` is set automatically to now (UTC, ISO-8601).

Prints the updated range on success; exits non-zero on failure.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def normalize_sheet_id(value: str) -> str:
    # Accept either a bare sheet ID or a full Google Sheets URL —
    # e.g. https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0.
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", value.strip())
    return m.group(1) if m else value.strip()

COLUMNS = [
    "date", "merchant", "category", "amount", "currency",
    "amount_hkd", "fx_rate", "fx_date", "payment_method",
    "line_items", "raw_ocr", "note", "receipt", "logged_at",
]


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"config.json not found at {CONFIG_PATH}. "
            f"Copy config.example.json to config.json and fill it in."
        )
    cfg = json.loads(CONFIG_PATH.read_text())
    cfg["service_account_path"] = os.path.expanduser(cfg["service_account_path"])
    return cfg


def main() -> int:
    cfg = load_config()
    row = json.loads(sys.stdin.read())
    row.setdefault(
        "logged_at",
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )

    values = [str(row.get(col, "")) for col in COLUMNS]

    creds = Credentials.from_service_account_file(
        cfg["service_account_path"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    resp = (
        svc.spreadsheets()
        .values()
        .append(
            spreadsheetId=normalize_sheet_id(cfg["sheet_id"]),
            range=f"{cfg['worksheet']}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [values]},
        )
        .execute()
    )
    updated = resp.get("updates", {}).get("updatedRange", "?")
    print(f"OK {updated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
