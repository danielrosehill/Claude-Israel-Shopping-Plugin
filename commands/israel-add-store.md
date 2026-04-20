---
description: Append a vendor to the workspace's Israeli store database with auto-dedup.
---

# Israel — Add Store

Add a new Israeli vendor to the workspace's `data/israeli-stores.json`. Auto-dedups by domain and auto-derives categories from the free-text description.

## Arguments

`$ARGUMENTS`: `<url> "<what they sell>" [--name "Display Name"] [--is-tech true|false|null]`

## Behaviour

1. Parse the URL to get the domain.
2. Read `data/israeli-stores.json`. If an entry with the same domain already exists, report it and exit without changes.
3. Derive `categories[]` from the description using the controlled-vocabulary keyword map in `data/hebrew-category-map.json`.
4. Insert the new entry alphabetically by name and write the file back.

## Flags

- `--name` — override the auto-derived name (defaults to title-cased leftmost domain label)
- `--is-tech` — `true` (default), `false`, or `null` if unsure. Skills only navigate to entries with `true` or `null`.

## Output

Report: store name, domain, derived categories, total entry count after insert.
