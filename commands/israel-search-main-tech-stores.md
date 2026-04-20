---
name: search-main-tech-stores
description: Search the four mainstream Israeli tech retailers — KSP, Ivory, Bug, TMS — for a product and return prices ranked low-to-high. Use when the user asks to compare prices on consumer tech (laptops, phones, peripherals, accessories) across the big Israeli chains. NOTE — for most price-comparison questions, prefer `search-zap` first; use this skill when Zap doesn't index the SKU, when the user wants direct retailer pricing, or as a fallback.
---

# Search Main Tech Stores

Search the tier-1 Israeli tech chains: **KSP**, **Ivory**, **Bug**, **TMS**. These four cover most consumer tech.

> **Read first:** `data/discovery-techniques.md`. The whole-system playbook for finding products in Israel — Hebrew term resolution, fallback chain, when to use what.

## Discovery order — when to invoke this skill

For the typical "find me cheapest X in Israel" query, this skill is **not** the first step:

1. **`search-zap`** — canonical aggregator, covers all four of these retailers plus more. Try this first.
2. **This skill** — only if Zap missed, the user wants a specific retailer's pricing, or you need direct-from-retailer confirmation.
3. **`search-google-il`** — for niche items the mainstream chains don't carry.

If the user asks "search KSP / Ivory / Bug / TMS specifically", come straight here.

## Preflight — Hebrew term resolution

Israeli retailer search returns nothing useful with raw English category nouns. Before touching any retailer:

1. Check `data/hebrew-category-map.json` for the product class.
2. If the class isn't mapped, invoke `discover-hebrew-term` first to derive and cache it.
3. Build the search query by combining: `<hebrew category> <brand in Latin> <model in Latin>`. Example: `עמדת טעינה Anker Prime A2343`, **not** `Anker Prime A2343 charging tower`.
4. If the map lists multiple Hebrew variants (`he_terms` array), be ready to try each — different retailers tag the same class differently.

## Backend choice

| Backend | When to use | Tools |
|---------|-------------|-------|
| **Playwright MCP** (default) | Default. Uses the user's local IP → correct Israeli pricing, correct shipping, no geo-blocks. Slower but accurate. Required for KSP and Bug (both have bot detection that blocks Tavily). | `mcp__playwright__*` |
| **Tavily MCP** (fallback) | Faster, no browser. Acceptable for Ivory and TMS. May return cached/stale prices. | `mcp__tavily__tavily_search` |

Ask the user once per session, default Playwright.

## How to find each retailer's search

**Do not trust hardcoded URL patterns** — they drift. Each retailer has a different search system that may change without notice.

The reliable approach: navigate to the retailer's homepage, find the search input, type the query, submit, then read the results. With Playwright:

1. `browser_navigate` to the retailer homepage.
2. `browser_evaluate` or `browser_snapshot` to find the search form (usually `input[name="q"]`, `input[type="search"]`, or `#qSearch`).
3. `browser_type` the Hebrew query into that input, with `submit: true`.
4. Wait for results, then `browser_snapshot` and extract product cards.

`data/retailers.md` has the **last-known-good** URL patterns as a starting hint, but treat them as candidates to verify, not contracts. If a documented pattern returns 404 or redirects to homepage, fall back to the homepage-form approach above and update `data/retailers.md` with what you discovered.

## Workflow

1. **Preflight** — Hebrew term resolution (above).
2. **For each of the four retailers**, in parallel where possible:
   - Submit the Hebrew query (homepage-form approach if URL pattern is unreliable).
   - Capture the top 5 product cards: title, price, link, in-stock indicator.
3. **Try Hebrew variants.** If a retailer returns nothing for the primary `he_terms[0]`, retry with `he_terms[1]` and `he_terms[2]` before declaring it absent.
4. **Apply VAT rules** from `data/shopping-rules.md`. On KSP always use the higher (regular, non-Eilat) price.
5. **Rank low-to-high** by VAT-inclusive ILS price.

## Fallback chain (if a retailer returns nothing)

For each retailer that comes back empty after trying all `he_terms`:

1. Try the same retailer with the **brand + model only** (no Hebrew category noun) — sometimes retailer search rejects the noun but accepts the SKU.
2. Try `search-google-il` with `<brand model> site:<retailer-domain>` — Google often has a better index of the retailer's catalog than the retailer itself.
3. Skip the retailer and note "no results across N variants" in the output.

## Output format

```
## {product} — main Israeli tech stores
Hebrew query terms tried: {he_terms used}
Backend: {Playwright | Tavily}

| # | Price (₪, inc. VAT) | Product | Retailer | Link |
|---|---------------------|---------|----------|------|
| 1 | ...                 | ...     | ...      | ...  |

### Notes
- Any VAT adjustments applied
- Any retailer that errored / timed out / had no results across all he_terms
- Any obvious outliers
- Any URL pattern in data/retailers.md found stale (with the new pattern, if discovered)
```

## Rules

- Cap at 5 results per retailer.
- Skip retailers that error; note them rather than failing the whole run.
- Never visit non-whitelisted domains.
- If both backends fail, report which one failed and offer to retry with the other.
- If the user-facing comparison would be more efficient via Zap, suggest `search-zap` instead and only continue if the user confirms.
