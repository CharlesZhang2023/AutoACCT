# BYO-KEY — Bring Your Own Service Account

This is an **alternative** to the default install. It buys you stronger privacy at the cost of ~15 extra minutes of GCP setup. **Most users should stick with the default flow** in [`README.md`](README.md) / [`DEPLOY.md`](DEPLOY.md) — this page is for people who explicitly want their service-account credential isolated from everyone else on the team.

---

## When to use this

Pick BYO-KEY if **any** of these apply:

- You don't trust the other teammates who have the shared passphrase. With the default flow, anyone with the passphrase can authenticate as the team SA and could (in theory, via API) read any sheet that has been shared with that SA. With BYO-KEY, your SA is only known to you.
- You're outside the original team and just want to use this skill for yourself.
- You log sensitive expenses (legal / medical / personal) and want belt-and-braces isolation.
- Your security policy requires per-user credentials with per-user audit trails.

Stick with the **default (shared-key) flow** if:

- You're in the trusted internal team this repo was built for.
- You're fine with the team passphrase being your trust boundary.
- You want the fastest path to "drop receipts in, see them in a sheet" (~5 minutes vs ~20).

---

## Trade-off at a glance

| | Default (shared SA) | BYO-KEY |
|---|---|---|
| Time to install | ~5 min | ~20 min |
| GCP knowledge required | Zero | Some (click through a few menus) |
| Costs you anything? | No | No (GCP free tier covers it) |
| Who can write to your sheet | Anyone with the team passphrase | Only you |
| Audit trail | "the team SA wrote it" | "your personal SA wrote it" |
| Rotation responsibility | Admin (rotates for everyone) | **You** (your problem alone) |
| If someone leaves the team | Admin rotates passphrase; you do nothing | Unaffected — wasn't your SA anyway |
| Skill features available | All | All — same code path |

---

## Steps

Assumes you've already done the **non-credential** parts of the default install: cloned the repo, run `pip install`. If not, do those first.

### Step 1 — Create a Google Cloud project

1. Go to https://console.cloud.google.com/.
2. Top bar → project dropdown → **New Project** → name it anything (e.g. `autoacct-personal`) → **Create**.
3. Wait ~10 seconds for it to provision, then **switch the project dropdown to your new project**.

GCP free tier covers this with room to spare. You will not be charged.

### Step 2 — Enable the Google Sheets API

1. Top search bar → type **Google Sheets API** → click the result.
2. Click **Enable**. (Page reloads to the API dashboard once enabled.)

### Step 3 — Create a service account

1. Left menu → **IAM & Admin → Service Accounts**.
2. Click **+ Create Service Account** at the top.
3. **Service account name**: anything (e.g. `autoacct-mine`).
4. Click **Create and Continue → Done**. **Skip the optional IAM role step** — your SA does not need any project-level GCP roles, since its sheet-write capability comes from per-sheet sharing.

### Step 4 — Download the JSON key

1. Click the row of the SA you just created.
2. Top tabs → **Keys → Add Key → Create new key → JSON → Create**.
3. A `.json` file downloads to your `~/Downloads/` folder. Its filename looks like `autoacct-personal-1a2b3c4d.json`.

### Step 5 — Move and secure the key file

```bash
mkdir -p ~/.config/gcp
mv ~/Downloads/autoacct-personal-*.json ~/.config/gcp/my-sa.json
chmod 600 ~/.config/gcp/my-sa.json
```

You can name the file anything — `my-sa.json`, `autoacct-personal.json`, whatever — as long as you remember it for Step 6.

### Step 6 — Note your service account's email

Open the JSON file and find the `client_email` field. It looks like:

```
autoacct-mine@autoacct-personal-12345.iam.gserviceaccount.com
```

Or use this one-liner:

```bash
python3 -c "import json; print(json.load(open('~/.config/gcp/my-sa.json'.replace('~', '$HOME')))['client_email'])"
```

Copy this email — you'll paste it into your Sheet's Share dialog (Step 8 below).

### Step 7 — Point `config.json` at your key

If you already have a `config.json` (from doing the default install previously):

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
```

Edit `config.json` and change **only** the `service_account_path` line to point at your key:

```json
{
  "sheet_id": "https://docs.google.com/spreadsheets/d/.../edit",
  "worksheet": "Sheet1",
  "service_account_path": "~/.config/gcp/my-sa.json",
  "hkd_fx_provider": "frankfurter"
}
```

If you don't have a `config.json` yet:

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
cp config.example.json config.json
# then edit config.json
```

**You do NOT need to run `scripts/decrypt-key.sh`.** That script is for the shared key flow. BYO-KEY users skip it entirely.

### Step 8 — Share your sheet with your SA

In your Google Sheet (the one with the AutoACCT headers in row 1):

1. Click **Share** (top right).
2. Paste the SA email from Step 6.
3. Role: **Editor**.
4. Uncheck "Notify people".
5. **Send**.

### Step 9 — Smoke test

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' \
  | python3 ~/.openclaw/workspace/skills/AutoACCT/scripts/append_row.py
```

Success: `OK Sheet1!A2:N2`, new TEST row in your sheet.

---

## What you take on by going this route

| Responsibility | What it means |
|---|---|
| **Key rotation** | Every 6–12 months (or when in doubt), download a new key in GCP Console and delete the old one. Replace `~/.config/gcp/my-sa.json` with the new file. No other config changes. |
| **Key safety** | The JSON is a private key. `chmod 600`, no laptop backups to public clouds, no copies in chat / email / Drive. If it leaks, **immediately** delete the key in GCP Console (the deleted key stops working globally within seconds). |
| **Project hygiene** | Your GCP project sits idle until you use it. Don't enable other APIs you don't need; don't grant the SA any project-level IAM roles. It only needs sheet-level Editor access via Share. |
| **Audit** | Sheet revision history will show your SA's email rather than the team SA. If you also share the same sheet with the team SA, both writers will appear separately — which lets you audit "who wrote what". |

---

## Switching back to the shared key later

You can have both keys side by side — only `config.json` decides which one is used. To switch back:

```bash
bash scripts/decrypt-key.sh   # decrypts the shared key to ~/.config/gcp/bookkeeping-sa.json
```

Then edit `config.json` to set:

```json
"service_account_path": "~/.config/gcp/bookkeeping-sa.json"
```

Your own `my-sa.json` stays on disk (untouched); you can switch back to it any time by flipping the `service_account_path` value. You can even keep two copies of `config.json` (e.g. `config.personal.json` and `config.shared.json`) and swap symlinks — though most people won't need that.

---

## What this does **not** protect you from

- **Google itself.** Your Sheet, your SA, and your key all live in Google's infrastructure. BYO-KEY isolates you from your *teammates*, not from Google.
- **A compromise of your own laptop.** If your machine is owned by an attacker, your SA key is theirs. Standard endpoint security applies.
- **You losing your own JSON.** There's no "forgot password" — if you delete the JSON, your only option is to generate a new key in GCP Console (the SA itself, and the sheets shared with it, all survive).
