---
name: israel-import-tax
description: Estimate the Israeli import tax and landed cost of a personal online order (Amazon, AliExpress, any foreign shop): the USD 75 exemption, VAT, customs duty, purchase tax, HS-code lookup, FTA origin proof, approvals, refunds. Use on "how much import tax will I pay", "will this be taxed at customs", "landed cost of this order", "what is the HS code for X", "mas kniya", before recommending an import over a local purchase.
---

# Israel import tax and landed cost

The one place the other skills and commands (`find-product`, `compare-to-local`, `/rrp-check`, and the Amazon and AliExpress plugins) send for "what does this really cost once it clears customs". An estimate from stated rules, not customs or tax advice: the binding charge is set by the Tax Authority at import.

## Rules as of 2026-11-20 (confirm before quoting)

Source skill verified these on 2026-10-18. Law and thresholds move; the live official calculators decide:
- Personal import calculator: https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/PersonalImportTax
- gov.il service: https://www.gov.il/en/service/customs-tax-calculation-import-by-israelis
- Tariff item lookup (duty, purchase tax, import conditions): https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/en/CustomsBook/Import/Doubt

| Goods value (excl. shipping and insurance) | Treatment |
|---|---|
| Up to USD 75 inclusive | No customs, VAT or purchase tax. The threshold changed four times Dec 2025 to Jun 2026 (75, 150, 130, back to 75): always re-check |
| USD 75 to 500 | Duty waived; VAT 18% (since 2025-01-01) on CIF; purchase tax still applies to goods that carry it (e.g. televisions, vehicle parts) |
| Over USD 500 | VAT, plus duty and purchase tax on items whose tariff line carries them. Not automatic: depends on the HS code |
| Over USD 1,000 | Treated as commercial in practice; carriers usually require a customs broker |

- Threshold is tested on goods alone; the tax is on CIF (goods + freight + insurance) plus duty and purchase tax.
- **Anti-splitting:** parcels from one supplier to one buyer within 72 hours are combined.
- **Never exempt:** tobacco and alcohol (specific/compound rates; not priced here).
- **FX:** customs uses the Bank of Israel representative rate plus 0.5% for the tax base only; the goods themselves are priced at the plain rate. Rate source: the gateway `fx` tool or boi.org.il.
- Courier/postal clearance commission is the carrier's own charge on top, not tax; disputes go to the carrier.
- Business buyers (Osek Murshe): no threshold; import VAT may be recoverable as input tax, check with your bookkeeper. Compare ex-VAT on both sides.

## Flow

1. **Check the order first.** If the seller or courier already collected Israeli tax (DDP, tax line at checkout), do not add it again.
2. **Import type:** personal parcel vs commercial. Aliyah/returning-resident, ATA carnet, repair re-imports and diplomatic entry are separate regimes: do not compute, send to a customs agent.
3. **Under USD 75:** done, add shipping and say the threshold was re-checked.
4. **Otherwise classify:** describe the product, find the HS chapter/heading, then the full Israeli tariff item in Shaar Olami (digits after the sixth are Israeli; a US HTS or EU CN code does not carry over). Do not guess them. Guide: `references/hs-codes-guide.md`.
5. **Rate:** read duty and purchase tax off the tariff item. Prefer the Tax Authority calculator's single all-in percentage for that parcel value and apply it once to CIF (`--combined-rate`); never add 18% on top of it. Rates that are not a bare percentage (per kg, per litre, compound) cannot be priced by the script.
6. **Compute:**
   ```bash
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/israel-import-tax/scripts/landed_cost.py \
     --value 200 --shipping 20 --fx <BOI representative rate> [--combined-rate 0.4066 | --duty-rate X --purchase-tax-rate Y] [--broker-fees-ils N] --json
   ```
   The cascade route's purchase-tax line is a floor (the real base is a reconstructed wholesale price), so label any such total "at least".
7. **FTA origin:** a valid origin proof removes duty only, never VAT or purchase tax. US, EU, UK, Canada, EFTA, Mercosur: `references/fta-preferences.md`. EUR.1 needs a wet-ink original.
8. **Approvals before tax:** communications gear (and 4+ phones), baby monitors (Ministry of Communications), vehicle parts (Transport), food and supplements (Health), plants (Agriculture), helmets and gas barbecues (Standards Institute) can be stopped regardless of tax.
9. **Report:** tax lines, the all-in landed total in ILS, what is excluded (clearance commission), the rule date, and the official calculator link. Say which figures are floors.

## Disputes and refunds

- Tax amount wrong: online application via the National Identification System personal area, with proof of payment to the supplier and the real transaction value; free. Help from the claims, deposits and arrears unit (tafag).
- Goods returned or exchanged as defective or not as described: tax refundable if not imported in bulk, not used beyond finding the defect, returned within 6 months with proof, and shown to be the same goods. Over USD 250 returned, the export must be recorded on the export declaration with a physical check: this cannot be added afterwards.
- Eilat residents can reclaim VAT on a personal import.
- A false declaration can get the parcel seized or fined even if the buyer did not know: make sure the declared contents and value match the purchase.

## Sources

Adapted from [israeli-customs-duty-calculator](https://github.com/skills-il/tax-and-finance/tree/14f6a7485156d94746139e6df047fe88be87c2aa/israeli-customs-duty-calculator) by Skills IL (MIT). Condensed into a landed-cost skill for the shopping flow; kept the two references; replaced the 19 KB calculator with a short stdlib script of the same maths; dropped the indicative per-category duty table (stale-prone) and the broker/commercial detail.
