---
description: Quick Israeli price vs international RRP check with import-cost realism
argument-hint: [model names, optional — defaults to current shortlist]
---

# Market Check (Israel)

Quick price-sanity check for Israeli buyers — compare Israeli retail pricing vs international RRP for the shortlist (or the models in `$ARGUMENTS`). Lighter weight than a full `/source` run.

Useful when you want to answer "is this a good price?" without running the whole sourcing waterfall.

## Steps

1. **Identify the models:**
   - If `$ARGUMENTS` is provided, use that list.
   - Otherwise, use the top picks from the most recent file in `from-ai/recommendations/`, or the CONSIDER candidates from `from-ai/shortlist.md`.

2. **Get Israeli prices** from:
   - `from-ai/sourcing.md` if already generated (use the "Israeli domestic" row from the waterfall)
   - `for-ai/catalogs/[vendor]/` or `data/extracted/products.csv` if available
   - Use the `search-main-tech-stores` / `search-major-retailers` / `search-by-category` skills for a fresh pull

3. **Look up international RRP:** official manufacturer site > official regional distributor > major reputable retailers (sanity check). Use WebFetch/WebSearch. Never guess.

4. **Convert currencies** with the `convert-currency` skill (live rate).

5. **Build a table:**

   | Model | Israeli price (₪) | USD eq. | Intl RRP (USD) | Δ (%) | Verdict |
   |---|---|---|---|---|---|

   Verdict values (use the `compare-to-international` skill for consistency):
   - `cheaper locally` — Israeli beats RRP
   - `parity` (±5%)
   - `mild markup` (5–20%)
   - `above average` (20–40%)
   - `heavy markup` (>40%)

6. **Apply the effective markup threshold** (spec per-purchase override first, else Standing preferences snapshot default — typically 40%). Flag any model above the threshold.

7. **Import realism for Israel:** Amazon or AliExpress landed costs to IL typically add:
   - Amazon: shipping ($15–40 for small items, more for large) + 18% VAT + possible customs duty (imports >$75 USD de minimis)
   - AliExpress: shipping usually cheap/free but 2–6 week lead time + same VAT/customs rules

   A 40% Israeli markup is often still cheaper than importing once all-in costs are counted.

8. **Write the result** to `from-ai/research/market-check-YYYY-MM-DD.md` and print the table inline.

9. **End with a one-line recommendation:** buy domestically, import via Amazon-IL, use AliExpress, or mixed (which specific items to source where).
