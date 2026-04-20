---
description: Apply the Israeli sourcing waterfall (tier-1 tech -> tier-2 broad -> niche specialists -> Amazon-IL -> AliExpress) for each shortlisted candidate.
---

# Source — Apply the Israeli Sourcing Waterfall

Apply the Israeli sourcing waterfall to the shortlisted candidates. For each CONSIDER candidate from `from-ai/shortlist.md`, find where it's available and at what **landed cost** (price + VAT + shipping + customs).

This is the fourth phase: `/intake` -> `/shortlist` -> **`/israel-source`** -> `/recommend`.

## Pre-source checklist

1. **Read `spec.md`** + the Standing preferences snapshot
2. **Read `from-ai/shortlist.md`** — must exist, must have at least one CONSIDER candidate
3. If no shortlist exists, stop and suggest `/shortlist`

## Inputs

- **CONSIDER candidates** from `shortlist.md`
- **Spec sourcing overrides** (e.g. "AliExpress off this time", "Domestic only — urgent")
- **Standing channel preferences** from the snapshot:
  - AliExpress tolerance
  - Amazon-IL tolerance
  - Parallel imports / grey market
  - Preferred / avoided Israeli stores

Per-purchase overrides beat standing defaults.

## The waterfall

For each CONSIDER candidate, evaluate channels in this order:

### 1. Israeli domestic tier-1 tech

Consumer tech — use `/shopping:israel-search-main-tech-stores` (KSP, Ivory, Bug, TMS).

Capture per store hit:
- Store name + URL
- Price in ILS (confirm VAT-included; add 18% if ex-VAT)
- Stock status
- Warranty terms
- **KSP note**: use the **higher (regular, non-Eilat)** price

### 2. Israeli domestic tier-2 broad

Appliances, office gear, audio, hardware — use `/shopping:israel-search-major-retailers` (Ace, Home Center, Office Depot, Audioline).

### 3. Niche Israeli specialists

Tactical, lighting, photography, gaming, smart home — use `/shopping:israel-search-by-category`.

### 4. Amazon (international)

Proceed only if domestic isn't found OR domestic exceeds the effective markup threshold AND spec hasn't disabled Amazon.

- **Verify shippable to Israel** — check for "this item cannot be shipped to your selected delivery location". If not shippable → mark **Not Available** and skip.
- Capture: USD price, shipping to IL, estimated VAT (18%) and possible customs duty (imports over $75 USD de minimis)
- Compute **landed total in ILS**

### 5. AliExpress

Proceed only if the spec / standing preferences allow AliExpress for this category. Branded items: only if seller rating >=95%.

Capture USD price + shipping, seller rating, lead time (typically 2-6 weeks to IL), landed total in ILS.

### 6. Manufacturer direct / B&H / specialist international

Last resort.

## Best channel per candidate

Pick based on landed cost, lead time vs spec tolerance, warranty, channel viability.

## Output: `from-ai/sourcing.md`

Structured per-candidate waterfall detail plus a summary (candidates sourced, sourcing-disqualified count, channel mix, cheapest landed, shortest lead time). Then prompt: "Sourcing saved. Run `/recommend` to generate the PDF report."
