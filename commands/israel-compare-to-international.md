---
name: compare-to-international
description: Compare an Israeli price (ILS) against the international RRP/MSRP or against a specific international retailer like Amazon, B&H, or the manufacturer's site. Reports the markup percentage and a verdict (good deal / fair / above average / expensive). Use when the user asks "is this a good price" or "how does this compare internationally".
---

# Compare to International

Given an Israeli price for a product, decide whether it's a good deal versus the international market.

## Backend choice

- **Playwright MCP** — best when comparing against a specific retailer page (Amazon, B&H, manufacturer). The user's local IP gives accurate region-specific pricing on the international side too.
- **Tavily MCP** — best for "what's the RRP" lookups across multiple sources at once.

Default to Tavily for RRP queries (faster, multi-source). Default to Playwright when the user names a specific URL.

## Inputs

- Product name + model
- Israeli price (ILS, VAT-inclusive — confirm with the user if ambiguous)
- Optional: comparison target (e.g. "vs Amazon US", "vs B&H", "vs RRP")

## Workflow

1. **Get the international reference price.** Sources to try, in order:
   - Manufacturer site (most authoritative for RRP)
   - Amazon US / Amazon DE / Amazon UK (whichever the user prefers, or default to US)
   - B&H Photo (good for camera/audio/computer gear)
   - Specialist retailers if the category demands it
2. **Convert to ILS** using the `convert-currency` skill or the live exchange rate (see `data/shopping-rules.md`).
3. **Calculate markup**: `(israeli_price - international_price_ils) / international_price_ils * 100`
4. **Apply the verdict scale** from `data/shopping-rules.md`:
   - ≤5% → GOOD DEAL
   - 5–15% → FAIR (typical Israel markup for imported tech)
   - 15–30% → ABOVE AVERAGE
   - >30% → EXPENSIVE — consider buying internationally

## Output

```
## {product} — Israel vs international

| Region          | Price                  | Source |
|-----------------|------------------------|--------|
| Israel          | ₪{x} (inc. VAT)        | {retailer} |
| {Region}        | {currency}{y} (≈ ₪{z}) | {source} |

**Markup:** {pct}%
**Verdict:** {GOOD DEAL | FAIR | ABOVE AVERAGE | EXPENSIVE}

### Notes
- Exchange rate used: 1 {ccy} = {rate} ILS ({date})
- Whether shipping/import duty is included on the international side
- Any caveats (e.g. warranty differences, local-only support)
```

## Rules

- Always state which exchange rate you used.
- Be explicit about whether the international price includes shipping to Israel and import VAT/duty. Most Amazon US prices don't — flag this when relevant.
- If the user gives an ex-VAT Israeli price, normalise to inc-VAT before comparing.
