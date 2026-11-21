---
name: find-product
description: Find where to buy a product in Israel, and at what price, by running every channel this plugin has instead of one search. Pins down the exact product, then fans out in parallel to Zap (all vendors, warranty, importer), the trusted vendors for the product's category (e.g. KSP/Ivory/TMS then Plonter/Bug for computer parts; KZPro/Speed of Sound/Halilit/Kley Zemer for microphones), a .co.il-restricted web search, branch stock at KSP and Ivory, and import options (Amazon delivered to Israel, AliExpress) with landed cost; returns one ranked table with delivery (ships from, how long, options, cost) and a verdict. Prices in ILS including VAT by default; in USD and/or excluding VAT on request or for business buyers. Use for "find me X", "where can I buy X in Israel", "cheapest X", "who sells X", "is X available here", "source X", or any Israeli purchase question where the user has not limited the search to one store.
---

# Find a product in Israel (orchestrator)

The default entry point for an Israeli shopping question. Do not stop at the first source that answers: the point is to run every relevant channel, proactively, and report them side by side. The individual commands and skills (`/search-zap`, `/tech-product-search`, `ksp-branch-stock`, …) are the building blocks; this skill decides which to run and merges their results.

Paths below are relative to the plugin root. Strategy detail (Hebrew terms, URL patterns, VAT rules) is in `docs/search-strategies.md`.

## 0. Pin down the product (always)

1. Identify the exact item: brand, model, part number, variant (colour, capacity, region). If the user gave a vague description, a photo or a link, resolve it first (`/whats-this-brand`, `/pn-check`, or a quick web search) and state the resolved model in the first line.
2. If several models fit and the choice changes the answer, list the top 2–3 and ask before fanning out.
3. Build the Hebrew query: `<Hebrew category noun> <Latin brand> <Latin model>` (see strategies doc § Hebrew-term resolution). Keep a model-only variant (`<brand> <model>`) for retailers that choke on the noun.
4. Classify into a category from `data/trusted-vendors.json` → `categories` (e.g. `computer_parts`, `consumer_tech`, `microphones_audio`, `microphones_headsets`, `musical_instruments`). If none fits, use the Israel-Online-Stores roster (step 1C) to find specialists by category.

## 1. Fan out (in parallel)

Run these at the same time: independent tool calls in one message, or parallel subagents (model sonnet/haiku) for the slow ones. Each channel that fails is recorded with the route tried, never silently dropped.

### A. Zap (aggregator, always)

```
python3 scripts/zap.py search "<hebrew query>"        # cards: model pages + single listings
python3 scripts/zap.py model <modelid>                 # every vendor: price, shipping, days, warranty, official importer
```

Plain HTTP from an Israeli residential IP; Zap rejects headless browsers. Pick the card that matches the exact model (not accessories that mention it). Zap prices can lag a day: confirm the top 2–3 on the vendor page.

### B. Trusted vendors for the category

Load `data/trusted-vendors.json`, merged with the user's `<plugin-data-dir>/trusted-vendors.json` if present (same `id` replaces). Search every **wave 1** vendor for the category. Search **wave 2** too when wave 1 has fewer than two hits, the item is niche, or the user asked for breadth.

Per vendor, use its `route`:
- `script` → the command in `how` (KSP, Ivory: also returns branch stock).
- `curl` → GET `search_url` with `{q}` URL-encoded and a desktop Chrome User-Agent; grep the model string and price near it.
- `browser` → the agent browser (or Claude in Chrome): open the site, use its search box, read the result cards.

Report vendors the user trusts even when Zap already lists them: their own site may be cheaper, show stock, or carry the item when Zap does not.

### C. Wider Israeli web (.co.il)

- Web search `"<brand> <model>" site:co.il` and `"<brand> <model>" מחיר`; drop news, blogs and review sites.
- When web search is thin or blocked, escalate to Exa (`exa__web_search_exa`, describe the page: "Israeli online store product page selling <model>").
- For specialists, `python3 scripts/stores.py --category <tag>` (5,590-store roster from Zap, specialists ranked first; see strategies doc § Store roster) and search the top matches.
- Any retailer found here that is not in the roster or the trusted list: mention it as a candidate for `/add-store`.

### D. Import options (run unless the user said local only)

