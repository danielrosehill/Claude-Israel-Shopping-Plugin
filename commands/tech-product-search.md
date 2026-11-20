---
name: tech-product-search
description: Search the four tier-1 Israeli tech retailers — Ivory, KSP, Bug, TMS — for a consumer-tech product (laptop, phone, peripheral, accessory, charger, cable, monitor, TV, headphones, etc.) and return prices ranked low-to-high. Handles Hebrew-term resolution Uses the bundled KSP/Ivory scripts and curl, with a real browser only for bot-walled sites. For a full multi-channel search (Zap, trusted vendors, imports) use the find-product skill.
---

# Tech Product Search — Ivory / KSP / Bug / TMS

Finds a consumer-tech product across the four tier-1 Israeli tech chains and returns a ranked price table.

> See `docs/search-strategies.md` for the full backend chain, Hebrew-term resolution, URL patterns, KSP regular-vs-Eilat rule, and store-metadata merge convention.

## When to use

- User asks to price, find, or compare consumer tech across the big Israeli chains.
- User names any of Ivory, KSP, Bug, TMS specifically.
- For cross-retailer comparison including tier-2 and niche stores, prefer `/search-zap` first; use this when Zap misses or direct retailer pricing is wanted.

## Workflow

1. **Resolve the Hebrew category noun** (see `docs/search-strategies.md` § Hebrew-term resolution). State it in the first user-facing line.
2. **For each of the four retailers**, run the backend chain (script → curl/WebFetch → real browser → web search; see strategies doc) in parallel. KSP: `skills/ksp-branch-stock/scripts/ksp_stock.py "<q>" --all`. Ivory: `skills/ivory-branch-stock/scripts/ivory_stock.py "<q>" --all`. Cap 5 results per retailer.
   For computer parts, also search wave 2 of `computer_parts` in `data/trusted-vendors.json` (Plonter) when these four are thin.
3. **Retry** with a Hebrew synonym or brand+model only if a retailer returns zero.
4. **KSP price rule:** quote the regular (non-Eilat) price unless the user asked about Eilat.
5. **Rank low-to-high** by VAT-inclusive ILS price.

## Output

```
## <product> — Israeli tech stores
Hebrew query: <hebrew noun> <brand> <model>
Backends used: Ivory=<script|curl|browser|…>, KSP=<…>, Bug=<…>, TMS=<…>

| # | ₪ (inc. VAT) | Product | Retailer | Link |
|---|---|---|---|---|
| 1 | … | … | … | … |

### Notes
- Any retailer that returned nothing and what fallbacks were tried.
- Price outliers / stock warnings.
- KSP: regular price quoted (Eilat price if seen: ₪X).
```

## Rules

- Never invent a price. If you can't extract it, say so.
- Quote ILS inc-VAT — never USD on these retailers.
- Never silently substitute a similar-but-different model. If the exact SKU isn't carried, name the closest match and flag it.
- For retailers outside this set, point the user to `/general-search` or `/search-zap`.
- When the user wants to pick up in a store, or names a branch, run the `ksp-branch-stock` / `ivory-branch-stock` skills on the shortlisted items and add a branch column.
