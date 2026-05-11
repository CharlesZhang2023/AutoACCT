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

### A.2 — Distribute the key + email to users

The JSON is a private key. Use a secure channel:

| Channel | Verdict |
|---|---|
| **Password manager shared vault** (1Password, Bitwarden, Vaultwarden) | **Recommended.** Easy to revoke, no copies floating in inboxes. |
| Encrypted email / Signal / private DM | OK for small teams. |
| Cloud drive with strict per-user ACLs | OK if your org already uses one. |
| **Plain email** | Do not. |
| **Git repo (even private)** | Do not — `.gitignore` already excludes `*-sa.json`. |

Tell each user:
- The JSON file (attach / share)
- The service-account email (so they know who to share their sheet with)
- Pointer to [`DEPLOY.md`](../DEPLOY.md) if they want hand-holding, or [`README.md`](../README.md) if they're comfortable with the terminal

### A.3 — Verify your own install first

Before sending the JSON to anyone, run through the user-side install yourself (Steps 1–11 of `DEPLOY.md`) to confirm everything works end-to-end. It's also a chance to catch any GCP-side misconfiguration before users hit it.

### A.4 — Key rotation (when you need to)

Rotate the JSON key when:
- A user leaves the team (so you stop trusting their copy of the key)
- You suspect a leak
- Every 6–12 months as routine hygiene

To rotate:
1. In GCP Console → Service Accounts → keys → **Add Key** (creates a new one) → download.
2. **Delete the old key** in the same panel. (After deletion, any existing copies stop working.)
3. Re-distribute the new JSON to all current users via your secure channel.
4. Users replace their `~/.config/gcp/autoacct-sa.json` with the new file. No other changes needed — `config.json`, sheet sharing, etc. all stay intact.

---

## Part B — Troubleshooting (user errors you'll see)

### `HTTP 403` / `The caller does not have permission`
The user forgot to share their sheet with the service-account email, or typed the email wrong. Tell them to re-do Step 8 in DEPLOY.md (or Step 3.5 in README.md). Confirm the email you sent them matches exactly.

### `HTTP 400: Unable to parse range`
The `worksheet` value in `config.json` doesn't match the actual tab name. Most common cause: user has Chinese Sheets UI → tab is `工作表1`, but they wrote `"worksheet": "Sheet1"`. Fix the config.

### `HTTP 404` / `Requested entity was not found`
`sheet_id` in `config.json` is wrong. Tell user to re-copy the long string from `/d/.../edit` in their browser's URL bar.

### `FileNotFoundError ... autoacct-sa.json`
The JSON file isn't where `config.json` expects. Common causes:
- User saved with a different filename (e.g. `autoacct-project-12345.json`) and never renamed it.
- User skipped the `mv` step and the file is still in Downloads.

Run `ls -la ~/.config/gcp/` to check.

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
