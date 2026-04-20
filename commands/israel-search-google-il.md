---
name: search-google-il
description: Use Google as an Israeli-shopping discovery surface. Runs the common IL query patterns — `<product> site:.il`, `מחיר <hebrew product>`, `קנה <hebrew product>`, plus Google Shopping IL — to surface listings that per-retailer searches and Zap miss. Use as the first discovery pass for niche products, for finding specialist retailers not in israeli-stores.json, or when retailer-specific searches return nothing.
---

# Search Google IL

Google is often a better starting point than any single retailer's search box for Israeli shopping — it indexes every IL retailer whose site is crawlable, surfaces specialist shops that aren't in our curated list, and catches listings that Zap doesn't index.

This command runs the common Google query patterns used for manual Israeli-shopping discovery.

## When to use

- **Discovery mode** — "find me some Israeli listings for X" with no specific retailer in mind.
- **Niche products** — tactical gear, specialist audio, photography accessories where the mainstream chains don't carry it.
- **Hebrew-term verification** — running a `site:.il` search on a brand/model is the fastest way to confirm the Hebrew retail term (pair with `discover-hebrew-term`).
- **Sanity check** — after a retailer-specific search, run Google to confirm the price ranking or catch cheaper options.

## Backend choice

Playwright MCP. Google Shopping blocks most scrapers — Tavily is not reliable here.

Navigate to `https://www.google.com/search` and submit the query. Set locale to Israel where helpful:

- `gl=il` — geolocation Israel (prices in ILS, IL retailers ranked first)
- `hl=he` — Hebrew interface (results include Hebrew-only pages)
- `tbm=shop` — Google Shopping vertical

## Query patterns (try in this order)

### 1. Brand + model + `site:.il`

Best for: known SKU lookups, Hebrew-term reverse-lookup, finding ANY IL retailer that carries the product.

```
"<brand model>" site:.il
```

Examples:
- `"Anker A2343" site:.il`
- `"Nitecore HC65" site:.il`
- `"Eneloop BK-3MCCE" site:.il`

Use quotes around the model number — prevents Google from relaxing it.

### 2. Brand + model + `site:co.il`

Like (1) but narrower — commercial-only. Skips `.org.il`, `.ac.il`, `gov.il`. Use when (1) returns too much noise from forums / news.

### 3. Hebrew term + `מחיר` (price)

Best for: surfacing commercial listings when all you have is a product class, not a specific model.

```
מחיר <hebrew term> <optional brand>
```

Examples:
- `מחיר עמדת טעינה Anker Prime`
- `מחיר פנס ראש Nitecore`
- `מחיר סוללות נטענות AA Eneloop`

The word `מחיר` ("price") is a strong commercial-intent signal — pages with "price" next to the product noun are almost always listings, not blogs.

### 4. Hebrew term + `קנה` (buy)

Similar to `מחיר` but noisier. Use as a fallback.

### 5. Hebrew term + `בארץ` / `ישראל`

Use when Google is returning too many international results and `site:.il` is over-filtering.

```
<hebrew term> בארץ
<hebrew term> ישראל
```

### 6. Google Shopping IL

Fast survey across multiple retailers with price ranking built in.

```
https://www.google.com/search?tbm=shop&gl=il&hl=he&q=<hebrew query>
```

Coverage is patchy — not all IL retailers feed Google Shopping — but it's a fast complement to Zap.

## Workflow

1. **Confirm the Hebrew term.** Check `data/hebrew-category-map.json`. If missing, invoke `discover-hebrew-term` first.
2. **Run pattern 1** (`"brand model" site:.il`). If this is a known-SKU query, this alone is usually enough.
3. **If pattern 1 is empty or too narrow, run pattern 3** (`מחיר <hebrew>`). This catches more listings.
4. **Run Google Shopping IL** (pattern 6) in parallel for a price-ranked cross-check.
5. **Extract results.** For each result, capture:
   - Domain (check against `data/israeli-stores.json` — is it in our known list?)
   - Page title (contains Hebrew product name + price on most retail sites)
   - Listed price if visible in the Google snippet
6. **Filter.** Drop:
   - News sites (ynet, walla, calcalist, haaretz, themarker, geektime, etc.)
   - Blogs and review sites (unless the user explicitly wants reviews)
   - Dead domains / parked pages
   - Duplicate domains (keep the most-relevant result per domain)
7. **Rank.** Group by domain, surface the top 3–5 unique retailers with best prices. Don't invent prices — if Google didn't show one in the snippet, flag as "visit for price".

## Output

```
## {product} — Google IL discovery
Hebrew term(s) used: {hebrew}
Patterns run: {pattern numbers}

### Retailers found

| # | Retailer | Domain | Listing title | Visible price | Link |
|---|----------|--------|---------------|---------------|------|
| 1 | ...      | ...    | ...           | ₪...          | ...  |

### Notes
- Retailers not in data/israeli-stores.json (potential additions): ...
- Patterns that returned nothing: ...
- Any suspicious / dropshipping-looking domains: ...
```

## Rules

- Never click through to dropshipping / grey-market sites without flagging.
- When Google Shopping and per-retailer results disagree on price, trust the retailer page (Shopping snippets go stale).
- If a result comes from a retailer not in `data/israeli-stores.json` but looks legitimate, mention it in output — we may want to add it.
- Don't run more than 3–4 query variants per session — Google rate-limits. Pick the most relevant patterns for the query type.
