---
name: store-zap-lookup
description: Given an Israeli retailer name (Hebrew or English), find its Zap.co.il profile URL and retrieve the seller rating and review count. Useful for vetting an unfamiliar retailer before buying.
---

# Store Zap Lookup

Resolve an Israeli retailer to its Zap seller profile and pull the rating.

## When to use

- User found a low price on an unfamiliar retailer and wants to check reputation.
- Comparing retailers on Zap and wants the rating surfaced alongside price.
- Adding a new store via `/add-store` and wants to record the Zap profile.

## Backend

curl / WebFetch with a desktop Chrome UA from an Israeli IP (Zap rejects headless browsers). Profile URL: `https://www.zap.co.il/clientcard.aspx?siteid=<siteid>`; the siteid is in the store roster (`zap.siteid`) and in every Zap offer row.

## Workflow

1. **Look the retailer up in the roster:** `python3 scripts/stores.py --find "<name or domain>"` returns its `zap_url` when it is on Zap (5,584 stores are).
2. **If known,** navigate directly to the profile URL (`https://www.zap.co.il/clientcard.aspx?siteid=<id>`).
3. **If unknown,** search Zap for the retailer:
   - Navigate `https://www.zap.co.il/` and use the shop search, OR
   - Google `site:zap.co.il "<retailer name>"` and look for a `clientcard.aspx?siteid=<id>` URL.
4. **On the profile page, extract:**
   - Seller rating (usually out of 5 or as a percentage)
   - Review count
   - Years active on Zap (if shown)
   - Any flags (verified seller, "Zap recommended", etc.)

## Output

```
## {retailer} — Zap profile

- **Zap URL:** {url}
- **Rating:** {rating} ({review_count} reviews)
- **Years on Zap:** {years or "not shown"}
- **Flags:** {verified / recommended / none}

### Notes
- {anything unusual — low rating, recent negative reviews, no Zap presence}
```

If the retailer has no Zap profile at all, say so — it's a soft signal about smaller or very new shops. Don't invent a rating.

## Rules

- Never fabricate a rating. If the page didn't load or the rating wasn't visible, say so.
- Cross-check the profile matches the retailer (Zap has some duplicate / similarly-named profiles).
