---
name: whats-this-brand
description: Identify an obscure brand encountered only in Israel. Many IL-market brands are white-labelled / rebadged versions of global brands or importer-specific labels. Returns probable OEM and international equivalent.
---

# What's This Brand?

User saw a brand name in an Israeli listing that doesn't match any global brand they recognise. Identify what it actually is — likely white-label, importer-specific, or genuinely local.

## When to use

- User asks "what is [brand]?" or "is [brand] any good?" for a brand they've only seen in Israel.
- Comparing an IL-market brand against a known global equivalent.
- Before buying a cheap unfamiliar brand — sanity-check whether it's a rebrand of something known.

## Workflow

1. **WebSearch** the brand name with Israeli context:
   - `"<brand>" Israel importer`
   - `"<brand>" יבואן` (Hebrew for "importer")
   - `"<brand>" white label OEM`
2. **Check the brand's Israeli website** (if any) for clues: address, importer disclosure (mandated by IL consumer law on some categories), OEM references, country of manufacture.
3. **Compare product photos** to known global brands — Israeli rebrands often keep the exact mold/design of the OEM. Reverse-image-search a product shot if unclear.
4. **Check shopping forums** — זאפ community, Ynet shopping, HWzone — users often identify rebrands there.
5. **Classify:**
   - **White-label of known OEM** — identify the OEM and name the comparable global product.
   - **Importer-specific label** — local distributor puts their brand on a generic OEM product; often Chinese ODM.
   - **Genuinely local IL brand** — e.g. some home-goods and furniture brands are actually Israeli.
   - **Unknown** — can't determine confidently.

## Output

```
## {brand} — what is it?

**Verdict:** {white-label | importer-label | local IL brand | unknown}
**Confidence:** {confident | tentative | unknown}

**Probable OEM / equivalent:** {global brand / model if identified}
**International equivalent product:** {name + link if applicable}

### Evidence
- {website / importer disclosure / product-photo match / forum thread}
- {country of manufacture, if determinable}

### Recommendation
- {worth buying? buy the international equivalent instead? wait for more info?}
```

## Rules

- Don't claim a specific OEM identification without evidence (visual match, importer disclosure, or credible forum consensus).
- If confidence is low, say "unknown" — don't guess.
- White-labels aren't inherently bad — flag it factually, not judgmentally.
