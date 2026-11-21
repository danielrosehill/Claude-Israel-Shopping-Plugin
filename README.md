![banner](banner.png)

# Israel-Shopping

Israeli shopping workflows for Claude Code — tech retailers, Zap price comparison, Hebrew term resolution, ILS conversion, and RRP/market checks.

> Renamed from `Israel-Skills` on 2026-04-20. The scope was always shopping; the new name reflects it. Non-shopping Israel utilities will live in a separate plugin.

## Start here: `find-product`

The `find-product` skill is the default entry point for "find me X" / "where can I buy X in Israel". It pins down the exact model, then runs every channel in parallel and returns one table ranked by delivered price:

- **Zap** — `scripts/zap.py` pulls every vendor on a Zap model page (price, shipping, delivery days, rating, official importer, warranty) over plain HTTP.
- **Trusted vendors per category** — [`data/trusted-vendors.json`](data/trusted-vendors.json), searched in waves. Defaults: computer parts → KSP, Ivory, TMS, then Plonter, Bug; microphones and audio → KZPro, Speed of Sound, Halilit, Kley Zemer, then Sound Check, HeadSound, La-Bama, KSP, Ivory; microphones and recording headsets → Speed of Sound, Sound Check, HeadSound, KZPro, then Halilit, Kley Zemer, La-Bama, Shalmon, Kol HaMusica, Next Pro, Diaz (via Zap), Bug, KSP. Each vendor carries its verified search URL and route. Add your own in `<plugin-data-dir>/trusted-vendors.json`.
- **.co.il web search** for retailers neither Zap nor the trusted list covers.
- **Import options** — Amazon delivered to Israel and AliExpress, with landed cost against the local best price.
- **Store reputation** — skill `store-reputation`: Zap store-card counts (`skills/store-reputation/scripts/zap_reputation.py <siteid>`) plus the Google Maps rating, combined into one verdict.
- **Branch stock** at KSP and Ivory when you want to pick it up.

Every result row shows **where it ships from, how long delivery takes, the delivery options** (courier, pickup point, store pickup, Israel Post) and their cost. Prices default to **₪ including VAT**; ask for **dollars** and/or **excluding VAT** (business buyers who reclaim VAT) and the whole table switches basis, with the exchange rate and date stated. A standing default can go in `<plugin-data-dir>/preferences.json`, e.g. `{"currency": "USD", "vat": "ex", "buyer": "business"}`.

## Skill: import tax

- `israel-import-tax` — landed cost of a personal import: USD 75 exemption, VAT, duty and purchase tax by HS code, FTA origin proof, approvals, refunds, plus a stdlib `landed_cost.py`. Called from `find-product`, `compare-to-local` and `/rrp-check`; rules dated and pointed at the live Tax Authority calculator.

## Commands (slash)

- `/tech-product-search` — search tier-1 IL tech retailers (Ivory, KSP, Bug, TMS) with Hebrew-term resolution; bundled KSP/Ivory scripts, curl, and a real browser only for bot-walled sites.
- `/general-search` — broader Israeli retail search (Ace, Home Center, Office Depot, Audioline, Google IL, Zap).
- `/search-zap` — query zap.co.il, the canonical Israeli price-comparison aggregator.
- `/rrp-check` — compare an Israeli price against international RRP / market pricing.
- `/convert-currency` — ILS ↔ USD/EUR/GBP conversion.
- `/pn-check` — given an IL product listing, find the canonical manufacturer part-number on the international market.
- `/store-zap-lookup` — given a retailer name, find its Zap profile URL, rating, and review count.
- `/whats-this-brand` — identify an obscure Israeli-market brand (white-label, importer-specific, OEM equivalent).
- `/freier-check` — playful "are you a freier" verdict given an IL price and international RRP.
- `/add-store` — append a vendor to the user's persistent store overlay (survives plugin updates).

## Skills: branch stock

- `ksp-branch-stock` — is it in stock at a given KSP branch? Search, URL, item id or מק"ט in; price, in-stock and last-unit flags per branch out. Stdlib Python, with a browser fallback for when KSP's bot filter kicks in.
- `ivory-branch-stock` — the same for Ivory, from the data behind its "הצג זמינות מלאי בסניפים" popup.

Both default to your home branches from `<plugin-data-dir>/home-branches.json`, e.g. `{"ksp": ["57"], "ivory": ["24"]}`. Endpoint notes and traps: [`docs/search-strategies.md`](docs/search-strategies.md) § Per-branch stock.

