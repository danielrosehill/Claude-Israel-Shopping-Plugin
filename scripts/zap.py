#!/usr/bin/env python3
"""Zap.co.il search and model-page offers over plain HTTP. Prints JSON.

Usage:
  python3 scripts/zap.py search "מיקרופון Shure SM7B"     # result cards, top 15
  python3 scripts/zap.py model 739590                        # vendor offers for one model
  python3 scripts/zap.py model https://www.zap.co.il/model.aspx?modelid=739590

Route (verified 2026-11-20): plain HTTPS GET with a desktop Chrome User-Agent from an
Israeli residential IP. Zap fingerprints headless browsers ("Request Rejected") and blocks
datacenter IPs, so Playwright and cloud fetchers are the wrong route; curl-style GET is right.

Markup (2026-11-20):
  search  -> cards split on '<div class="card-v2 '; variant 'card-v2--compare' links to
             /model.aspx?modelid=N (many vendors), 'card-v2--one-store-model' links to
             /fs?pid=N (one vendor). Title in 'card-v2__title' anchor, lowest price in
             'card-v2__price-amount'.
  model   -> each offer is '<section class="BuyBox ...' with data-site-name, data-siteid,
             data-product-price, data-shipping-price, data-shipping-days, data-site-rate, data-pid;
             every vendor row is '<div class="compare-item-row ...' with data-site-name,
             data-site-id, data-product-price, data-ship-price/data-delivery-price,
             data-delivery-time (max business days, shown as 'עד N ימי עסקים'), data-marketing-tags ('zap choice'), data-official-importer, data-warranty-company/-months.
Zap prices can lag the vendor by a day: confirm on the vendor page before quoting a winner.
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")
BASE = "https://www.zap.co.il"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "he-IL,he;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "ignore")
    if "Request Rejected" in body[:2000]:
        sys.exit(json.dumps({"error": "zap_rejected", "hint": "egress is not an Israeli residential IP, or UA looks automated"}))
    return body


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s).replace("‏", "")).strip()


def price(s):
    try:
        return float(s.replace(",", ""))
    except (TypeError, ValueError):
        return None


def search(query, limit=15):
    url = f"{BASE}/search.aspx?keyword={urllib.parse.quote(query)}"
    h = get(url)
    out = []
    for c in re.split(r'<div class="card-v2 ', h)[1:]:
        t = re.search(r'card-v2__title">\s*<a href="([^"]+)"[^>]*>(.*?)</a>', c, re.S)
        if not t:
            continue
        href = html.unescape(t.group(1))
        p = re.search(r'card-v2__price-amount">([\d,.]+)', c)
        kind = "model" if "modelid=" in href else "single_listing"
        mid = re.search(r"modelid=(\d+)", href)
        out.append({
            "title": clean(t.group(2)),
            "kind": kind,
            "modelid": int(mid.group(1)) if mid else None,
            "from_price_ils": price(p.group(1)) if p else None,
            "url": urllib.parse.urljoin(BASE, href),
        })
        if len(out) >= limit:
            break
    return {"query": query, "search_url": url, "results": out}


def model(ref):
    m = re.search(r"(\d+)", str(ref))
    mid = m.group(1)
    url = f"{BASE}/model.aspx?modelid={mid}"
    h = get(url)
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    offers, seen = [], set()
    # Buy box (Zap's featured offer) and the full comparison rows carry the same data-* fields,
    # with slightly different names for shipping; read both.
    rows = re.findall(r'<section class="BuyBox[^"]*"([^>]*)>', h) + \
        re.findall(r'<div\s+([^>]*class="compare-item-row[^"]*"[^>]*)>', h)
    for raw in rows:
        a = dict((k, html.unescape(v)) for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', raw))
        key = a.get("data-pid") or a.get("data-site-name")
        if not key or key in seen:
            continue
        seen.add(key)
        item = price(a.get("data-product-price"))
        ship = price(a.get("data-shipping-price") or a.get("data-ship-price") or a.get("data-delivery-price"))
        offers.append({
            "vendor": a.get("data-site-name"),
            "siteid": a.get("data-siteid") or a.get("data-site-id"),
            "price_ils": item,
            "shipping_ils": ship,
            "total_ils": (item or 0) + (ship or 0) if item is not None else None,
            "delivery_business_days_max": a.get("data-shipping-days") or a.get("data-delivery-time"),
            "zap_choice": "zap choice" in (a.get("data-marketing-tags") or ""),
            "vendor_rating": a.get("data-site-rate"),
            "official_importer": a.get("data-official-importer"),
            "parallel_importer": a.get("data-parallel-importer"),
            "warranty_company": a.get("data-warranty-company"),
            "warranty_months": a.get("data-warranty-months"),
            "pid": a.get("data-pid"),
        })
    offers.sort(key=lambda o: (o["total_ils"] is None, o["total_ils"] or 0))
    return {"modelid": int(mid), "title": clean(title.group(1)).replace(" - זאפ השוואת מחירים", "") if title else None,
            "model_url": url, "offers": offers}


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("search", "model"):
        sys.exit(__doc__)
    fn = search if sys.argv[1] == "search" else model
    print(json.dumps(fn(" ".join(sys.argv[2:])), ensure_ascii=False, indent=1))
