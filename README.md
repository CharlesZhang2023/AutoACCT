# AutoACCT for OpenClaw

**English** | [简体中文](README.zh-CN.md)

An OpenClaw skill that turns a receipt image (optionally with a caption) into a structured row in a Google Sheet, with automatic HKD conversion.

Intended to be invoked manually inside OpenClaw today, and wired up to a WhatsApp webhook later.

## What it does

1. Reads a receipt / invoice / payment-screenshot image via vision.
2. Extracts: date, merchant, category, amount, currency, payment method, line items, raw OCR, caption note.
3. Converts the amount to **HKD** at that day's ECB reference rate via [frankfurter.app](https://frankfurter.app) (free, no API key).
4. Appends one row to a configured Google Sheet (14 columns — see `schema.md`).
5. Replies with the row and flags any field it had to guess.

## Install (end users)

Your admin will have given you **two things**: a service-account JSON key file (e.g. `autoacct-sa.json`) and a service-account email (e.g. `autoacct@your-project.iam.gserviceaccount.com`). If you don't have them, ask your admin first.

Follow the 4 steps below. Takes ~5 minutes.

> **Not comfortable with the terminal?** Use [`DEPLOY.md`](DEPLOY.md) instead — same install, but written for non-technical users with an AI agent walking them through.

### Step 1 — Clone the skill and install Python deps

```bash
git clone https://github.com/CharlesZhang2023/AutoACCT.git ~/.openclaw/workspace/skills/AutoACCT
pip install google-api-python-client google-auth
```

### Step 2 — Drop the admin's JSON key into `~/.config/gcp/`

```bash
mkdir -p ~/.config/gcp
mv ~/Downloads/autoacct-sa.json ~/.config/gcp/autoacct-sa.json
chmod 600 ~/.config/gcp/autoacct-sa.json
```

(Replace `~/Downloads/autoacct-sa.json` with wherever you saved the file your admin sent.)

### Step 3 — Create your Google Sheet and share it with the service account

1. Open https://sheets.new (creates a fresh blank sheet).
2. Title it (e.g. `My AutoACCT Expenses`).
3. **Note the tab name** at the bottom-left — `Sheet1` (English UI) or `工作表1` (Chinese UI). You'll paste it into `config.json` in Step 4.
4. Click cell **A1**, then paste this one line (the tabs split the headers across A–N automatically):
   ```
   Date	Merchant	Category	Amount	Currency	Amount (HKD)	FX Rate	FX Date	Payment Method	Line Items	Raw OCR	Note	Receipt	Logged At
   ```
5. Click **Share** (top right) → paste the **service-account email** your admin gave you → role **Editor** → **Send** (you can uncheck "Notify people").
6. **Copy the full URL from your browser's address bar.** Something like:
   `https://docs.google.com/spreadsheets/d/1abc...xyz/edit#gid=0`
   (The script extracts the sheet ID for you — either the full URL or just the bare ID works.)

### Step 4 — Write config.json

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
cp config.example.json config.json
```

Open `config.json` and fill in **sheet_id** (paste the URL from Step 3.6) and **worksheet** (the tab name from Step 3.3):

```json
{
  "sheet_id": "https://docs.google.com/spreadsheets/d/1abc...xyz/edit",
  "worksheet": "Sheet1",
  "service_account_path": "~/.config/gcp/autoacct-sa.json",
  "hkd_fx_provider": "frankfurter"
}
```

> **Common pitfall**: if your Google Sheets UI is in Chinese, the default tab is named `工作表1` (not `Sheet1`). Put `"worksheet": "工作表1"` exactly. A mismatched tab name throws `HTTP 400: Unable to parse range`.

### Sanity check

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' | python3 ~/.openclaw/workspace/skills/AutoACCT/scripts/append_row.py
```

Success looks like: `OK 'Sheet1'!A2:N2` and a new row appears in your sheet. Delete the TEST row when you're done.

If you hit an error, see [`scripts/setup.md`](scripts/setup.md) for troubleshooting.

## Admin setup (one time, done by you before distributing)

Before users can run the steps above, **you** (the admin) create one shared service account and distribute the JSON to users. See [`scripts/setup.md`](scripts/setup.md) for the full admin guide — short version:

1. Create a GCP project, enable Sheets API, create a service account, download the JSON key.
2. Distribute the JSON file + the service-account email to your users via a secure channel (1Password / Bitwarden / encrypted email — **never commit to git**).
3. Tell users to follow the 4 steps above.

## Use

In an OpenClaw session, drop a receipt image in and say "log this" (or similar). The skill auto-triggers on receipt-image requests — no slash command needed.

Caption is optional; use it to add context (payment method, split, category hint, free-text note).

## Files

| File                      | Purpose                                              |
|---------------------------|------------------------------------------------------|
| `SKILL.md`                | Entry — OpenClaw reads this to invoke the skill      |
| `categories.md`           | Fixed category list (14 categories)                  |
| `schema.md`               | Google Sheet column order (A–N)                      |
| `config.example.json`     | Template → copy to `config.json` (gitignored)        |
| `scripts/fx_convert.py`   | Currency → HKD via frankfurter.app                   |
| `scripts/append_row.py`   | Writes one row to Google Sheets                      |
| `scripts/setup.md`        | Admin setup guide + troubleshooting                  |
| `DEPLOY.md`               | Step-by-step install guide for non-technical users   |

## License

[MIT](LICENSE) © 2026 Knowit
