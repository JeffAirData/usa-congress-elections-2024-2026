"""House seats per party at the opening of each Congress, from the unitedstates/congress-legislators dataset.

A member counts for a Congress when one of their House terms starts on or within 60 days of the opening day
(members elected in November and sworn in late still count; later special-election winners do not).
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from pathlib import Path

import pandas as pd
import yaml

RAW = Path(__file__).resolve().parent.parent / "Data" / "raw"
TERRITORIES = {"DC", "PR", "GU", "VI", "AS", "MP"}
# the party of the president in office during each midterm (election year -> party)
MIDTERM_PRESIDENT = {1946: "D", 1950: "D", 1954: "R", 1958: "R", 1962: "D", 1966: "D", 1970: "R", 1974: "R",
                     1978: "D", 1982: "R", 1986: "R", 1990: "R", 1994: "D", 1998: "D", 2002: "R", 2006: "R",
                     2010: "D", 2014: "D", 2018: "R", 2022: "D", 2026: "R"}
PARTY = {"Democrat": "D", "Republican": "R"}


def load_people() -> list[dict]:
    people = []
    for f in ("legislators-historical.yaml", "legislators-current.yaml"):
        people += yaml.load((RAW / f).read_text(encoding="utf8"), Loader=yaml.CLoader)
    return people


def opening(year: int) -> dt.date:
    """Opening day of the Congress elected in `year` (January 3 since 1935)."""
    return dt.date(year + 1, 1, 3)


def seats_by_election(years) -> pd.DataFrame:
    people = load_people()
    rows = []
    for y in years:
        o = opening(y)
        c = Counter()
        for p in people:
            for t in p["terms"]:
                if t["type"] != "rep" or t["state"] in TERRITORIES:
                    continue
                s = dt.date.fromisoformat(t["start"])
                if o - dt.timedelta(days=3) <= s <= o + dt.timedelta(days=60):
                    c[PARTY.get(t.get("party"), "O")] += 1
                    break
        rows.append(dict(election=y, D=c["D"], R=c["R"], other=c["O"], seated=sum(c.values())))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = seats_by_election(range(1944, 2025, 2))
    print(df.to_string())
