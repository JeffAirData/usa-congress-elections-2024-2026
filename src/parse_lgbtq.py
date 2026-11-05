"""Parse Wikipedia's "List of LGBTQ members of the United States Congress" into one row per member and term.

Members marked "came out after serving" (dagger) or "posthumously identified" (double dagger) are flagged, so
the series of openly LGBTQ members in office can leave them out.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from parse_house import clean


def parse(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf8")
    rows = []
    for chamber, head in (("Senate", "==Senate=="), ("House", "==House of Representatives==")):
        sec = text[text.index(head):]
        sec = sec[:sec.index("\n|}")]
        for blk in re.split(r"\n\|-", sec):
            name = re.search(r"\{\{sortname\|[^}]*\}\}", blk)
            if not name:
                continue
            dates = re.findall(r"\{\{dts\|(\d{4})\|(\d{1,2})\|(\d{1,2})", blk)
            if not dates:
                continue
            start = int(dates[0][0])
            end = 9999 if re.search(r"^\|\s*(?:rowspan=\d+\s*\|)?\s*Incumbent\s*$", blk, re.M) else int(dates[1][0]) if len(dates) > 1 else None
            party = "D" if "Democratic Party (United States)|" in blk else "R" if "Republican Party (United States)|" in blk else "O"
            rows.append(dict(chamber=chamber, name=clean(name.group(0)), party=party, start=start, end=end,
                             came_out_after="{{dagger}}" in blk, posthumous="{{double-dagger}}" in blk))
    return pd.DataFrame(rows)


def openly_serving(df: pd.DataFrame, years) -> pd.DataFrame:
    """Openly LGBTQ members in office at the opening of the Congress that starts in each year."""
    ok = df[~df.came_out_after & ~df.posthumous]
    return pd.DataFrame([dict(start_year=y, congress=(y - 1789) // 2 + 1,
                              House=int(((ok.chamber == "House") & (ok.start <= y) & (ok.end > y)).sum()),
                              Senate=int(((ok.chamber == "Senate") & (ok.start <= y) & (ok.end > y)).sum()))
                         for y in years])


if __name__ == "__main__":
    df = parse(Path("Data/raw/w_List_of_LGBTQ_members_of_the_United_States_Congress.wiki"))
    print(len(df), df.chamber.value_counts().to_dict())
    print(openly_serving(df, range(1973, 2027, 2)).to_string())
    print(df[df.end == 9999].to_string())
