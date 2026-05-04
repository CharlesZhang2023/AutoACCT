---
name: bookkeeping
description: Extract expense data from a receipt/invoice image (plus optional caption) and append it to a Google Sheet with HKD conversion. Use whenever the user provides a receipt image and wants it logged, or forwards a WhatsApp-style message that contains a receipt.
---

# Bookkeeping — Receipt → Google Sheet

Default working language: **English**. All written output (row values, replies) is English unless the user explicitly requests otherwise.

## When to use
- User provides a receipt / invoice / payment-screenshot image and wants it recorded.
- User says "log this", "record this expense", "add to bookkeeping", "记一下" with an image.
- Caption may be empty, or may add context (who paid, split %, category hint, payment method). Always incorporate caption if present.

## Prerequisites (check once per session)
1. `~/.openclaw/workspace/skills/bookkeeping/config.json` exists. If only `config.example.json` is present, **stop** and tell the user to copy it and fill in `sheet_id`, `worksheet`, `service_account_path`. Point them at `scripts/setup.md`.
2. Python deps installed: `google-api-python-client`, `google-auth`. If `append_row.py` fails with ImportError, instruct the user to run `pip install google-api-python-client google-auth` and retry.

## Workflow
1. **Extract** fields from the image using vision. Caption is auxiliary — never let caption override a legible receipt, but use it to fill gaps (category hint, note, payment method).
2. **Normalize** per the rules below.
3. **Convert to HKD** by running:
   ```
   python ~/.openclaw/workspace/skills/bookkeeping/scripts/fx_convert.py <amount> <currency> --date <yyyy-mm-dd>
   ```
   Output is `<hkd_amount>\t<fx_rate>\t<fx_date>` (tab-separated). If currency is HKD, skip the call and set `amount_hkd=amount`, `fx_rate=1`, `fx_date=<date>`.
4. **Append the row** by piping JSON into:
   ```
   echo '<json>' | python ~/.openclaw/workspace/skills/bookkeeping/scripts/append_row.py
   ```
   Keys must match `schema.md` (snake_case: `date`, `merchant`, `category`, `amount`, `currency`, `amount_hkd`, `fx_rate`, `fx_date`, `payment_method`, `line_items`, `raw_ocr`, `note`, `receipt`). Script adds `logged_at` automatically.
5. **Report** to the user: the row you wrote and any field you had to guess.

## Normalization rules
- **Date** → `yyyy-mm-dd`. Use the receipt date. If no date visible, fall back to today and flag it.
- **Amount** → grand total, numeric, no currency symbol. Tax/tip already included.
- **Currency** → ISO-4217 code (USD, CNY, HKD, JPY, EUR, GBP, …). Infer from symbol and language. If symbol is just "$" and context is ambiguous, check merchant country; if still unclear AND amount > 500 units, **ask**.
- **Merchant** → clean chain name. Strip store numbers, addresses, register IDs. "STARBUCKS #1234 SHENZHEN" → `Starbucks`.
- **Category** → pick exactly one from `categories.md`. Default to `Other` rather than invent a new one.
- **Payment method** → one of `cash`, `card`, `alipay`, `wechat`, `octopus`, `other`, or `""`. Only fill if visible on receipt or stated in caption.
- **Line items** → `"name xQty price; name xQty price"`. Skip (empty string) if handwritten, illegible, or trivially one item.
- **Raw OCR** → full receipt text, newlines as literal `\n`. For audit. Trim trailing whitespace only.
- **Note** → user's caption verbatim. Empty string if none.
- **Receipt** → if image arrived as a URL, use it. If it's a local path, write the local path and tell the user to wire Drive/S3 upload if they want hotlinkable receipts.

## Caption handling
- Caption overrides only when the receipt lacks that field, OR when caption is an explicit correction ("this is actually groceries, not food").
- Split expenses: if caption says "split 50/50 with Alice", still log the **full** amount — splitting belongs in a separate sheet/column. Note the split in the Note field.

## When to ask vs. guess
- **Ask** when: currency is ambiguous and amount is non-trivial; date could be MM/DD vs DD/MM and merchant country is unclear; amount is unreadable.
- **Guess + flag** when: category is multi-fit (pick most specific, mention it); merchant name is partially OCR'd (pick best guess, mention it).
- **Never silently guess** the amount or the currency.

## Reply format
```
Logged to <worksheet> (row <N>):
  Date:     2026-04-20
  Merchant: Starbucks
  Category: Food & Drink
  Amount:   CNY 48.00  →  HKD 51.74  (fx 1.0779 on 2026-04-20)
  Payment:  wechat
  Note:     "breakfast with Mark"
Guessed: category (receipt didn't specify; "Food & Drink" based on items).
```
Omit the `Guessed:` line when nothing was guessed.

## Reference files
- `categories.md` — fixed category list.
- `schema.md` — Google Sheet column order and formats.
- `scripts/setup.md` — one-time setup (service account, sheet share, deps).
