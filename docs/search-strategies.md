# Israeli Shopping — Search Strategies

Agent-facing reference for the substantive know-how behind the plugin's search commands. The commands (`/tech-product-search`, `/general-search`, `/search-zap`, etc.) point here rather than restating the strategy. Read the section relevant to the task at hand.

## Store-metadata merge convention

All commands that consume the Israeli store list must **merge** two sources:

1. **Upstream canonical list** — `https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json` (live, 800+ entries). Read this first.
2. **User overlay** — `<plugin-data-dir>/user-stores.json` (optional). The plugin data directory resolves as `$CLAUDE_USER_DATA/israel-shopping/` if `CLAUDE_USER_DATA` is set; otherwise `$XDG_DATA_HOME/claude-plugins/israel-shopping/` if `XDG_DATA_HOME` is set; otherwise `~/.local/share/claude-plugins/israel-shopping/`. See the canonical convention in the `meta-tools:plugin-data-storage` skill. If present, merge/append on top of the upstream list. Dedup by canonical URL / domain — user entries win on conflict.

Do not write user additions back into the plugin install directory — those get clobbered on plugin update. Only `<plugin-data-dir>/user-stores.json` persists across updates.

Schema matches the upstream `stores.json` shape (name, url, categories[], is_tech, description, delivery, eilat_door, zap_profile, etc. — read a live entry to confirm the current shape before writing).

---

## Hebrew-term resolution (mandatory preflight)

Israeli retailer and aggregator search returns nothing useful with English category nouns. Every query must be built as:

```
<Hebrew category noun>  <brand in Latin>  <model in Latin>
```

Examples:
- Anker Prime A2343 charging tower → `עמדת טעינה Anker Prime A2343`
- Logitech MX Master 3S mouse → `עכבר Logitech MX Master 3S`
- LG C4 55" OLED TV → `טלוויזיה LG C4 55`

**Brand and model stay Latin** — retailers index SKUs in Latin. Only the category noun is translated.

### If you don't know the Hebrew noun

1. Check the user's vocabulary — if they used a Hebrew word, use it.
2. Otherwise translate the category noun. Common mappings:
   - mouse → `עכבר`
   - charger → `מטען`
   - cable → `כבל`
   - monitor → `מסך`
   - headphones → `אוזניות`
   - laptop → `מחשב נייד`
   - keyboard → `מקלדת`
   - TV → `טלוויזיה`
   - headlamp → `פנס ראש`
   - rechargeable battery → `סוללות נטענות`
   - charging dock/station → `עמדת טעינה` / `תחנת טעינה` / `מטען שולחני`
3. Have 1–2 Hebrew synonyms ready as fallback.

### Reverse-lookup when the term is unknown

If translation gives weak results, derive the canonical term from a real IL listing:

1. Google `"<brand model>" site:.il` for a known SKU in the class.
2. Open the top 2–3 retail results (skip news/blog domains — ynet, walla, haaretz, calcalist, themarker, geektime).
3. Extract the Hebrew noun from, in order of cleanness:
   - **URL slug** — percent-decode and read the Hebrew noun.
   - **`<title>` tag** — usually starts with the Hebrew product class noun.
   - **Breadcrumb nav** — `.breadcrumb`, `nav[aria-label*="breadcrumb"]`, schema.org breadcrumb markup.
4. Normalise to **singular**. Strip plural `ות`/`ים` unless the category is inherently plural in retail use.
5. If different retailers use different terms, record all variants — common for chargers (`עמדת טעינה` vs `מטען שולחני` vs `תחנת טעינה`).
6. Note exclude terms — e.g. `סוללה ניידת` (power bank) must be excluded when searching for `סוללות נטענות` (rechargeable batteries).

Never trust Google Translate alone for retail jargon. Never invent a Hebrew term — if no IL listing exists for any SKU in the class, ask the user.

---

## Tier-1 Israeli tech retailers — Ivory / KSP / Bug / TMS

The four mainstream tech chains. Used by `/tech-product-search`.

