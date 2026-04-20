# Google Sheet Column Schema

`append_row.py` writes columns in this exact order. Create the header row manually once during setup.

| Col | Header          | Format                                       | Source                          |
|-----|-----------------|----------------------------------------------|---------------------------------|
| A   | Date            | `yyyy-mm-dd`                                 | receipt date, else today        |
| B   | Merchant        | string                                       | cleaned chain name              |
| C   | Category        | one of `categories.md`                       | inferred                        |
| D   | Amount          | decimal                                      | grand total, original currency  |
| E   | Currency        | ISO-4217 (USD, CNY, HKD, …)                  | inferred                        |
| F   | Amount (HKD)    | decimal                                      | `fx_convert.py` output          |
| G   | FX Rate         | decimal, original→HKD                        | `fx_convert.py` output          |
| H   | FX Date         | `yyyy-mm-dd`                                 | `fx_convert.py` output          |
| I   | Payment Method  | `cash` / `card` / `alipay` / `wechat` / `octopus` / `other` / `""` | receipt or caption |
| J   | Line Items      | `"name xQty price; name xQty price"` or `""` | receipt                         |
| K   | Raw OCR         | full text, `\n` for newlines                 | receipt                         |
| L   | Note            | verbatim caption                             | user                            |
| M   | Receipt         | URL or local path                            | image ref                       |
| N   | Logged At       | ISO-8601 UTC timestamp                       | auto (`append_row.py`)          |
