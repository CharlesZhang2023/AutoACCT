# AutoACCT — Install Guide for Non-Technical Users

This guide is written for people who don't write code for a living. If you can use email and Google Sheets, you can finish this in about 5 minutes. You will **not** need to understand any of the code you see, and you will **not** create anything inside Google Cloud — your admin already did that part for you.

If you are following this with an AI agent (Claude, OpenClaw, ChatGPT, etc.), you can paste any error or screenshot into the chat and ask "what does this mean?" — the agent will translate.

---

## What you are about to set up

By the end of this guide, you will be able to drop a photo of a receipt into a chat with your AI assistant and have it automatically appear as a new row in your own Google Sheet, with the amount converted to Hong Kong Dollars.

You will keep your own Google Sheet (only you can read it). A small "service account" that your admin already created will be allowed to add rows to your sheet — and nothing else. You can revoke that access at any time by un-sharing the sheet.

---

## Before you start: a 30-second checklist

Make sure you have all four of these. If any is missing, stop and get it before continuing.

| You need | How to check |
|---|---|
| **A Google account** | You can sign in to gmail.com |
| **A Mac or Linux computer** | This guide uses Mac. Linux is identical. **Windows users**: use WSL (Windows Subsystem for Linux), or ask your AI agent for the Windows-equivalent commands |
| **OpenClaw (or another AI client) installed** | You already use it to chat with an AI |
| **A passphrase from your admin** | A ~48-character random string, typically delivered through a password manager (1Password / Bitwarden). **If you don't have it, message your admin first.** |
| **About 5 minutes** | Don't start during a phone call. |

---

## How to ask your AI agent for help

If you get stuck at any step:

1. Copy the step number and a short description of what went wrong.
2. If you can, take a screenshot.
3. Paste both into your AI chat and say something like: "I'm on Step 4 of the AutoACCT deploy guide and I see X. What should I do?"

The agent has access to this guide and can walk you through.

**Important:** If you do not understand a command, **ask before running it**. Do not paste any command you don't understand into a Terminal window.

---

# Part 1 — Get the code onto your computer (2 minutes)

## Step 1. Open the Terminal

The Terminal is a window where you type commands instead of clicking. You won't write any commands yourself — you'll only copy-paste them from this guide.

**On Mac:**
1. Press **Command (⌘) + Space** to open Spotlight search.
2. Type `terminal` and press **Enter**.
3. A small white-on-black (or black-on-white) window will appear.

That's the Terminal. Leave it open.

## Step 2. Copy the skill onto your computer + install its Python helpers

Copy the entire line below, click into the Terminal, paste, and press **Enter**:

```bash
git clone https://github.com/CharlesZhang2023/AutoACCT.git ~/.openclaw/workspace/skills/AutoACCT
```

**What you should see:** a few lines like `Cloning into '/Users/.../AutoACCT'...` followed by your prompt returning.

**If you see "git: command not found":** your Mac is missing developer tools. Run `xcode-select --install` and click through the popup. Then re-run the command above.

**If you see "fatal: destination path ... already exists":** you've run this before. Skip to the next command.

Now install the two Python packages the skill needs:

```bash
pip install google-api-python-client google-auth
```

**What you should see:** a flurry of `Collecting ...` / `Installing ...` lines ending with `Successfully installed ...`. Done.

**If `pip` is not found:** try `pip3` instead, or run `python3 -m pip install google-api-python-client google-auth`.

---

# Part 2 — Unlock the bundled service-account key (1 minute)

The repo ships with the team's service-account key already encrypted (AES-256). You don't need any extra file — you just need the passphrase from your admin to unlock it.

## Step 3. Have the passphrase ready

The passphrase is a ~48-character random string. It looks something like:

```
d03wb3gAnXyo2N8e6FYGIUTNUd3-rFu-UxuEYbVWgOOZxZnG
```

Your admin will have stored it in the team password manager (1Password / Bitwarden). Open that, find the entry called something like "AutoACCT decrypt passphrase", and **copy it now**. You'll paste it in the next step.

If you can't find it, message your admin before continuing.

## Step 4. Run the decrypt script

Paste this into the Terminal:

```bash
bash ~/.openclaw/workspace/skills/AutoACCT/scripts/decrypt-key.sh
```

The Terminal prompts:

```
enter AES-256-CBC decryption password:
```

