---
name: ksp-branch-stock
description: Check whether a product is in stock at a specific KSP branch (or the user's home branch), straight from KSP's own per-branch stock data — no clicking through the "בדיקת מלאי בסניפים" popup. Takes a search query, a ksp.co.il item URL, an item id or a KSP catalogue number (מק"ט); returns price plus in-stock and last-unit flags per branch. Use for "is X in stock at KSP <branch>", "which KSP branch near me has X", "can I pick this up today at KSP", or any KSP availability question.
---

# KSP branch stock

Per-branch availability for KSP items, filtered to the branches the user cares about.

## When to use

- "Is <product> in stock at KSP King George / Talpiot / <branch>?"
- "Which KSP branch has it?", "can I pick it up today?"
- Any KSP search where branch pickup matters. For price comparison across chains, use `/tech-product-search` first, then this for stock.

## Home branches

Branch filter order: `--branch` flags, then `<plugin-data-dir>/home-branches.json`, then every branch. The plugin data dir is `$CLAUDE_USER_DATA/israel-shopping/`, else `$XDG_DATA_HOME/claude-plugins/israel-shopping/`, else `~/.local/share/claude-plugins/israel-shopping/`.

```json
{ "ksp": ["57"], "ivory": ["24"] }
```

If the file is missing and the user names a usual branch, offer to write it. Branch ids, keys and names: `references/ksp-branches.md`.

## Run

```bash
python3 scripts/ksp_stock.py "logitech f310"                       # search, top 8
python3 scripts/ksp_stock.py https://ksp.co.il/web/item/11239       # one item
python3 scripts/ksp_stock.py 11239 --branch talpiot --branch 57     # explicit branches
python3 scripts/ksp_stock.py --sku 20767 --all                      # by מק"ט, every branch
```

Stdlib only, no install. `--branch` accepts an id (`57`), key (`jeruscenter`) or a name substring (`קינג`, `talpiot`). Output is JSON: per item `id`, `sku`, `name`, `price_ils`, `eilat_price_ils`, `url`, `branches_in_stock` (national count) and `branches[]` with `in_stock` and `last_unit`.

**Search in Hebrew as well** for generic products (`בקר משחק`, not just `gamepad`): KSP's search is title-based. Hebrew nouns: `docs/search-strategies.md`.

## If KSP blocks it (exit code 2)

KSP's bot filter passes these API calls only with browser-style `Sec-Fetch-*` headers, which the script sends. After roughly 100 rapid calls it starts returning 403 for search and item lookups for a while (the stock endpoint kept answering). On exit 2:

1. Open any `ksp.co.il` page in a real browser: the agent browser if one exists, else claude-in-chrome, else Playwright.
2. Take `scripts/ksp_stock_browser.js`, replace `__TARGET__` (query, URL or id) and `__BRANCHES__` (JSON array, `[]` = all), and pass it as the `function` of a browser evaluate call. It returns the same JSON.

## Reading the data

- `in_stock` comes from `qnt` in KSP's stock feed, which is a 0/1 flag, not a unit count. `last_unit: true` means one unit left; say so, since it can be gone by the time the user arrives.
- `branches_in_stock` equals the length of `pickupDeliveryBranches` in KSP's search results (checked across 10 items).
- Prices are VAT-inclusive ILS. Quote the regular price, not Eilat (`docs/search-strategies.md`).

## Output to the user

```
## <query> — KSP stock, <branch names>
Checked <time>.

| ₪ | Product | <Branch> | KSP-wide | Link |
|---|---|---|---|---|
| 105 | Logitech F310 | Yes (last unit) | 73 branches | … |
```

List items not at the home branch but in stock nearby (same `region`) in a short note.

## Rules

- Never report stock you didn't fetch. If a call failed, say which.
- An item whose every branch is `in_stock: false` while the website shows "add to cart" usually means the wrong id was passed to the stock endpoint (see the `sku` trap in `docs/search-strategies.md`). Re-check before reporting "out of stock everywhere".
- Keep searches to what's needed (`--limit`): every result costs one stock call.
