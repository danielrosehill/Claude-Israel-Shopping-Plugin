#!/usr/bin/env python3
"""Zap store-card reputation as JSON.

Usage: zap_reputation.py <siteid | clientcard URL> [--reviews N]

Fetches https://www.zap.co.il/clientcard.aspx?siteid=<id> with a desktop Chrome UA
(plain GET works from an Israeli IP, verified 2026-11-21) and parses the
"דירוג החנות" block: positive/neutral/negative counts per period, plus the newest reviews.
"""
import html, json, re, sys, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
PERIODS = ["month", "3_months", "6_months", "year", "all"]


def text_of(raw: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    arg = sys.argv[1]
    n_reviews = int(sys.argv[sys.argv.index("--reviews") + 1]) if "--reviews" in sys.argv else 5
    m = re.search(r"siteid=(\d+)", arg)
    siteid = m.group(1) if m else arg
    if not siteid.isdigit():
        print(json.dumps({"error": "need a numeric siteid or clientcard URL"}))
        return 2
    url = f"https://www.zap.co.il/clientcard.aspx?siteid={siteid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "he-IL,he;q=0.9"})
    try:
        raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"url": url, "error": str(e)}))
        return 1
    t = text_of(raw)
    out = {"url": url, "siteid": int(siteid)}
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw, flags=re.S)
    if h1:
        out["store"] = text_of(h1.group(1))
    counts = {}
    for label, key in (("חיובי", "positive"), ("ניטרלי", "neutral"), ("שלילי", "negative")):
        mm = re.search(label + r"((?: \d+){5})", t)
        if mm:
            counts[key] = dict(zip(PERIODS, map(int, mm.group(1).split())))
    out["counts"] = counts or None
    mm = re.search(r"נמצאו (\d+) חוות דעת", t)
    out["total_reviews"] = int(mm.group(1)) if mm else (sum(c["all"] for c in counts.values()) if counts else 0)
    if counts:
        last_year = sum(c["year"] for c in counts.values())
        out["reviews_last_year"] = last_year
        alln = sum(c["all"] for c in counts.values())
        out["positive_share_all"] = round(counts.get("positive", {}).get("all", 0) / alln, 2) if alln else None
    mm = re.search(r"כתובת (.{3,80}?) נמצאו", t)
    if mm:
        out["address"] = mm.group(1).strip()
    reviews = re.findall(r"(\S+) (\d{2}\.\d{2}\.\d{4}) מוצר שנרכש: (.*?)(?= חוות הדעת עזרה לכם)", t)
    out["recent_reviews"] = [
        {"author": a, "date": d, "text": body[:300]} for a, d, body in reviews[:n_reviews]
    ]
    if not counts and "דירוג החנות" not in t:
        out["warning"] = "rating block not found: page layout changed, bot wall, or no such store"
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
