---
name: discover-hebrew-term
description: Discover the canonical Hebrew retail term for a product class by finding an Israeli listing of a known SKU and reading the Hebrew noun off its title/URL/breadcrumbs. Use when the product class has no mapping in data/hebrew-category-map.json, or when existing Hebrew terms return weak search results. Critical preflight for any shopping search — Israeli retailers index in Hebrew and Google Translate often gives the wrong term.
---

# Discover Hebrew Term

Half of Israeli-shopping is figuring out what the accepted Hebrew term is for a product class. Google Translate is often wrong — retailers use idiomatic Israeli retail jargon, not literal translations. The fix: find **one** Israeli listing for a representative SKU and read the canonical Hebrew noun straight off the page.

This skill implements that reverse-lookup.

## When to invoke

- `data/hebrew-category-map.json` has no entry for the product class.
- The mapped terms are returning zero results across multiple retailers (term may be stale or wrong).
- The user asks for a niche / specialty product that's unlikely to be in the seed map.

## Inputs

- **Product class** in English (e.g. "desktop charging tower", "mechanical keyboard", "headlamp").
- **Optional: a known SKU** that's definitely sold in Israel — speeds up the lookup dramatically. Any popular model in that class works (e.g. `Anker A2343` for chargers, `Eneloop AA` for batteries, `Nitecore HC65` for headlamps).

If no SKU is given, ask the user for one, or pick a plausible bestseller in the category and proceed.

## Workflow

### Step 1 — Google for a known IL listing

Use the Google discovery skill (`search-google-il`) or Playwright directly:

```
"<brand model>" site:.il
```

Prefer `site:.il` over `site:co.il` here — `.il` also catches `.org.il`, `.net.il`, brand pages hosted at subdomains.

Example queries:

- `"Anker A2343" site:.il`
- `"Nitecore HC65" site:.il`
- `"Eneloop BK-3MCCE" site:.il`

### Step 2 — Open the top 2–3 retail results

Filter to domains that look like retailers (skip news, blogs, forums). Good signals:

- Domain ends in `co.il` and isn't `ynet`, `walla`, `haaretz`, `calcalist` (news).
- Listed on Zap (domain appears in Zap vendor list).
- Domain is in `data/israeli-stores.json`.

### Step 3 — Extract the Hebrew noun

Look at three sources on each page, in this order:

1. **URL slug** — the cleanest source. Hebrew appears url-encoded; decode to read it. Example:
   ```
   lev-hamisrad.co.il/%D7%A2%D7%9E%D7%93%D7%AA-%D7%98%D7%A2%D7%99%D7%A0%D7%94-...
   ```
   Decodes to `עמדת-טעינה-...` → canonical Hebrew noun is `עמדת טעינה`.

2. **Page title** — the `<title>` tag usually starts with the Hebrew product class noun, followed by brand/model. Strip the retailer-name suffix.

3. **Breadcrumb navigation** — often the clearest source of the Hebrew category name. Look for elements matching `.breadcrumb`, `nav[aria-label*="breadcrumb"]`, or schema.org breadcrumb markup.

### Step 4 — Normalise

- Convert to **singular**. Retailers usually index in singular even for inherently-plural products (batteries, cables). Strip the plural `ות`/`ים` suffix if present (but check — some nouns don't have singular forms in retail use).
- Identify **multiple variants**. If different retailers use different Hebrew terms, record all of them. Common for chargers (`עמדת טעינה` vs `מטען שולחני` vs `תחנת טעינה`).
- Record an **exclude list** if you see the term colliding with a different product class. Example: `סוללה ניידת` (power bank) should be excluded when searching for `סוללות נטענות` (rechargeable batteries).

### Step 5 — Cache

Append the result to `data/hebrew-category-map.json` under a new category key (snake_case English). Include:

- `en_aliases`: all the English phrasings you've encountered
- `he_terms`: most-common first
- `exclude_he`: Hebrew terms that look similar but are a different category
- `notes`: anything about retailer-specific phrasing or gotchas

Commit the change so the next caller benefits.

## Output

```
## Hebrew term for "{english category}"

**Canonical:** {primary he_term}
**Alternates:** {he_term_2}, {he_term_3}
**Derived from:** {source URL} (listing for {sku})

**Cached to:** data/hebrew-category-map.json under `{category_key}`

### Why this term
- {slug/title/breadcrumb evidence}
- {any retailer-specific phrasing noted}
```

## Rules

- Never guess. If no IL listing can be found for ANY SKU in the class, report that and ask the user for guidance — do not invent a Hebrew term.
- Never trust Google Translate alone. The whole point of this skill is that Translate gets retail jargon wrong.
- If the user provides a Hebrew term they've seen used, trust it over your derivation and skip to caching.
- Always cache — the next user in the class shouldn't have to re-derive.
