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

Follow the 6 steps below. Takes ~10 minutes.

### Step 1 — Clone the skill and install Python deps

```bash
git clone https://git.deepknow.site/Knowit/AutoACCT.git ~/.claude/skills/bookkeeping
pip install google-api-python-client google-auth
```

### Step 2 — Create a Google Cloud service account

1. Open https://console.cloud.google.com/ and create a new project (e.g. `autoacct`).
2. In the top search bar, search **Google Sheets API** → click the result → **Enable**.
3. Left menu: **IAM & Admin → Service Accounts → + Create Service Account**
   - Name: `bookkeeping` (any name works)
   - Click **Create and Continue → Done** (skip the optional role step).
4. Click the new service account → **Keys** tab → **Add Key → Create new key → JSON → Create**.
   A `.json` key file will download to your browser's Downloads folder.
5. **Copy the service account's email** (looks like `bookkeeping@<project>.iam.gserviceaccount.com`) — you'll paste it in Step 4.

### Step 3 — Move the key file out of the repo

Never leave a service-account key inside the repo directory. Move it to `~/.config/gcp/`:

```bash
mkdir -p ~/.config/gcp
mv ~/Downloads/<your-downloaded-file>.json ~/.config/gcp/bookkeeping-sa.json
chmod 600 ~/.config/gcp/bookkeeping-sa.json
```

### Step 4 — Create the Google Sheet

1. Open https://sheets.new (creates a fresh blank sheet).
2. Give it a title (e.g. `AutoACCT Expenses`).
3. **Note the tab name** at the bottom-left — default is `Sheet1` (English UI) or `工作表1` (Chinese UI). Write it down, you'll need the exact string in Step 5.
4. Click cell **A1**, then paste this one line (the tabs split the headers across A–N automatically):
   ```
   Date	Merchant	Category	Amount	Currency	Amount (HKD)	FX Rate	FX Date	Payment Method	Line Items	Raw OCR	Note	Receipt	Logged At
   ```
5. Click **Share** (top right) → paste the service-account email from Step 2 → role **Editor** → **Send** (you can uncheck "Notify people").
6. Copy the **Sheet ID** from the URL — it's the long string between `/d/` and `/edit`:
   `https://docs.google.com/spreadsheets/d/`**`1abc...xyz`**`/edit`

### Step 5 — Write config.json

```bash
cd ~/.claude/skills/bookkeeping
cp config.example.json config.json
```

Open `config.json` in your editor and fill in **sheet_id** and **worksheet** with the values from Step 4:

```json
{
  "sheet_id": "1abc...xyz",
  "worksheet": "Sheet1",
  "service_account_path": "~/.config/gcp/bookkeeping-sa.json",
  "hkd_fx_provider": "frankfurter"
}
```

> ⚠️ **Common pitfall**: if your Google Sheets UI is in Chinese, the default tab is named `工作表1` (not `Sheet1`). Put `"worksheet": "工作表1"` exactly. A mismatched tab name throws `HTTP 400: Unable to parse range`.

### Step 6 — Sanity check

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' | python3 ~/.claude/skills/bookkeeping/scripts/append_row.py
```

Success looks like: `OK 'Sheet1'!A2:N2` and a new row appears in the sheet. Delete the TEST row when you're done.

If you hit an error, see [`scripts/setup.md`](scripts/setup.md) for the longer reference.

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
