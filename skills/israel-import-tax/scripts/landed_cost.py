#!/usr/bin/env python3
"""Israeli personal-import landed cost (estimate, not customs advice).

Rules encoded (confirm live; see SKILL.md): goods up to USD 75 are exempt (tested on goods
value only); above that VAT applies on CIF, plus duty/purchase tax where the tariff item
carries them (duty is waived for personal imports up to USD 500). Customs converts at the
Bank of Israel representative rate x 1.005; the goods themselves are priced at the plain
rate. Stdlib only. Ad-valorem rates only.

Two routes, never both:
  --combined-rate 0.4066   the single all-in % the Tax Authority calculator shows (VAT included)
  --duty-rate / --purchase-tax-rate   cascade; purchase-tax output is a FLOOR (no TAMA uplift)
Example:
  uv run python landed_cost.py --value 200 --shipping 20 --fx 3.65 --usd-value 200
"""
import argparse, json
from decimal import Decimal as D, ROUND_HALF_UP

VAT = D("0.18")            # standard rate since 2025-01-01
THRESHOLD_USD = D("75")    # personal import exemption; changed 4x Dec 2025 - Jun 2026
DUTY_WAIVER_USD = D("500")
UPLIFT = D("1.005")

def m(x): return x.quantize(D("0.01"), ROUND_HALF_UP)

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for n, d in (("value", None), ("shipping", "0"), ("insurance", "0"), ("fx", None),
                 ("duty-rate", "0"), ("purchase-tax-rate", "0"), ("combined-rate", None),
                 ("broker-fees-ils", "0"), ("usd-value", None)):
        a.add_argument("--" + n, type=D, default=None if d is None else D(d), required=n in ("value", "fx"))
    a.add_argument("--currency", default="USD")
    a.add_argument("--commercial", action="store_true", help="B2B: no threshold, no duty waiver")
    a.add_argument("--excluded-goods", action="store_true", help="tobacco/alcohol: never exempt (not priceable here)")
    a.add_argument("--json", action="store_true")
    x = a.parse_args()

    goods_usd = x.value if x.currency.upper() == "USD" else x.usd_value
    personal = not x.commercial
    notes = []
    if personal and goods_usd is None and not x.excluded_goods:
        a.error("non-USD invoice needs --usd-value to test the USD 75 threshold")
    paid_ils = (x.value + x.shipping + x.insurance) * x.fx   # what the seller is paid
    base = {"currency": x.currency.upper(), "fx_representative": str(x.fx),
            "fx_customs": str(m(x.fx * UPLIFT) if x.currency.upper() != "ILS" else x.fx)}
    if personal and not x.excluded_goods and goods_usd <= THRESHOLD_USD:
        r = dict(base, exempt=True, duty=0, purchase_tax=0, vat=0, goods_and_freight_ils=str(m(paid_ils)),
                 landed_cost_ils=str(m(paid_ils + x.broker_fees_ils)),
                 notes=["At or below USD 75: no tax. Anti-splitting: parcels from one supplier to one buyer within 72 h are combined."])
    else:
        cfx = x.fx if x.currency.upper() == "ILS" else x.fx * UPLIFT
        cif = (x.value + x.shipping + x.insurance) * cfx
        if x.combined_rate is not None:
            tax = cif * x.combined_rate
            duty = pt = vat = None
            notes.append("Route: Tax Authority all-in rate on CIF (VAT included).")
        else:
            dr = x.duty_rate
            if personal and goods_usd is not None and goods_usd <= DUTY_WAIVER_USD and not x.excluded_goods:
                dr = D(0)
                notes.append("Duty waived (personal import up to USD 500).")
            duty = cif * dr
            pt = (cif + duty) * x.purchase_tax_rate
            vat = (cif + duty + pt) * VAT
            tax = duty + pt + vat
            if x.purchase_tax_rate > 0:
                notes.append("Purchase tax is a FLOOR: real base is a reconstructed wholesale price. Use the official calculator's all-in % instead.")
        if x.excluded_goods:
            notes.append("Tobacco/alcohol have specific/compound rates this script cannot price.")
        if goods_usd is not None and goods_usd > 1000:
            notes.append("Over USD 1,000 is treated as commercial in practice: expect a customs broker.")
        r = dict(base, exempt=False, cif_ils=str(m(cif)),
                 duty=None if duty is None else str(m(duty)),
                 purchase_tax=None if pt is None else str(m(pt)),
                 vat=None if vat is None else str(m(vat)), tax_total_ils=str(m(tax)),
                 goods_and_freight_ils=str(m(paid_ils)),
                 landed_cost_ils=str(m(paid_ils + tax + x.broker_fees_ils)), notes=notes)
    r["not_included"] = "Israel Post / courier clearance commission (varies by carrier); pass --broker-fees-ils to include."
    print(json.dumps(r, ensure_ascii=False, indent=2) if x.json else "\n".join(f"{k}: {v}" for k, v in r.items()))

if __name__ == "__main__":
    main()
