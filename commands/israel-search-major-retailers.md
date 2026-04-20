---
name: search-major-retailers
description: Search the broader major Israeli retailers — Ace, Home Center, Office Depot, Audioline — for products that the tech-focused chains may not carry (home appliances, office gear, audio equipment, hardware-store overlap). Use when the request leans appliance/home/office rather than pure consumer electronics. Prefer `search-zap` first if the SKU is mainstream — Zap covers these retailers too.
---

# Search Major Retailers

Tier-2 major chains that sit alongside the pure tech stores. Use when the product is more "household/office" than "consumer tech."

| Retailer | Best for |
|----------|----------|
| Ace | Hardware, tools, garden, some electronics |
| Home Center | Home improvement, appliances, fixtures |
| Office Depot | Office supplies + tech accessories |
| Audioline | Audio equipment specialist |

> **Read first:** `data/discovery-techniques.md`. The discovery playbook applies to all search skills — Hebrew term resolution, fallback chain, etc.

## Discovery order

1. **`search-zap`** — covers all four of these too. Try first unless the user explicitly named one of these retailers.
2. **This skill** — direct queries to the four when Zap is empty or user wants a specific retailer.
3. **`search-google-il`** — for niche category items.

## Preflight — Hebrew term resolution

Same as `search-main-tech-stores`:

1. Check `data/hebrew-category-map.json`.
2. Run `discover-hebrew-term` if missing.
3. Build query as `<hebrew category> <brand Latin> <model Latin>`.
4. Have all `he_terms` ready to retry.

## Backend choice

Same as the other search skills: Playwright (default, local IP) or Tavily (fast fallback). Ask the user once per session.

## How to find each retailer's search

Same caveat as `search-main-tech-stores` — `data/retailers.md` URL patterns are last-known-good hints, not contracts. If a pattern fails, navigate to the retailer's homepage, locate the search input, submit the Hebrew query, and read the results. Update `data/retailers.md` with whatever you discover.

## Workflow

1. Preflight — Hebrew term resolution.
2. For each of the four retailers, submit the Hebrew query (homepage-form approach if URL pattern is unreliable).
3. Try alternate `he_terms` if the primary returns nothing.
4. Apply VAT rules from `data/shopping-rules.md`.
5. Rank low-to-high.

## Fallback

If a retailer comes back empty after all `he_terms`:

1. Brand + model only (no Hebrew noun).
2. `search-google-il` with `<brand model> site:<retailer-domain>`.
3. Skip and note in output.

## Output

Same table format as `search-main-tech-stores`. Note when a retailer is clearly out-of-category for the query (e.g. searching Audioline for a vacuum cleaner — say so).

## Rules

- Cap at 5 results per retailer.
- If none of these retailers fit (e.g. user asks for a niche tactical product), suggest `search-by-category` instead.
- Out-of-category misses are normal and not worth flagging unless every retailer missed.
