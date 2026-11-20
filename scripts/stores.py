#!/usr/bin/env python3
"""Query the Israeli store roster (Israel-Online-Stores stores-index.json + the user's overlay). Prints JSON.

Usage:
  python3 scripts/stores.py --category pro_audio                 # specialists first
  python3 scripts/stores.py --category computers --city ירושלים
  python3 scripts/stores.py --find "kzpro"                       # name / domain / description match
  python3 scripts/stores.py --categories                         # tag vocabulary with counts

Sources, merged (user entries win on the same domain):
  1. https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores-index.json
     (cached 24 h under <plugin-data-dir>/cache/)
  2. <plugin-data-dir>/user-stores.json, same slim shape:
     {"name","website","domain","categories":[],"is_tech","city_he","description_he","zap_siteid"}
<plugin-data-dir> = $CLAUDE_USER_DATA/israel-shopping, else $XDG_DATA_HOME/claude-plugins/israel-shopping,
else ~/.local/share/claude-plugins/israel-shopping.

Ranking for --category: stores whose description names the product come first, then by fewest tags
(facet-tagged generalists can carry 20+ tags), then by Zap siteid presence.
"""
import argparse
import collections
import json
import os
import time
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores-index.json"


def data_dir():
    if os.environ.get("CLAUDE_USER_DATA"):
        return Path(os.environ["CLAUDE_USER_DATA"]) / "israel-shopping"
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "claude-plugins" / "israel-shopping"


def load():
    cache = data_dir() / "cache" / "stores-index.json"
    if not cache.exists() or time.time() - cache.stat().st_mtime > 86400:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=60) as r:
            cache.write_bytes(r.read())
    stores = {(s.get("domain") or s["name"]).lower(): s for s in json.loads(cache.read_text())}
    user = data_dir() / "user-stores.json"
    if user.exists():
        for s in json.loads(user.read_text()):
            s["source"] = "user"
            stores[(s.get("domain") or s["name"]).lower()] = s
    return [s for s in stores.values() if not s.get("status")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category")
    ap.add_argument("--city")
    ap.add_argument("--find")
    ap.add_argument("--categories", action="store_true")
    ap.add_argument("--limit", type=int, default=15)
    a = ap.parse_args()
    st = load()
    if a.categories:
        print(json.dumps(collections.Counter(t for s in st for t in s.get("categories") or []).most_common(), ensure_ascii=False))
        return
    if a.find:
        q = a.find.lower()
        st = [s for s in st if q in " ".join(str(s.get(k) or "") for k in ("name", "domain", "description_he", "description_en")).lower()]
    if a.category:
        st = [s for s in st if a.category in (s.get("categories") or [])]
        st.sort(key=lambda s: (len(s.get("categories") or []), s.get("zap_siteid") is None))
    if a.city:
        st = [s for s in st if a.city in (s.get("city_he") or "") or a.city in (s.get("description_he") or "")]
    keep = ("name", "website", "domain", "categories", "city_he", "description_he", "zap_url", "source")
    print(json.dumps([{k: s.get(k) for k in keep if s.get(k)} for s in st[: a.limit]], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
