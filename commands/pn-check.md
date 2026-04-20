---
name: pn-check
description: Given an Israeli product listing, find what manufacturer part-number (PN) / SKU it corresponds to on the international market. Useful because Israeli retailers often relabel consumables (toner cartridges, filters, replacement parts) with odd local PNs that don't match the manufacturer's global catalog.
---

# PN Check

Cross-reference an Israeli product listing against the manufacturer's global catalog to find the canonical international part-number.

## When to use

- IL listing has an unfamiliar PN that doesn't match global search results (common for toner, filters, replacement parts, accessories).
- User wants to confirm they're comparing like-for-like against Amazon / B&H / AliExpress.
- User wants to buy the consumable abroad but needs the international PN.

## Workflow

1. **Extract** from the IL listing:
   - Brand
   - Model (the parent device, if relevant — e.g. "for HP LaserJet M404")
   - Any visible PN / SKU (IL-local)
   - Product photos (for visual match if PN doesn't resolve)
2. **Cross-reference** in this order:
   - **Manufacturer global site** — authoritative source for canonical PNs.
   - **Amazon US** — search by brand + description; check "Product details" for PN.
   - **B&H** — strong for imaging, audio, computing consumables.
   - **AliExpress** — compatible/OEM equivalents; flag if it's a compatible rather than genuine.
3. **Confirm the match** — visual (product photo), spec (capacity, yield, dimensions), and the device-compatibility list must all agree. Don't match on PN alone if the IL PN looks relabelled.
4. If the IL PN is an **importer-specific relabel**, note it.

## Output

```
## PN check — {brand} {product}

| Field | IL listing | International |
|---|---|---|
| PN / SKU | {il_pn} | {intl_pn} |
| Listing URL | {il_url} | {intl_url} |
| Source | {il_retailer} | {manufacturer / Amazon / B&H / AliExpress} |

**Mapping confidence:** {confident | tentative | unknown}
**Notes:** {any relabel / importer-specific info / genuine-vs-compatible flag}
```

## Rules

- If the IL PN can't be matched to any international PN, say so — don't guess.
- Flag clearly when the international equivalent is a **compatible** (third-party) rather than the genuine manufacturer part.
- For consumables, confirm capacity / yield / compatibility list matches before declaring equivalence.
