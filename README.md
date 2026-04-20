# Israel-Skills

Israel-specific Claude Code agent skills and commands — Hebrew, Israeli services, local retail, and regional utilities.

## Commands

Retail & shopping (migrated from the `shopping` plugin):

- `israel-search-zap` — query zap.co.il, the canonical Israeli price-comparison aggregator
- `israel-search-google-il` — `site:.il` / Hebrew-keyword Google discovery
- `israel-search-main-tech-stores` — KSP, Ivory, Bug, TMS
- `israel-search-major-retailers` — Ace, Home Center, Office Depot, Audioline
- `israel-search-by-category` — dispatch to stores matching a category slug from the store DB
- `israel-discover-hebrew-term` — reverse-lookup the canonical Hebrew noun for a product class
- `israel-compare-to-international` — compare an Israeli price against international RRP
- `israel-convert-currency` — ILS ↔ USD/EUR/GBP conversion
- `israel-market-check` — quick IL vs international RRP sanity check
- `israel-source` — apply the Israeli sourcing waterfall (tier-1 tech → major retailers → Zap)
- `israel-add-store` — append a vendor to the Israeli store database with auto-dedup

## Skills

_To be added._

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-skills@danielrosehill
```

## License

MIT