| Retailer | Search URL pattern | Backend notes |
|---|---|---|
| Ivory | `https://www.ivory.co.il/catalog.php?act=cat&q=<URL-encoded Hebrew>` | curl / WebFetch, or `skills/ivory-branch-stock/scripts/ivory_stock.py "<q>" --all` (adds branch stock). |
| KSP | `https://ksp.co.il/web/cat/?search=<URL-encoded Hebrew>` | The HTML site returns 403 to every automated route (curl, headless, residential IP). Use `skills/ksp-branch-stock/scripts/ksp_stock.py "<q>" --all`, which calls KSP's JSON API with browser Sec-Fetch headers. Two prices (regular + Eilat); always quote the **regular** (higher) price unless the user specifies Eilat pickup. |
| Bug | `https://www.bug.co.il/search?q=<URL-encoded Hebrew>` | curl with a desktop Chrome UA works (verified 2026-11-20); page is ~1.3 MB, grep the model. |
| TMS | `https://tms.co.il/index.php?route=product/search&search=<URL-encoded Hebrew>` | curl / WebFetch. |

Verified 2026-11-20 with `מיקרופון Shure SM7B`. Trusted vendors beyond these four, with their verified routes and per-category search waves, are in `data/trusted-vendors.json` (see § Trusted vendors).

**URL-encode the Hebrew query.** Example: `מחשב` → `%D7%9E%D7%97%D7%A9%D7%91`. Don't paste raw Hebrew into the URL.

Treat the URL patterns as last-known-good hints, not contracts. If a documented pattern returns a homepage redirect or 404, fall back to the real-browser homepage-form flow and note it in the output.

### Backend chain (per retailer)

Try in order; note the backend used in the output. Verified routes as of 2026-11-20:

1. **Bundled script** where one exists (KSP, Ivory, Zap: `scripts/zap.py`).
2. **curl / WebFetch** of the retailer's search URL with a desktop Chrome User-Agent. From this kind of setup both egress on the user's Israeli IP, which most Israeli retailers require. Check you got real results, not a homepage or a bot-challenge page (Incapsula, Cloudflare, "Request Rejected").
3. **Real browser** (the agent browser, else Claude in Chrome, else Playwright) for sites behind a JS bot wall (Plonter: Incapsula) or with no URL-addressable search. Headless Playwright is fingerprinted by Zap and KSP; do not use it for those.
4. **Web search** `"<brand model>" site:<domain>`, escalating to Exa (`exa__web_search_exa`) when plain web search is thin. Tavily is no longer the escalation route (keyless tier, hourly cap).

If every route fails for a retailer, record "blocked: <routes tried>" and continue; don't fail the whole run.

### KSP regular-vs-Eilat price rule

KSP lists two prices: regular and Eilat (tax-exempt). Always quote the **regular (higher)** price unless the user explicitly asked about Eilat pickup. If both appear, show the regular price in the table and note the Eilat price in a comment.

### Per-branch stock: KSP and Ivory endpoints

Used by the `ksp-branch-stock` and `ivory-branch-stock` skills. Reverse-engineered from each site's own "stock in branches" popup on 2026-10-26; neither is a documented API.

