---
name: freier-check
description: Playful "are you a freier" (sucker) assessment — given an Israeli price and international RRP, compute the premium and deliver a verdict on the freier scale. Light-hearted counterpart to `/rrp-check`.
---

# Freier Check

Are you a freier? Let's find out.

IL VAT (18%) + typical import margin means a 30–40% premium over international RRP is actually normal — the scale starts at "not a freier" below that.

## When to use

- User has an IL price and an international RRP and wants a quick verdict with attitude.
- After `/rrp-check`, when the markup pct is the actual question.

## Workflow

Reuses `/rrp-check` for the calculation — run that logic (or its output) to get the % over RRP, then apply the scale.

1. Confirm IL price is VAT-inclusive. Normalise if ex-VAT.
2. Convert international RRP to ILS at the live rate.
3. Compute premium: `(il_price - intl_rrp_ils) / intl_rrp_ils * 100`.
4. Apply the scale:
   - **≤ 30%** → *"Not a freier. Normal IL tax/import premium. Buy it."*
   - **30–70%** → *"Mild freier. Worth checking alternatives but not outrageous."*
   - **70–150%** → *"Freier territory. Consider waiting, importing, or finding an alternative."*
   - **> 150%** → *"Full freier. Tell your uncle to bring it from chutz la'aretz."*

## Output

```
## Freier check — {product}

- **IL price:** ₪{il_price} (inc. VAT)
- **International RRP:** {ccy}{rrp} (≈ ₪{rrp_ils} at {rate})
- **Premium:** ₪{diff} ({pct}%)

### Verdict
{bucket verdict line}

{one line of advice — buy locally / wait / import / ask the uncle}
```

## Rules

- Keep it light — the scale is meant to be fun, not a financial instrument.
- Note the 18% VAT + importer-margin baseline when the premium is in the "not a freier" bucket so the user understands why 30% isn't outrageous.
- If the international RRP can't be verified, bail out and suggest `/rrp-check` instead — don't freier-shame on a guessed RRP.
