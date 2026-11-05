"""Download the Wikipedia article (raw wikitext) of each 2026 House winner who is not a current member.

Used only to read the pronouns of first-time winners (she/her or he/his), so women elected for the first time
in 2026 can be counted before any official tally exists. Pages are cached in Data/raw/winners/.
"""
from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "Data" / "raw"
CACHE = RAW / "winners"
UA = "JeffAirData-research/1.0 (github.com/JeffAirData)"


def norm(s: str) -> str:
    import unicodedata
    s = re.sub(r"\b(Jr|Sr|II|III|IV)\b\.?", "", s or "")
    return re.sub(r"[^A-Z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper())


def current_members() -> pd.DataFrame:
    t = (RAW / "MemberData.xml").read_text(encoding="utf8")
    rows = []
    for m in re.finditer(r"<member>.*?</member>", t, re.S):
        b = m.group(0)
        g = lambda tag: (re.search(fr"<{tag}>(.*?)</{tag}>", b) or [None, ""])[1]
        if not g("lastname"):
            continue  # vacant seat
        rows.append(dict(state=b[b.index("<statedistrict>") + 15:][:2], lastname=g("lastname"), firstname=g("firstname"),
                         courtesy=g("courtesy"), party=g("party")))
    return pd.DataFrame(rows)


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    h = pd.read_csv(ROOT / "Data" / "processed" / "house_districts_2026.csv")
    cur = current_members()
    for _, r in h[h.called].iterrows():
        known = cur[(cur.state == r.state) & cur.lastname.map(norm).map(lambda k: norm(r.winner).endswith(k))]
        if len(known) or not isinstance(r.winner_link, str):
            continue
        f = CACHE / (re.sub(r"[^\w]+", "_", r.winner_link) + ".wiki")
        if f.exists():
            continue
        url = "https://en.wikipedia.org/w/index.php?" + urllib.parse.urlencode({"title": r.winner_link, "action": "raw", "redirect": "yes"})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as resp:
                f.write_bytes(resp.read())
        except Exception as e:  # a missing article stays missing; the build reports it as unknown
            print("no page:", r.winner_link, e)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