AliExpress lives in the companion plugin [`aliexpress-israel-skills`](https://github.com/danielrosehill/Aliexpress-Israel-Skills) (search, true prices, landed cost, $75 de-minimis, Israeli reviews, cart). This plugin keeps `compare-to-local` (is an AliExpress item sold in Israel, and for how much) and calls the companion from `find-product`.

## History

- 2026-11-20: `find-product`, trusted vendors and `scripts/zap.py` added. The AliExpress skills (`search-aliexpress`, `fetch-listing`, `fetch-listing-api`, `free-shipping-only`, `il-reviews-show`, `exclude-combo-deals`) and the `research/` notes moved to `aliexpress-israel-skills`.

Strategy and know-how (Hebrew terms, verified URL patterns and routes per retailer, trusted vendors, Amazon-to-Israel, sourcing waterfall, store roster) live in [`docs/search-strategies.md`](docs/search-strategies.md). The commands reference it rather than restating.

## Data

Store roster: [`danielrosehill/Israel-Online-Stores`](https://github.com/danielrosehill/Israel-Online-Stores), 5,590 Israeli stores from Zap's store directory (refreshed 2026-11-20) with Zap profile links and product categories (80% tagged). Query it with `python3 scripts/stores.py --category <tag>` / `--find <name>`. Your own additions go in `<plugin-data-dir>/user-stores.json` (`/add-store`) and survive plugin updates.

# Sources

None are bundled yet — see [`INTEGRATIONS.md`](INTEGRATIONS.md) for status. These tables credit the upstream projects considered as roadmap dependencies.

## Consumer rights / legal

| Project | Description |
| --- | --- |
| [`Ansvar-Systems/israel-law-mcp`](https://github.com/Ansvar-Systems/israel-law-mcp) | Hosted MCP exposing Israeli statutes; check Consumer Protection Law coverage. |

## Currency / FX

| Project | Description |
| --- | --- |
| **TODO** | No candidate yet. Needs a mid-market-rate FX MCP (exchangerate.host, Frankfurter, open.er-api.com) for reproducible cross-border comparisons. |

## Domestic retailers & price comparison

| Project | Description |
| --- | --- |
| [`danielrosehill/Israeli-Tech-Shopping-MCP`](https://github.com/danielrosehill/Israeli-Tech-Shopping-MCP) | Own project: browser-automation comparison across IL tech retailers. |
| [`guymon92/ksp-mcp`](https://github.com/guymon92/ksp-mcp) | KSP.co.il MCP. |
| [`Simtob-Eran/mcp-israeli-price-comparison`](https://github.com/Simtob-Eran/mcp-israeli-price-comparison) | Generic IL price-comparison MCP. |
| [`TalKleinBgu/Zap`](https://github.com/TalKleinBgu/Zap) | Zap.co.il product dedup / normalization pipeline. |

## Grocery

| Project | Description |
| --- | --- |
| [`aloncarmel/supermeskill`](https://github.com/aloncarmel/supermeskill) | SuperMe skill. |
| [`asafr93-rosa/shopping-list-il`](https://github.com/asafr93-rosa/shopping-list-il) | Shopping-list tool. |
| [`danielJL-altius/israelgrocerymcp`](https://github.com/danielJL-altius/israelgrocerymcp) | Alt grocery MCP. |
| [`matipojo/shufersal-mcp`](https://github.com/matipojo/shufersal-mcp) | Shufersal MCP. |
| [`OpenIsraeliSupermarkets/israeli-supermarket-scarpers`](https://github.com/OpenIsraeliSupermarkets/israeli-supermarket-scarpers) | Python scraper library (Shufersal, Rami Levy, Victory, etc.). |

## International / cross-border

| Project | Description |
| --- | --- |
| Amazon | **TODO** — no candidate yet that handles ships-to-IL eligibility. |
| [`justinritchie/aliexpress-mcp-server`](https://github.com/justinritchie/aliexpress-mcp-server) | AliExpress MCP for cross-border lookups. |
| Newegg | **TODO** — no candidate yet. |
| [`rootsbymenda/iherbchecker`](https://github.com/rootsbymenda/iherbchecker) | iHerb availability/price check. |

## Pharmacy

| Project | Description |
| --- | --- |
| [`alexpolonsky/agent-skill-maccabi-pharm-search`](https://github.com/alexpolonsky/agent-skill-maccabi-pharm-search) | Maccabi pharmacy search. |
| [`skills-il/health-services`](https://github.com/skills-il/health-services) | Broader health services (lift pharmacy sub-skills). |
| [`tomron/agent-skill-clalit-pharm-search`](https://github.com/tomron/agent-skill-clalit-pharm-search) | Clalit pharmacy search. |

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-shopping@danielrosehill
```

## License

MIT