| Retailer | Search | Stock by branch | Access |
|---|---|---|---|
| KSP | `GET https://ksp.co.il/m_action/api/category/?search=<q>` → `result.items[]` with `uin` (URL id), `uinsql` (catalogue number, מק"ט), `name`, `price`, `eilatPrice`, `pickupDeliveryBranches[]` | `GET https://ksp.co.il/m_action/api/mlay/<uinsql>` → `result.stores{<key>: {id, name, region, qnt, isLastItem}}`, 75 branches | Plain HTTP passes only with `Sec-Fetch-Site: same-origin` + `Sec-Fetch-Mode: cors` and a current Chrome UA; without them, 403. Search and `/item/<uin>` start returning 403 after ~100 rapid calls (Cloudflare challenge); `mlay` kept answering. Fallback: `fetch()` from inside a ksp.co.il page in a real browser. |
| Ivory | `GET https://www.ivory.co.il/catalog.php?act=cat&q=<q>` (HTML; cards split on `catalogVertical_item`, id in `data-product-id`, price in `מחיר רגיל: N`) | `GET https://www.ivory.co.il/catalog-items/ws/check_balance/<id>` → `{Status, Data[{branch_code, branchName, address, isAvailable, notAvailable}]}`, 45 branches incl. warehouse `690` and external stock `19` | Plain HTTP, no special headers. |

Traps:

- **KSP `mlay` takes `uinsql`, not the URL id.** Passing the URL id (e.g. 410052 instead of 372624) returns a well-formed response with every branch at `qnt: 0`. That looks like "sold out everywhere" and is wrong. `/m_action/api/item/<uin>` gives the `uinsql`.
- **KSP `qnt` is a 0/1 flag, not a unit count.** `isLastItem: true` marks the last unit. `pickupDeliveryBranches` in search results lists exactly the branches with `qnt > 0` (checked on 10 items), so search alone answers in/out-of-stock.
- **Ivory `notAvailable: 1`** renders as the orange "i" (orderable to the branch) or grey cross; only `isAvailable: 1` (green tick) means on the shelf. Checked against the popup for product 160813.
- Branch tables: `skills/ksp-branch-stock/references/ksp-branches.md`, `skills/ivory-branch-stock/references/ivory-branches.md`.

### Fallback when a retailer returns nothing

1. Retry with a Hebrew synonym from the term-resolution list.
2. Retry with **brand + model only** (drop the Hebrew noun) — some retailer search engines reject the noun but accept the SKU.
3. Google `<brand model> site:<retailer-domain>` — Google's index of the retailer often beats the retailer's own search.

---

## Tier-2 major retailers — Ace / Home Center / Office Depot / Audioline

For products that lean household/office/audio rather than pure consumer tech. Used by `/general-search`.

| Retailer | Best for |
|---|---|
| Ace | Hardware, tools, garden, some electronics |
| Home Center | Home improvement, appliances, fixtures |
| Office Depot | Office supplies + tech accessories |
| Audioline | Audio equipment specialist |

Same backend chain as the tier-1 group (script → curl/WebFetch → real browser → web search). Same Hebrew preflight. Same fallback chain. Out-of-category misses are normal (e.g. searching Audioline for a vacuum) and not worth flagging unless every retailer missed.

---

## Zap — canonical price-comparison aggregator

Zap.co.il indexes prices across tier-1, tier-2, and many niche IL retailers. For most cross-retailer price-comparison queries, Zap is the fastest first pass — one query returns the ranked vendor table.

### Backend

`scripts/zap.py` — plain HTTPS GET with a desktop Chrome UA from an Israeli residential IP (verified 2026-11-20). Zap fingerprints headless browsers ("Request Rejected", since 2026-09) and blocks datacenter IPs, so Playwright and cloud fetchers fail; search-engine snapshots are stale and miss the vendor table.

```
python3 scripts/zap.py search "<hebrew query>"   # result cards: model pages (many vendors) + single listings
python3 scripts/zap.py model <modelid|url>        # every vendor row: price, shipping, delivery days, rating, official importer, warranty
```

Each vendor row on a model page is a `div.compare-item-row` carrying `data-site-name`, `data-site-id`, `data-product-price`, `data-ship-price`, `data-delivery-time`, `data-official-importer`, `data-warranty-company`, `data-warranty-months`. The featured offer is `section.BuyBox` with the same fields.

### URL patterns

- **Keyword search:** `https://www.zap.co.il/search.aspx?keyword=<encoded Hebrew query>`
- **Model page (vendor comparison table):** `https://www.zap.co.il/model.aspx?modelid=<id>` — this is what you actually want; it has all vendors side-by-side. `modelid` is visible in the search results.
- **Category browse:** `https://www.zap.co.il/models.aspx?sog=<category>` — fallback when keyword search is unhelpful.
- **Store profile (for retailer ratings):** `https://www.zap.co.il/clientcard.aspx?siteid=<siteid>` — used by `/store-zap-lookup`. The siteid is in every offer row (`data-site-id`).
- **Store directory (with category facets):** `https://www.zap.co.il/modelsstore.aspx?sog=g-stores` — the source of the Israel-Online-Stores roster.

### Workflow

1. Resolve Hebrew term (preflight).
2. Navigate to keyword search with the Hebrew query.
3. Find the right model — Zap groups by SKU. If unsure between multiple matches, list the top 3 and confirm with user.
4. Open the model page. Extract the vendor table: vendor name, ILS price (verify VAT-inclusive), delivery info, link.
5. Check for Eilat / ex-VAT badges on unusually low prices — use the regular price.
6. Rank low-to-high. Cap at 10 vendors unless asked.

### Caveats

- Zap's cached price can lag reality by 24+ hours — visit the vendor page before quoting.
- Zap sometimes lists ex-VAT prices without a clear badge — verify on the vendor page.
- Show Zap's own "Zap price" (recommendation) alongside the cheapest vendor — it reflects Zap's deal arrangements.

### When Zap misses

If keyword search returns no model page or the vendor table is empty:

1. Google IL discovery (below) — catches specialists Zap doesn't index.
2. Tier-1 tech retailer sweep (`/tech-product-search`).
3. Category-dispatched search against the merged store list.

Tell the user why Zap didn't work (new SKU, niche product, variant not indexed).

---

## Google IL discovery

Google often beats per-retailer search for discovery, for niche products, and as a Hebrew-term sanity check. Used within `/general-search` and whenever retailer-specific searches return nothing.

### Backend

The built-in web search tool first (it honours `site:`), then Exa when results are thin. Google Shopping itself needs a real browser (it blocks scrapers); navigate `https://www.google.com/search` with the params below.

Locale params:
- `gl=il` — geolocation Israel (prices in ILS, IL retailers ranked first)
- `hl=he` — Hebrew interface (Hebrew-only pages surface)
- `tbm=shop` — Google Shopping vertical

### Query patterns

Try in this order; don't run more than 3–4 per session (Google rate-limits).

1. **`"<brand model>" site:.il`** — best for known-SKU lookups, Hebrew-term reverse-lookup, finding any IL retailer carrying the product. Quote the model number to stop Google relaxing it.
2. **`"<brand model>" site:co.il`** — narrower, commercial-only (skips `.org.il`, `.ac.il`, `gov.il`). Use when (1) is too noisy.
3. **`מחיר <hebrew term> <brand>`** — the word `מחיר` ("price") is a strong commercial-intent signal. Good when you have a category but not a specific model.
4. **`קנה <hebrew term>`** — similar but noisier; fallback.
5. **`<hebrew term> בארץ` / `ישראל`** — when Google returns too many international results and `site:.il` over-filters.
6. **Google Shopping IL** — `https://www.google.com/search?tbm=shop&gl=il&hl=he&q=<hebrew query>`. Patchy coverage but fast price-ranked cross-check.

### Extract + filter

For each result: domain, page title, visible price (if in snippet). Drop:
- News sites (ynet, walla, calcalist, haaretz, themarker, geektime).
- Blogs/reviews unless the user asked for them.
- Dead or parked domains.
- Duplicate domains — keep the best-ranked per domain.

Group by domain, surface the top 3–5 retailers. Flag any retailer not already in the merged store list — candidate for user to add via `/add-store`.

---

## Category-dispatched search

When the query lies outside the mainstream tier-1 and tier-2 chains — e.g. tactical gear, specialist audio, photography accessories — filter the merged store list by category and search the matching stores directly.

### Vocabulary

`computers`, `mobile`, `peripherals`, `appliances`, `photography`, `audio`, `tv_av`, `gaming`, `office`, `lighting`, `tactical`, `power_battery`, `smart_home`, `security`, `tools`, `spare_parts`, `accessories`.

### Workflow

1. Map the user's request to one or more categories. Examples: "headlamps" → `lighting` + `tactical`; "DSLR bag" → `photography` + `accessories`; "UPS" → `power_battery`.
2. Filter the merged store list: `is_tech != false` AND any category in `store.categories[]` matches.
3. Pick up to 8 stores. Prioritise `is_tech: true` over `null`, then stores whose description mentions the specific product type, then stores with multiple matching categories.
4. Resolve Hebrew terms.
5. Search each store. Try in order:
   - Real browser: homepage, locate search form (`input[type=search]`, `input[name=q]`, `input[name=s]`, `#search`, `#qSearch`), submit Hebrew query.
   - URL-pattern probes: `/?s={q}` (WordPress), `/search?q={q}`, `/catalogsearch/result/?q={q}` (Magento).
   - Web search / Exa: `site:{domain} <hebrew query>`.
6. Try alternate Hebrew variants if primary returns nothing.
7. Rank low-to-high. Cap at 3 results per store.

Only navigate to stores where `is_tech` is `true` or `null`. Never `false`.

---

## Trusted vendors (per category, in waves)

`data/trusted-vendors.json` lists the vendors the user always wants searched for a category, with each vendor's verified search URL and route (`script` / `curl` / `browser`). Categories hold a `wave1` (always searched) and a `wave2` (searched when wave 1 is thin or breadth is wanted). Defaults shipped with the plugin, e.g.:

| Category | Wave 1 | Wave 2 |
|---|---|---|
| `computer_parts` | KSP, Ivory, TMS | Plonter, Bug |
| `consumer_tech` | KSP, Ivory, Bug | TMS, Plonter |
| `microphones_audio` | KZPro, Speed of Sound, Halilit, Kley Zemer | KSP, Ivory |
| `musical_instruments` | Halilit, Kley Zemer, KZPro | — |

Users extend or override it in `<plugin-data-dir>/trusted-vendors.json` (same shape; a vendor with the same `id` replaces the default, a category with the same key replaces its waves). `find-product` reads both.

---

## Amazon delivered to Israel

What the user pays to have it shipped home, without a US exit IP (verified 2026-10-21 on amazon.com, .co.uk, .de):

1. GET `/portal-migration/hz/glow/get-rendered-address-selections` with the page's `anti-csrftoken-a2z` token.
2. POST `/portal-migration/hz/glow/address-change` with `{"locationType":"COUNTRY","countryCode":"IL","district":"IL"}`.
3. Product pages then show "AmazonGlobal Shipping / Estimated Import Charges / Total", or "cannot be shipped to Israel".

Prices stay in USD; convert with `/convert-currency`. Import charges ran about 23% of item price on electronics. Where the `amazon` plugin is installed, its `amazon-listing-check` / `amazon-search` skills do this with a set delivery location.

---

## Sourcing waterfall

When a candidate has survived shortlisting and you need landed cost + availability, apply the waterfall in order:

1. **IL domestic tier-1 tech** — Ivory/KSP/Bug/TMS via `/tech-product-search`. Capture store, ILS price (VAT-incl; add 18% if ex-VAT), stock, warranty. KSP: use regular (non-Eilat) price.
2. **IL domestic tier-2 broad** — Ace/Home Center/Office Depot/Audioline via `/general-search`.
3. **Niche IL specialists** — category-dispatched search (above).
4. **Amazon** — only if domestic missing or exceeds markup threshold, and spec hasn't disabled Amazon. Verify "ships to Israel" on the product page. Add shipping + 18% VAT + possible customs duty (imports >$75 USD de minimis). Compute landed total in ILS.
5. **AliExpress** — only if spec/preferences allow. Branded items: seller rating ≥95%. Capture USD price + shipping, rating, lead time (2–6 weeks to IL), landed ILS.
6. **Manufacturer direct / B&H / specialist international** — last resort.

Pick the best channel per candidate based on landed cost, lead time vs spec tolerance, warranty, channel viability.

---

## VAT and markup verdict scale

Israeli VAT is currently 18% (as of 2025+). All retail pricing should be quoted VAT-inclusive. If a listing is ex-VAT (common for Eilat, B2B quotes, some Zap rows), normalise by adding 18% before comparing.

### RRP-vs-IL verdict scale

Used by `/rrp-check`:
- ≤5% → GOOD DEAL
- 5–15% → FAIR (typical IL import markup)
- 15–30% → ABOVE AVERAGE
- 30–40% → MILD MARKUP
- \>40% → HEAVY MARKUP (consider importing)

An IL markup of 30–40% is often still cheaper than importing once shipping + VAT + customs are counted — factor landed cost before recommending import.

---

## Browser usage notes (agent browser / Claude in Chrome / Playwright)

- Always `browser_close` when done with a retailer to free the session.
- Use `browser_snapshot` over `browser_evaluate` for extracting product cards — more robust to DOM changes.
- When a homepage search form isn't obviously matchable, fall back to trying common URL patterns (see category section) before giving up.
- Never invent prices — if you can't extract one, say so.
