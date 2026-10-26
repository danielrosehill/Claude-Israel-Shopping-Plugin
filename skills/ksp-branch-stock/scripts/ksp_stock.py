#!/usr/bin/env python3
"""KSP per-branch stock. Stdlib only.

Usage:
  ksp_stock.py "<search query>"            search, then stock for the top results
  ksp_stock.py https://ksp.co.il/web/item/11239
  ksp_stock.py 11239                       item id from the URL (uin)
  ksp_stock.py --sku 9871                  KSP catalogue number (מק"ט / uinsql)

Options:
  --branch X     branch to report (repeatable): id ("57"), key ("jeruscenter") or name
                 substring ("קינג", "talpiot"). Default: home branches from
                 <plugin-data-dir>/home-branches.json, else every branch.
  --all          report every branch, ignoring home branches
  --limit N      search results to check (default 8)

Output: JSON on stdout. Exit 2 when KSP blocks the request (HTTP 403): use the
browser fallback in ksp_stock_browser.js.
"""
import argparse, datetime, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

BASE = "https://ksp.co.il/m_action/api"
# KSP's bot filter lets requests through only with the Sec-Fetch-* headers a browser's
# own XHR sends (verified 2026-10-26). It also starts returning 403 on search/item
# after ~100 rapid requests; mlay (stock) kept answering.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9",
    "Referer": "https://ksp.co.il/web/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
}


class Blocked(Exception):
    pass


def get_json(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise Blocked(path)
        raise


def data_dir():
    root = os.environ.get("CLAUDE_USER_DATA") or os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "claude-plugins")
    return os.path.join(root, "israel-shopping")


def home_branches():
    try:
        with open(os.path.join(data_dir(), "home-branches.json"), encoding="utf-8") as f:
            return [str(b) for b in json.load(f).get("ksp", [])]
    except FileNotFoundError:
        return []


def branch_matches(store, key, wanted):
    for w in wanted:
        wl = w.lower()
        if w == store["id"] or wl == key.lower() or wl in store["name"].lower() or wl in key.lower():
            return True
    return False


def stock(sku, wanted):
    # mlay takes the catalogue number (uinsql), NOT the URL id. Passing the URL id
    # returns a valid-looking response with every branch at qnt 0.
    stores = (get_json(f"/mlay/{sku}").get("result") or {}).get("stores") or {}
    rows = [{"id": s["id"], "key": k, "name": s["name"], "region": s["region"],
             "in_stock": s["qnt"] > 0, "last_unit": bool(s["isLastItem"])}
            for k, s in stores.items()]
    shown = [r for r in rows if branch_matches(r, r["key"], wanted)] if wanted else rows
    return sum(r["in_stock"] for r in rows), shown


def item_record(uin, sku, name, price, eilat, wanted):
    n, branches = stock(sku, wanted)
    return {"id": int(uin), "sku": str(sku), "name": name, "price_ils": price, "eilat_price_ils": eilat or None,
            "url": f"https://ksp.co.il/web/item/{uin}", "branches_in_stock": n, "branches": branches}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--sku", action="store_true", help="target is a KSP catalogue number (uinsql)")
    ap.add_argument("--branch", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()

    wanted = [] if a.all else (a.branch or home_branches())
    out = {"retailer": "ksp", "checked_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "branch_filter": wanted or "all", "items": []}
    try:
        m = re.search(r"/item/(\d+)", a.target)
        if a.sku:
            n, branches = stock(a.target, wanted)
            out["items"].append({"sku": a.target, "url": None, "branches_in_stock": n, "branches": branches})
        elif m or a.target.isdigit():
            uin = m.group(1) if m else a.target
            d = get_json(f"/item/{uin}")["result"]["data"]
            out["items"].append(item_record(uin, d["uinsql"], d["name"], d["price"], d.get("eilatPrice"), wanted))
        else:
            res = get_json("/category/?search=" + urllib.parse.quote(a.target))["result"]
            out["products_total"] = res.get("products_total")
            for it in (res.get("items") or [])[: a.limit]:
                out["items"].append(item_record(it["uin"], it["uinsql"], it["name"], it["price"],
                                                it.get("eilatPrice"), wanted))
                time.sleep(0.3)
    except Blocked as e:
        out["error"] = f"blocked (HTTP 403) on {e}; use the browser fallback (ksp_stock_browser.js)"
        print(json.dumps(out, ensure_ascii=False, indent=1))
        sys.exit(2)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