**Paste the passphrase from Step 3.** (Right-click → Paste, or Cmd+V. The characters won't appear on screen — that's normal; it's hiding your password.) Press **Enter**.

**What success looks like:**
```
Decrypted to /Users/you/.config/gcp/bookkeeping-sa.json

Service-account email: bookkeeping@autoacct.iam.gserviceaccount.com
Next step: share your Google Sheet with this email (Editor).
```

**Write down the service-account email** — you'll paste it in Step 8.

**If you see `bad decrypt`:** the passphrase is wrong. Either you mistyped it, or your admin sent a different one. Try again with a fresh paste.

**Verify:**

```bash
ls -la ~/.config/gcp/
```

You should see one line containing `bookkeeping-sa.json` with permissions `-rw-------`.

---

# Part 3 — Make your Google Sheet and grant access (2 minutes)

## Step 5. Create a new blank sheet

1. In your web browser, go to **https://sheets.new**
2. A blank spreadsheet opens.
3. At the top-left where it says **Untitled spreadsheet**, click and rename it to something like `My AutoACCT Expenses`.

## Step 6. Note the tab name (very important)

Look at the bottom-left of your sheet. You'll see one tab:
- If you see `Sheet1` → write down "Sheet1"
- If you see `工作表1` → write down "工作表1"

You'll paste this exact name into `config.json` in Step 10. **Tab name and config must match exactly, or saving will fail.**

## Step 7. Paste in the table headers

1. Click cell **A1** (top-left cell).
2. Copy this **entire single line** (don't worry that it looks long — it's one line with invisible tab characters separating the 14 headers):

   ```
   Date	Merchant	Category	Amount	Currency	Amount (HKD)	FX Rate	FX Date	Payment Method	Line Items	Raw OCR	Note	Receipt	Logged At
   ```

3. Paste into cell A1. The 14 headers automatically spread across columns A through N.

**Verify:** Column A says `Date`, Column N (scroll right if needed) says `Logged At`.

## Step 8. Share the sheet with the service account

This is the step that lets the skill write into your sheet.

1. Click the green **Share** button (top right of the sheet).
2. In the "Add people, groups, and calendar events" box, **paste the service-account email that `decrypt-key.sh` printed back in Step 4**. It looks like:
   ```
   bookkeeping@autoacct.iam.gserviceaccount.com
   ```
3. Make sure the role on the right says **Editor** (not Viewer / Commenter).
4. **Uncheck "Notify people"** — there's no real person on the other end of that email.
5. Click **Send** (or **Share**, depending on the dialog).

**Verify:** click Share again, scroll the list of people with access. You should see two entries: yourself (Owner) and the service-account email (Editor).

## Step 9. Copy the sheet's URL

Look at your browser's **address bar** — the URL of your sheet looks something like:

```
https://docs.google.com/spreadsheets/d/1abcDEF...xyz123/edit#gid=0
```

**Just copy the whole URL.** Click in the address bar, press **Command (⌘) + A** to select all, then **Command (⌘) + C** to copy.

(The script is smart enough to pull the sheet ID out of the URL. If you happen to know what the ID alone looks like, pasting just the ID also works — but the URL is easier to copy.)

---

# Part 4 — Connect the skill to your sheet (1 minute)

## Step 10. Create the config file

Back in your Terminal, paste and run:

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
cp config.example.json config.json
```

Nothing visible happens — that's expected. The Terminal just made a copy of the template.

## Step 11. Edit the config file with your sheet ID and tab name

1. Open the config file with TextEdit (Mac's built-in text editor):

   ```bash
   open -e config.json
   ```

   A TextEdit window opens showing:

   ```json
   {
     "sheet_id": "PASTE_YOUR_GOOGLE_SHEET_URL_OR_ID_HERE",
     "worksheet": "Sheet1",
     "service_account_path": "~/.config/gcp/bookkeeping-sa.json",
     "hkd_fx_provider": "frankfurter"
   }
   ```

2. Replace `PASTE_YOUR_GOOGLE_SHEET_URL_OR_ID_HERE` with the URL you copied in Step 9. **Keep the double quotes around it.**

3. If your tab is `工作表1` (Chinese UI), change `"Sheet1"` to `"工作表1"`. Otherwise leave it.

4. **Leave the other two lines alone** — they already point at the JSON file you placed in Step 4.

   The file should now look something like:

   ```json
   {
     "sheet_id": "https://docs.google.com/spreadsheets/d/1abcDEF...xyz123/edit#gid=0",
     "worksheet": "Sheet1",
     "service_account_path": "~/.config/gcp/bookkeeping-sa.json",
     "hkd_fx_provider": "frankfurter"
   }
   ```

5. Save: **Command (⌘) + S**, then close TextEdit.

**Important:** TextEdit sometimes converts plain quotes (`"`) into "smart quotes" (`"` and `"`). If your AI agent later complains about JSON errors, this is usually why. To prevent this:
- Before pasting: **TextEdit menu → Format → Make Plain Text** (if "Make Rich Text" is shown instead, you're already in plain text — good).
- Or ask your AI agent: "Open my config.json and check for smart quotes."

---

# Final test — Confirm it all works (30 seconds)

Paste this into the Terminal and run:

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' | python3 ~/.openclaw/workspace/skills/AutoACCT/scripts/append_row.py
```

**What success looks like:**
```
OK 'Sheet1'!A2:N2
```
(or `'工作表1'!A2:N2` if you used the Chinese tab name)

Switch to your Google Sheet — there's a new row with `TEST` as the merchant. **You're done.** Delete the test row, then go drop a real receipt into your AI chat.

**What failure looks like, and how to fix it:** see the table below.

---

# Common problems

| You see | What it means | How to fix |
|---|---|---|
| `HTTP 403` or `The caller does not have permission` | You forgot Step 8 (sharing the sheet with the service-account email), or the email was typed incorrectly | Re-run `bash scripts/decrypt-key.sh` to print the email again, then re-share the sheet with that exact address, role Editor. |
| `HTTP 400: Unable to parse range` | The `worksheet` in `config.json` doesn't match the actual tab name | Open `config.json`, fix it to exactly match the tab name at the bottom-left of your sheet (`Sheet1` or `工作表1`). |
| `HTTP 404` or `Requested entity was not found` | The `sheet_id` in `config.json` is wrong | Open your sheet in the browser, copy the **full URL** from the address bar, paste it into `sheet_id` (replacing whatever's there). |
| `FileNotFoundError ... bookkeeping-sa.json` | The JSON file isn't where `config.json` says it is | Run `ls -la ~/.config/gcp/` — confirm the file is there with the exact name `bookkeeping-sa.json`. If it has a different name, either rename it or update `service_account_path` in `config.json`. |
| `ImportError: No module named 'googleapiclient'` | You skipped or partially failed the `pip install` step | Re-run `pip install google-api-python-client google-auth`. If that fails, try `pip3` or `python3 -m pip install ...`. |
| `config.json not found` | You skipped Step 10 | Run `cp config.example.json config.json` from inside the skill folder. |
| `Expecting value: line 1 column 1` (JSON error) | Your `config.json` has smart quotes or is otherwise malformed | Re-open with TextEdit in plain-text mode (Format → Make Plain Text), or ask your AI agent to repair it. |

If your problem is not in this table: copy the **exact error text** and paste it to your AI agent along with "I'm following the AutoACCT deploy guide and I got this error at Step N."

---

# What to do when you want to change something later

| You want to... | What to do |
|---|---|
| Use a different sheet | Repeat Steps 5–9 on the new sheet (including the Share-with-service-account step), then update `sheet_id` and `worksheet` in `config.json`. |
| Stop the skill writing to a sheet | Open the sheet → Share → find the service-account email → click trash icon → Save. The skill will get HTTP 403 on the next attempt. |
| Move to a new computer | Repeat Parts 1, 2, and 4 on the new computer (re-clone, re-run `decrypt-key.sh`, copy `config.json`). Your sheet and its sharing don't change. |
| You think the decrypted JSON or passphrase leaked | Message your admin immediately. They will rotate both the passphrase **and** the underlying GCP key; you'll then `git pull` + re-run `decrypt-key.sh` with the new passphrase. |

---

# Summary of what just happened (so you understand what you set up)

1. **Your computer** has the AutoACCT skill in `~/.openclaw/workspace/skills/AutoACCT/`. When you drop a receipt photo into your AI chat, the AI runs `scripts/append_row.py`, which is a small Python program.
2. **The repo ships an encrypted JSON file** (`secrets/bookkeeping-sa.json.enc`) — the service-account key locked with AES-256 + your team's passphrase. `decrypt-key.sh` unlocks it into `~/.config/gcp/bookkeeping-sa.json` (mode 600). The unlocked JSON authenticates the Python program as the service account your admin created in Google Cloud.
3. **The service account** is allowed to edit Google Sheets only when those sheets have been shared with its email. You shared *your* sheet with it in Step 8 — so it can only write to your sheet (and any other sheet you might share with it later).
4. **Other users on your team** decrypt the **same JSON file** with the **same passphrase** but write to **their own sheets**. The service account can write to each of their sheets only because each user has shared *their own* sheet with it. They cannot see your sheet, and you cannot see theirs — unless someone explicitly shares.

That's it. Welcome to AutoACCT.
