#!/usr/bin/env python3
"""Ivory per-branch stock. Stdlib only. No bot filter on these endpoints (2026-10-26).

Usage:
  ivory_stock.py "<search query>"          search, then stock for the top results
  ivory_stock.py "https://www.ivory.co.il/catalog.php?id=150475"
  ivory_stock.py 150475                    product id

Options:
  --branch X     branch to report (repeatable): branch code ("24") or name substring
                 ("קינג", "תלפיות"). Default: home branches from
                 <plugin-data-dir>/home-branches.json, else every branch.
  --all          report every branch, ignoring home branches
  --limit N      search results to check (default 8)

Output: JSON on stdout.
"""
import argparse, datetime, html, json, os, re, time, urllib.parse, urllib.request

BASE = "https://www.ivory.co.il"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Accept-Language": "he-IL,he;q=0.9",
}


def get(path):
    with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=HEADERS), timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def data_dir():
    root = os.environ.get("CLAUDE_USER_DATA") or os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "claude-plugins")
    return os.path.join(root, "israel-shopping")


def home_branches():
    try:
        with open(os.path.join(data_dir(), "home-branches.json"), encoding="utf-8") as f:
            return [str(b) for b in json.load(f).get("ivory", [])]
    except FileNotFoundError:
        return []


def stock(pid, wanted):
    # check_balance is what the product page's "הצג זמינות מלאי בסניפים" popup renders.
    # notAvailable=1 shows as the orange "i" icon (orderable to the branch, not on the
    # shelf); isAvailable=1 is the green tick. Matched against the popup 2026-10-26.
    d = json.loads(get(f"/catalog-items/ws/check_balance/{pid}"))
    rows = [{"code": r["branch_code"], "name": html.unescape(r["branchName"]).strip(),
             "address": html.unescape(r.get("address") or ""), "in_stock": not r.get("notAvailable")}
            for r in d.get("Data") or []]
    shown = [r for r in rows if any(w == r["code"] or w.lower() in r["name"].lower() for w in wanted)] if wanted else rows
    return sum(r["in_stock"] for r in rows), shown


def product_meta(pid):
    h = get(f"/catalog.php?id={pid}")
    title = re.search(r'<meta property="og:title" content="([^"]+)"', h)
    price = re.search(r'"price"\s*:\s*"?([\d.]+)', h)
    return (html.unescape(title.group(1)) if title else None), (float(price.group(1)) if price else None)


def search(query, limit):
    h = get("/catalog.php?act=cat&q=" + urllib.parse.quote(query))
    found = []
    for card in h.split("catalogVertical_item")[1:]:
        pid = re.search(r'data-product-id="(\d+)"', card)
        if not pid:
            continue
        title = re.search(r'class="img-fluid[^"]*"[^>]*title="([^"]+)"', card)
        price = re.search(r"מחיר רגיל:\s*([\d,.]+)", card)
        found.append((pid.group(1), html.unescape(title.group(1)) if title else None,
                      float(price.group(1).replace(",", "")) if price else None))
        if len(found) >= limit:
            break
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--branch", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()

    wanted = [] if a.all else (a.branch or home_branches())
    m = re.search(r"[?&]id=(\d+)", a.target)
    if m or a.target.isdigit():
        pid = m.group(1) if m else a.target
        products = [(pid, *product_meta(pid))]
    else:
        products = search(a.target, a.limit)

    items = []
    for pid, name, price in products:
        n, branches = stock(pid, wanted)
        items.append({"id": int(pid), "name": name, "price_ils": price,
                      "url": f"{BASE}/catalog.php?id={pid}", "branches_in_stock": n, "branches": branches})
        time.sleep(0.3)
    print(json.dumps({"retailer": "ivory",
                      "checked_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                      "branch_filter": wanted or "all", "items": items}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
