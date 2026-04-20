---
name: add-store
description: Append a user-added Israeli vendor to the persistent user store list (`~/.claude/plugins-data/israel-shopping/user-stores.json`) with auto-dedup. Survives plugin updates.
---

# Add Store

Append a new Israeli retailer to the user's persistent store overlay. Does **not** modify the upstream `stores.json` or anything inside the plugin install directory — those get clobbered on update.

## Arguments

`$ARGUMENTS`: `<url> "<what they sell>" [--name "Display Name"] [--is-tech true|false|null]`

## Storage

User additions go to:

```
~/.claude/plugins-data/israel-shopping/user-stores.json
```

Create the parent directory if missing. File is a JSON array of store entries whose shape matches the upstream `stores.json`. To confirm the current schema, fetch a live entry:

```
https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json
```

and use the same field names and types.

> Consumer commands (`/tech-product-search`, `/general-search`, `/store-zap-lookup`, etc.) load the upstream list first and overlay `user-stores.json` on top — see `docs/search-strategies.md` § store-metadata merge convention.

## Behaviour

1. Parse the URL → canonical domain.
2. Ensure `~/.claude/plugins-data/israel-shopping/` exists; create if not. Initialise `user-stores.json` with `[]` if missing.
3. Load `user-stores.json`. Also load the upstream `stores.json` to check for duplicates across the merged set.
4. If the domain already exists in either list, report it and exit without changes.
5. Derive `categories[]` from the `<what they sell>` free-text description using the controlled vocabulary (see strategies doc).
6. Build the entry matching the upstream schema (`name`, `url`, `categories`, `is_tech`, `description`, plus any available metadata like `delivery`, `eilat_door`, `zap_profile` if obvious from the site — leave null otherwise).
7. Append to `user-stores.json` and write back, preserving JSON formatting (2-space indent).

## Flags

- `--name` — override the auto-derived name (default: title-cased leftmost domain label).
- `--is-tech` — `true` (default), `false`, or `null` if unsure. Consumer commands only navigate to entries with `true` or `null`.

## Output

```
## Added store

- **Name:** {name}
- **Domain:** {domain}
- **Categories:** {cats}
- **is_tech:** {bool/null}
- **Saved to:** ~/.claude/plugins-data/israel-shopping/user-stores.json
- **User overlay entry count:** {n}
- **Merged total (upstream + user):** {n}
```

## Rules

- Never write to the plugin install directory. User data lives under `~/.claude/plugins-data/israel-shopping/`.
- Dedup across the merged set (upstream + user overlay) — don't re-add a store that's already in the upstream canonical list.
- If `is_tech: false`, still store the entry for user reference, but consumer commands will skip it.