- **Amazon delivered to Israel:** use the `amazon` plugin (`amazon-listing-check` / `amazon-search`) with the delivery location set to Israel, or the curl recipe in `docs/search-strategies.md` § Amazon. Record item, AmazonGlobal shipping, estimated import charges, total, or "cannot be shipped to Israel".
- **AliExpress:** prefer the `aliexpress-israel-skills` plugin (deep search with true SKU prices, landed cost, the $75 de-minimis). If it is not installed, search `he.aliexpress.com` in a real browser and compute landed cost by hand (item + shipping to IL; 18% VAT above $75). Only for unbranded items or when the user accepts AliExpress.
- Landed cost for either: run the `israel-import-tax` skill (USD 75 exemption, VAT, duty and purchase tax by HS code) rather than a rule of thumb, and compare against the Israeli best price with `/rrp-check` logic.

### E. Stock and pickup (when the user wants it today or names a place)

`ksp-branch-stock` and `ivory-branch-stock` on the shortlisted items, for the user's home branches.

## 2. Price basis: currency and VAT

Decide once, state it in the header line, apply it to every row.

- **Default: ILS (₪), VAT included** — what a private buyer pays.
- **USD on request** ("in dollars", "$"): convert every figure at one live rate, fetched once per run (`fx__latest_rates` on the gateway if available, else `/convert-currency`'s API), and print the rate and its date in the header. Keep the ILS figure in a second column unless the user asked for USD only.
- **Excluding VAT for business buyers** ("for the business", "ex VAT", "לפני מע"מ", "I can reclaim VAT", an Osek Murshe / company purchase): show `price / 1.18` as the main figure, labelled "ex VAT", and keep the inc-VAT figure alongside. Shipping is ex-VAT too. Import options: VAT paid at customs is also reclaimable, so compare ex-VAT on both sides.
- Combine freely: "USD ex VAT" is a valid basis.
- Standing preference: read `<plugin-data-dir>/preferences.json` if present, e.g. `{"currency": "ILS", "vat": "inc", "buyer": "consumer"}` or `{"currency": "USD", "vat": "ex", "buyer": "business"}`. An explicit request in the conversation overrides it.
- Normalise sources first: Zap and Israeli retailers quote inc VAT (Eilat and some B2B rows are ex VAT: add 18% before converting); Amazon quotes USD with import charges separate; AliExpress quotes in the locale currency.

## 3. Delivery: where from, how long, which options

For every row on the shortlist (at least the top 5), fill in:

- **Ships from** — Israel (city or warehouse if known: roster `city_he` / the vendor page) or abroad (country; Amazon US/UK/DE, AliExpress CN/TR/IL warehouse).
- **Delivery time** — Zap's `delivery_business_days_max` ("up to N business days"), the vendor page's stated time, or the import estimate (AliExpress 1–6 weeks, AmazonGlobal date range). Say "same day / tomorrow" when branch stock makes pickup possible.
- **Delivery options and cost** — courier to the door, pickup point (נקודת איסוף), store pickup (איסוף עצמי, with which branches have it in stock), Israel Post; cost of each where shown, "free" when free. Zap gives one shipping price and time; read the vendor page for the top 3 to get the full option list.
- **Total** = item + cheapest delivery option the user would actually use (door delivery unless they said pickup).

## 4. Merge and report

One table, ranked by **total delivered price on the chosen price basis**:

```
## <exact product> — where to buy (checked <date>)
Hebrew query: <query>   Category: <category>

Prices: ₪ inc VAT   (or: USD ex VAT @ 1 USD = 3.xx ILS, <rate date>)

| # | Total | Item | Delivery | Vendor | Ships from | Delivery time | Delivery options | Stock | Warranty | Link |
|---|---|---|---|---|---|---|---|---|---|---|

Channels run: Zap ✓ (N vendors) · Trusted: KSP ✓, Ivory ✓, TMS ✗ (no hit), Plonter — (browser, skipped: …) · .co.il ✓ · Amazon→IL ✓ · AliExpress — (not relevant)
```

Then a short verdict: best local price, best trusted-vendor price, best import option and whether it beats local after VAT, and any warranty difference (official importer vs parallel import matters for electronics).

## Rules

- Never invent a price or stock state. A channel with no extractable price says so.
- Never substitute a similar model silently; flag near-matches as such.
- Quote KSP's regular price, not the Eilat price. Normalise ex-VAT source prices by adding 18% before applying the chosen basis.
- Never mix bases in one table: every number is in the stated currency and VAT mode.
- Prefer the official-importer offer when prices are within ~5% and the user has not said otherwise.
- The user's trusted vendors are always searched for their categories, whether or not Zap lists them.
- Record the date: Israeli prices move weekly.
