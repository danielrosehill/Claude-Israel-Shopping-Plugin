---
name: ivory-branch-stock
description: Check whether a product is in stock at a specific Ivory (אייבורי) branch, or the user's home branch, using the same data as Ivory's "הצג זמינות מלאי בסניפים" popup, without opening it product by product. Takes a search query, an ivory.co.il product URL or a product id. Returns price plus in-stock per branch. Use for "is X in stock at Ivory <branch>", "which Ivory branch has it", "can I pick it up today at Ivory", or any Ivory availability question.
---

# Ivory branch stock

Per-branch availability for Ivory products, filtered to the branches the user cares about.

## When to use

- "Is <product> in stock at Ivory King George / Talpiot / <branch>?"
- "Which Ivory branch has it?", "can I pick it up today?"
- Any Ivory search where branch pickup matters. For price comparison across chains, use `/tech-product-search` first, then this for stock.

## Home branches

Branch filter order: `--branch` flags, then `<plugin-data-dir>/home-branches.json`, then every branch. The plugin data dir is `$CLAUDE_USER_DATA/israel-shopping/`, else `$XDG_DATA_HOME/claude-plugins/israel-shopping/`, else `~/.local/share/claude-plugins/israel-shopping/`.

```json
{ "ksp": ["57"], "ivory": ["24"] }
```

If the file is missing and the user names a usual branch, offer to write it. Branch codes and names: `references/ivory-branches.md`.

## Run

```bash
python3 scripts/ivory_stock.py "בקר משחק"                                        # search, top 8
python3 scripts/ivory_stock.py "https://www.ivory.co.il/catalog.php?id=150475"   # one product
python3 scripts/ivory_stock.py 150475 --branch 24 --branch תלפיות                # explicit branches
python3 scripts/ivory_stock.py 150475 --all                                      # every branch
```

Stdlib only, no install, no browser: Ivory's endpoints answered plain HTTP on 2026-10-26. `--branch` accepts a branch code (`24`; keep leading zeros, e.g. `02`) or a name substring. Output is JSON: per item `id`, `name`, `price_ils`, `url`, `branches_in_stock` (national count) and `branches[]` with `code`, `name`, `address`, `in_stock`.

**Search in Hebrew as well** for generic products: Ivory's search ranks accessories that mention the term (a DualSense charging dock before the DualSense). Raise `--limit` or use a model name. Hebrew nouns: `docs/search-strategies.md`.

## Reading the data

- `in_stock: true` is the popup's green tick. `in_stock: false` covers both the orange "i" (not on the shelf, can be ordered to that branch) and the grey cross. Neither means "walk in and buy today".
- Ivory gives no unit count and no last-unit flag.
- Prices are VAT-inclusive ILS. Eilat branches show separate VAT-free prices on the site; quote the regular price.

## Output to the user

```
## <query> — Ivory stock, <branch names>
Checked <time>.

| ₪ | Product | <Branch> | Ivory-wide | Link |
|---|---|---|---|---|
| 299 | Sony DualSense, white | Yes | 34 branches | … |
```

Mention nearby branches with stock when the home branch has none.

## Rules

- Never report stock you didn't fetch. If a call failed, say which.
- If search returns nothing, retry with a Hebrew noun or the brand + model before saying Ivory doesn't carry it.
