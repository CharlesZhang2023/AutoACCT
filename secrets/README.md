# secrets/

This directory holds the team's shared Google Cloud service-account key,
encrypted with **AES-256-CBC + PBKDF2 (100k iterations)** using a single
team passphrase.

| File | What it is |
|---|---|
| `bookkeeping-sa.json.enc` | The SA private key, encrypted. Safe to commit. |

## To decrypt (end users)

```bash
bash scripts/decrypt-key.sh
```

You'll be prompted for the team passphrase. Ask your admin if you don't have
it — it's stored in the team password manager (1Password / Bitwarden), never
in this repo or in chat history.

On success the decrypted JSON lands at `~/.config/gcp/bookkeeping-sa.json`
with mode 600, and the script prints the service-account email you need to
share your Sheet with.

## To rotate the passphrase (admin)

```bash
# Decrypt with old passphrase
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -d \
  -in secrets/bookkeeping-sa.json.enc \
  -out /tmp/sa.json

# Re-encrypt with new passphrase
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt \
  -in /tmp/sa.json \
  -out secrets/bookkeeping-sa.json.enc

shred -u /tmp/sa.json   # or: rm -P on macOS

git add secrets/bookkeeping-sa.json.enc
git commit -m "secrets: rotate passphrase"
git push
```

Then update the passphrase in the team password manager and notify users.

## To rotate the SA key itself (admin)

When the underlying GCP key needs replacement (key leak, periodic rotation,
team member departure):

1. In GCP Console → Service Accounts → `bookkeeping@autoacct...` → Keys → **Add Key** → JSON → download.
2. **Delete the old key** in the same panel.
3. Re-encrypt:
   ```bash
   openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt \
     -in ~/Downloads/<new-key>.json \
     -out secrets/bookkeeping-sa.json.enc
   ```
4. `git add` + `commit` + `push`.
5. Tell users to `git pull` and re-run `bash scripts/decrypt-key.sh`.

## Why this works

- AES-256 + PBKDF2 with 100k iterations makes brute-forcing infeasible for a
  strong (>32 char) random passphrase, even with the ciphertext public.
- Encrypted blob in git history means anyone with the passphrase can install
  with just `git clone` + run the decrypt script — no out-of-band file
  transfer needed.
- Passphrase distribution is the only remaining out-of-band step; that
  belongs in a password manager.

## Threats this does NOT protect against

- Anyone with the passphrase can read/write **all team sheets** shared with
  the service account. The passphrase is the team's collective trust boundary.
- If the passphrase leaks publicly: rotate both passphrase **and** the
  underlying GCP key (see above). Don't just rotate the passphrase.
- A user who has previously decrypted the key has a plaintext copy on their
  machine. Removing them from the team requires rotating the GCP key (the
  passphrase rotation is not enough — they already have a decrypted JSON).
