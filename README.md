# AutoACCT — Bookkeeping Skill for Claude Code

**English** | [简体中文](README.zh-CN.md)

A [Claude Code](https://claude.com/claude-code) skill that turns a receipt image (optionally with a caption) into a structured row in a Google Sheet, with automatic HKD conversion.

Intended to be invoked manually inside Claude Code today, and wired up to a WhatsApp webhook later.

## What it does

1. Reads a receipt / invoice / payment-screenshot image via vision.
2. Extracts: date, merchant, category, amount, currency, payment method, line items, raw OCR, caption note.
3. Converts the amount to **HKD** at that day's ECB reference rate via [frankfurter.app](https://frankfurter.app) (free, no API key).
4. Appends one row to a configured Google Sheet (14 columns — see `schema.md`).
5. Replies with the row and flags any field it had to guess.

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://git.deepknow.site/Knowit/AutoACCT.git ~/.claude/skills/bookkeeping
```

Then follow [`scripts/setup.md`](scripts/setup.md) for the one-time setup:

- Python deps: `pip install google-api-python-client google-auth`
- Create a GCP service account + download its JSON key
- Create a Google Sheet, add 14 header columns, share with the service account email
- `cp config.example.json config.json` and fill in `sheet_id` + `service_account_path`

## Use

In a Claude Code session, drop a receipt image in and say "log this" (or similar). The skill auto-triggers on receipt-image requests — no slash command needed.

Caption is optional; use it to add context (payment method, split, category hint, free-text note).

## Files

| File                  | Purpose                                           |
|-----------------------|---------------------------------------------------|
| `SKILL.md`            | Entry — Claude reads this to invoke the skill     |
| `categories.md`       | Fixed category list (14 categories)               |
| `schema.md`           | Google Sheet column order (A–N)                   |
| `config.example.json` | Template → copy to `config.json` (gitignored)     |
| `scripts/fx_convert.py` | Currency → HKD via frankfurter.app              |
| `scripts/append_row.py` | Writes one row to Google Sheets                 |
| `scripts/setup.md`    | One-time setup steps                              |

## Roadmap

- [ ] WhatsApp webhook layer (Meta Cloud API or Twilio) so images can be sent from a phone.
- [ ] Optional Google Drive upload so the `Receipt` column becomes a clickable image link.
- [ ] Monthly summary script (totals by category, currency breakdown).

## License

Private — internal use.
