---
name: search-by-category
description: Search Israeli stores filtered by product category — e.g. tactical gear, lighting, audio, photography, gaming, smart home. Pulls the candidate store list dynamically from data/israeli-stores.json categories[] field, then searches each. Use when the user asks for a category-specific product where the mainstream chains (KSP/Ivory/Bug/TMS) won't be the best source — niche specialist gear, brand-store-only items, etc.
---

# Search by Category

For category-specific shopping where mainstream chains aren't the right fit — e.g. "headlamps" wants `tactical` + `lighting` stores like Tactit and Nitecore, not KSP.

> **Read first:** `data/discovery-techniques.md`. The discovery playbook — Hebrew term resolution, fallback chain, when to use what.

## Discovery order

1. **`search-zap`** — Zap covers many specialist retailers too. Try first unless you already know the product is in a niche corner Zap doesn't index.
2. **This skill** — for niche / specialist categories where Zap is sparse.
3. **`search-google-il`** — to find shops that aren't in `israeli-stores.json` yet.

## Backend choice

Same dual-backend pattern as `search-main-tech-stores`: default to Playwright MCP (local IP), fall back to Tavily MCP if the user wants speed over accuracy. Ask once.

## Preflight — Hebrew term resolution

Same as the other search skills:

1. Check `data/hebrew-category-map.json` for the product class.
2. If missing, invoke `discover-hebrew-term`.
3. Build query as `<hebrew category> <brand Latin> <model Latin>` (or just `<hebrew category>` for a discovery-style search).
4. Carry all `he_terms` forward — small specialist retailers often use unusual phrasing.

## Available store categories

Read `data/israeli-stores.json`. Each entry has a `categories: []` field. The controlled vocabulary is:

`computers`, `mobile`, `peripherals`, `appliances`, `photography`, `audio`, `tv_av`, `gaming`, `office`, `lighting`, `tactical`, `power_battery`, `smart_home`, `security`, `tools`, `spare_parts`, `accessories`

## Workflow

1. **Map the user's request to one or more categories.** Examples:
   - "headlamps" → `lighting`, `tactical`
   - "DSLR camera bag" → `photography`, `accessories`
   - "gaming mouse" → `gaming`, `peripherals`
   - "UPS" → `power_battery`
2. **Filter the store list:**
   ```python
   stores = [s for s in data
             if s["is_tech"] is not False
             and any(cat in (s.get("categories") or []) for cat in target_cats)]
   ```
3. **Pick up to 8 stores** to actually search. Prioritise:
   - Stores tagged `is_tech: true` over `null`
   - Stores whose `description` mentions the user's specific product type
   - When in doubt, prefer stores with multiple matching categories
4. **Resolve Hebrew terms** (preflight above).
5. **Search each store** with the chosen backend. Don't trust a single URL pattern — try in this order:
   - Playwright: navigate to homepage, locate the search form (`input[type=search]`, `input[name=q]`, `input[name=s]`, `#search`), submit the Hebrew query
   - Fall-back URL patterns: `https://{domain}/?s={query}` (WordPress/WooCommerce default), `/search?q={query}`, `/catalogsearch/result/?q={query}` (Magento)
   - Tavily: `site:{domain} <hebrew query>`
6. **Try alternate `he_terms`** if the primary returns nothing.
7. **Apply VAT rules** from `data/shopping-rules.md`.
8. **Rank low-to-high** and report.

## Fallback (if a store returns nothing across all variants)

1. `search-google-il` with `<brand model> site:{domain}` — Google's index of the store may beat the store's own search.
2. Skip and note in output.

## Output

```
## {product} — category search ({categories joined})
Hebrew query terms tried: {he_terms}
Stores searched: {count}
Backend: {Playwright | Tavily}

| # | Price (₪, inc. VAT) | Product | Store | Link |
|---|---------------------|---------|-------|------|
```

If a store's site has no working search, skip it and note in output. Never invent results.

## Rules

- Only navigate to stores where `is_tech` is `true` or `null`. Never `false`.
- If the user's request doesn't map to any category, fall back to `search-main-tech-stores` and tell the user why.
- Cap at 3 results per store.
