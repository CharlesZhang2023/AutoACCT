#!/usr/bin/env bash
# decrypt-key.sh — decrypt the bundled service-account key into
# ~/.config/gcp/bookkeeping-sa.json. You'll be prompted for the passphrase
# (ask your admin; it's stored in the team password manager).
#
# Usage:
#   bash scripts/decrypt-key.sh
#
# Idempotent: re-running overwrites the existing decrypted file.
set -euo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_DIR/secrets/bookkeeping-sa.json.enc"
DEST_DIR="$HOME/.config/gcp"
DEST="$DEST_DIR/bookkeeping-sa.json"

if [[ ! -f "$SRC" ]]; then
  echo "error: encrypted key not found at $SRC" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# AES-256-CBC + PBKDF2 (100k iter) + salt. Passphrase read interactively.
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -d -in "$SRC" -out "$DEST"

chmod 600 "$DEST"
echo "Decrypted to $DEST"

SA_EMAIL=$(python3 -c "import json; print(json.load(open('$DEST'))['client_email'])" 2>/dev/null || true)
if [[ -n "$SA_EMAIL" ]]; then
  echo ""
  echo "Service-account email: $SA_EMAIL"
  echo "Next step: share your Google Sheet with this email (Editor)."
fi
