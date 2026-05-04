# One-time setup

## 1. Python deps
```
pip install google-api-python-client google-auth
```

## 2. Google Cloud service account
1. Create (or reuse) a GCP project.
2. Enable the **Google Sheets API** for the project.
3. Create a **service account**; skip the optional IAM steps.
4. In the service account, create a **JSON key** and download it.
5. Move the key to a safe path, e.g. `~/.config/gcp/bookkeeping-sa.json`, then:
   ```
   chmod 600 ~/.config/gcp/bookkeeping-sa.json
   ```

## 3. Prepare the Google Sheet
1. Create a new Google Sheet (or open an existing one).
2. Rename the first tab to `Expenses` (or update `worksheet` in config).
3. In row 1 add headers matching `schema.md` columns A–N:
   `Date | Merchant | Category | Amount | Currency | Amount (HKD) | FX Rate | FX Date | Payment Method | Line Items | Raw OCR | Note | Receipt | Logged At`
4. Open the service account JSON and copy the `client_email` value (looks like `...@...iam.gserviceaccount.com`).
5. Click **Share** on the sheet and add that email as **Editor**.
6. Copy the sheet ID from the URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`.

## 4. Skill config
```
cd ~/.openclaw/workspace/skills/bookkeeping
cp config.example.json config.json
# edit config.json: sheet_id, service_account_path
```

## 5. Sanity check
```
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' \
  | python ~/.openclaw/workspace/skills/bookkeeping/scripts/append_row.py
```
You should see `OK Expenses!A2:N2` (or similar) and a new row in the sheet. Delete the TEST row when done.
