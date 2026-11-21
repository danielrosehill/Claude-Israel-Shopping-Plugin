---
name: store-reputation
description: Vet an Israeli store before buying by combining its Zap store-card reviews with its Google Maps rating, then giving one verdict (safe / safe with caveats / caution / avoid). Zap alone is thin for small shops (few, old reviews) and Google alone can be gamed, so it needs both. Takes a store name, domain or Zap siteid. Use for "is this store reputable", "can I trust <shop>", "check the store's reputation", "is <domain> legit", or before recommending an unfamiliar vendor from a price comparison.
---

# Store reputation: Zap + Google Maps

One verdict on an Israeli retailer from two independent signals. This supersedes `/store-zap-lookup` for vetting; that command remains for just finding the Zap profile.

## Inputs

A store name (Hebrew or English), a domain, or a Zap siteid / clientcard URL. If a city or address is known, carry it: Google Maps matching needs it.

## Workflow

Run steps 2 and 3 in parallel.

1. **Resolve the store.** `python3 scripts/stores.py --find "<domain or name>"` gives `zap_url` (with `siteid`), city and categories. For a store missing from the roster, search `site:zap.co.il clientcard "<name>"`; the siteid is also in every Zap offer row. Also take the address from the store's contact or footer page.

2. **Zap.** `python3 skills/store-reputation/scripts/zap_reputation.py <siteid> --reviews 5`. It fetches with a plain GET and a desktop Chrome UA (verified 2026-11-21) and returns JSON:
   - `counts`: positive / neutral / negative counts for the month, 3 months, 6 months, year and all time
   - `total_reviews`, `reviews_last_year` and `positive_share_all`
   - `address` and `recent_reviews`

   A `warning` field means the rating block was not found. Retry once, then fetch the clientcard URL with a web-fetch tool and read the "דירוג החנות" block by hand.

3. **Google Maps.** You need the rating (out of 5), the number of ratings, and the place's address, category and opening hours.
   - **Route A, first try (verified 2026-11-21):** a semantic web search such as Exa `web_search_exa` with the query `"<Hebrew name> <city> ביקורות"` and the objective "Google Maps place rating and review count for <store> at <address>". It returns a place record like "rated 4.1 (71)" with address and phone.
   - **Route B:** open `https://www.google.com/maps/search/<name>+<city>` in a real browser (Claude in Chrome) and read the rating line under the place name. Headless fetches of Google Maps return no rating.
   - **Route C:** directory sites that mirror Google-style ratings, such as openinghours.co.il, d.co.il (Dapei Zahav) and easy.co.il. They are secondary: label them as such and never substitute them for Google.
   - **Matching:** confirm the address matches what step 1 found. Chains have many places, so use the branch you would deal with, or say that the figure covers one branch.

4. **Optional extra signals,** only if steps 2–3 are thin or conflict:
   - how long the domain or store has been trading: the oldest Zap review or the site's "about" page
   - complaints: web search `"<name>" תלונה OR נוכלים OR עוקץ`

## Verdict rules

| Verdict | When |
|---|---|
| **Safe** | Google ≥ 4.3 with ≥ 50 ratings, and Zap positive share ≥ 0.85 or no Zap negatives |
| **Safe with caveats** | Google 3.8–4.3, or under 50 ratings, or Zap thin (< 10 reviews or none in the last year). Say what the caveat is |
| **Caution** | Google < 3.8, or Zap negatives ≥ 20 % in the last year, or a recurring complaint pattern (non-delivery, refund refusals) |
| **Avoid** | Recurring scam or non-delivery reports, or no physical address and no presence on either platform |

- **Thin data is not bad data.** A small shop with 3 old positive Zap reviews and a decent Google score gets "safe with caveats", not "caution".
- **Reviews of a different service:** many Israeli audio shops are listed on Google as rental services, so their reviews may be about rentals. Note this when it applies.

## Output

```
## <store> (<domain>): <verdict>

| Signal | Result | Source |
|---|---|---|
| Google Maps | 4.1 ★ (71 ratings), category | route used |
| Zap | 3 reviews, 3 positive / 0 negative, 0 in the last year | clientcard URL |
| Secondary | openinghours.co.il 3.0 (14) … | |

Verdict: <one sentence why>. Caveats: <stock or warranty quirks, thin data>.
Checked <YYYY-MM-DD>.
```

## Rules

- Never invent a rating. If a route failed, say which route failed and how.
- State the date: ratings drift.
- Keep the two platforms separate in the output. Don't average them.
- When vetting a store with a trusted-vendors entry, append the result to that vendor's `notes` in the user's `<plugin-data-dir>/trusted-vendors.json` overlay, as "Reputation YYYY-MM-DD: Google X (N), Zap P/T positive".
