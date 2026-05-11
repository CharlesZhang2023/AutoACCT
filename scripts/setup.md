# Admin setup + troubleshooting

End users follow the 4-step install in the main README (or the gentler [`DEPLOY.md`](../DEPLOY.md)). This page covers two things they don't see:

1. **Admin setup** — what you do once, before anyone can install
2. **Troubleshooting** — the errors users will report back to you

---

## Part A — Admin setup (one time)

The shared-key model: you create **one** Google Cloud service account and distribute its JSON key + email address to every user. Each user creates their own Google Sheet and shares it with that one service-account email. The service account can only write to sheets that have been explicitly shared with it.

### A.1 — Create the Google Cloud project + service account

1. Go to https://console.cloud.google.com/ and create a new project (e.g. `autoacct`).
2. In the top search bar, search **Google Sheets API** → click the result → **Enable**.
3. Left menu: **IAM & Admin → Service Accounts → + Create Service Account**.
   - Name: `AutoACCT` (any name works)
   - Click **Create and Continue → Done** (skip the optional IAM role step — the service account doesn't need any GCP roles, since it gains write access per-sheet via sheet-level sharing).
4. Click the new service account → **Keys** tab → **Add Key → Create new key → JSON → Create**.
   A `.json` key file downloads to your browser's Downloads folder.
5. **Copy the service account's email** (e.g. `autoacct@<project>.iam.gserviceaccount.com`).
6. Rename the downloaded file to `autoacct-sa.json` (recommended — DEPLOY.md assumes this name).

### A.2 — Encrypt the JSON and commit it to the repo

Generate a strong random passphrase (48 chars; alphanumeric + `-_`):

```bash
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '_-') for _ in range(48)))"
```

Encrypt with openssl (AES-256-CBC + PBKDF2, 100k iterations):

```bash
PASSPHRASE='<paste-passphrase-here>' openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt \
  -pass env:PASSPHRASE \
  -in ~/Downloads/<downloaded-key>.json \
  -out secrets/bookkeeping-sa.json.enc

git add secrets/bookkeeping-sa.json.enc
git commit -m "secrets: add encrypted SA key"
git push
```

Then **store the passphrase in your team password manager** (1Password / Bitwarden shared vault). The passphrase is the only out-of-band thing your users need.

Move the plaintext key out of the repo dir and protect it on your own machine:

```bash
mv ~/Downloads/<downloaded-key>.json ~/.config/gcp/bookkeeping-sa.json
chmod 600 ~/.config/gcp/bookkeeping-sa.json
```

Tell each user:
- A pointer to the repo (`git clone https://github.com/CharlesZhang2023/AutoACCT.git`)
- The passphrase (via 1Password share — **never via plain email / chat**)
- Link to [`DEPLOY.md`](../DEPLOY.md) for hand-holding or [`README.md`](../README.md) if they're comfortable in the terminal

### A.3 — Verify your own install first

Before announcing it to anyone, run through the user-side install yourself (`DEPLOY.md` Parts 1–4) on a clean directory to confirm `git clone` + `decrypt-key.sh` + sheet creation + smoke test all work end-to-end. Catches any GCP-side misconfiguration before users hit it.

### A.4 — Rotation

**Passphrase rotation** (when a user leaves, or every 6–12 months):
1. Generate a new passphrase as in A.2.
2. Decrypt with the old passphrase, re-encrypt with the new one:
   ```bash
   openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -d \
     -in secrets/bookkeeping-sa.json.enc -out /tmp/sa.json
   PASSPHRASE='<new>' openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt \
     -pass env:PASSPHRASE -in /tmp/sa.json -out secrets/bookkeeping-sa.json.enc
   shred -u /tmp/sa.json   # rm -P on macOS
   ```
3. Commit + push the new `.enc`. Update the passphrase entry in the team password manager. Users `git pull` + re-run `decrypt-key.sh`.

**Underlying GCP key rotation** (when the passphrase leaks, or a user with a decrypted copy leaves):
- Passphrase rotation alone is **not enough** if someone already has the decrypted JSON on their machine — they retain a working credential.
- GCP Console → Service Accounts → Keys → **Add Key** (download new) → **Delete old**. The deleted key stops working immediately, globally.
- Re-encrypt the new JSON (A.2 flow), commit, push. Users pull + decrypt.

See [`secrets/README.md`](../secrets/README.md) for the same procedures with copy-pasteable commands.

---

## Part B — Troubleshooting (user errors you'll see)

### `HTTP 403` / `The caller does not have permission`
The user forgot to share their sheet with the service-account email, or typed the email wrong. Tell them to re-do Step 8 in DEPLOY.md (or Step 3.5 in README.md). Confirm the email you sent them matches exactly.

### `HTTP 400: Unable to parse range`
The `worksheet` value in `config.json` doesn't match the actual tab name. Most common cause: user has Chinese Sheets UI → tab is `工作表1`, but they wrote `"worksheet": "Sheet1"`. Fix the config.

### `HTTP 404` / `Requested entity was not found`
`sheet_id` in `config.json` is wrong. Tell user to re-copy the long string from `/d/.../edit` in their browser's URL bar.

### `FileNotFoundError ... bookkeeping-sa.json`
User skipped `bash scripts/decrypt-key.sh`, or decryption failed and they didn't notice. Have them re-run it and confirm the success line `Decrypted to ~/.config/gcp/bookkeeping-sa.json`.

Run `ls -la ~/.config/gcp/` to check.

### `bad decrypt` from openssl
Wrong passphrase. Most common causes:
- They pasted the wrong entry from the password manager.
- The passphrase has been rotated since last time. Have them check the password manager for the latest version.

### `ImportError: No module named 'googleapiclient'`
Python deps not installed. Run `pip install google-api-python-client google-auth`. If `pip` is missing, try `pip3` or `python3 -m pip install ...`.

### `config.json not found`
User skipped the `cp config.example.json config.json` step. They need to be inside the skill directory when running it.

### JSON parse error (`Expecting value` / `Extra data`)
Smart quotes from TextEdit, or a stray comma. Fix in plain-text mode, or have an AI agent repair the file.

### Authorization or quota errors at scale
The shared SA shares one GCP project's quota. The default Sheets API quota (300 req/min per project) is generous for receipts — you would have to log thousands per minute to hit it. If you do hit quota, request an increase in the GCP console.

---

## Part C — When to abandon the shared-key model

The shared-key model is right for **trusted internal teams** (you know everyone with a copy of the JSON). Move to a different model if any of these happen:

- **You're distributing to strangers / customers.** They can write to each other's sheets if the JSON leaks. Move to OAuth (each user authenticates with their own Google account).
- **You can't trust users to keep the JSON private.** Same answer.
- **You need per-user audit trails.** Sheets API logs only "the SA wrote" — you can't tell from GCP which user did it. (Sheet revision history still shows it, since each user has their own sheet.)

In those cases, see the git history for an earlier Apps Script–based variant, or design a small backend that holds the key server-side and exposes a per-user-authenticated endpoint.
