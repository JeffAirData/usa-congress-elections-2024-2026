"""Parse the House Historian's "Members by Congress" tables (women, Black Americans, Hispanic Americans).

Each row: congress number, name, state, party, chamber. The Historian lists everyone who served at any point
during a Congress, delegates and resident commissioners included; TERRITORIES lets callers drop them.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd

TERRITORIES = {"DC", "PR", "GU", "VI", "AS", "MP", "PI", "DK", "HI-T", "AK-T"}
ROW_RE = re.compile(
    r"<tr class=\"(?:odd|even)\">\s*<td>\s*(\d+)(?:st|nd|rd|th)\s*\((\d{4})-(\d{4})\)\s*</td>\s*"
    r"<td>\s*<a href=\"/People/Detail/(\d+)\">\s*(.*?)\s*</a>\s*</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>",
    re.S)


def parse(path: Path, group: str) -> pd.DataFrame:
    text = path.read_text(encoding="utf8", errors="ignore")
    rows = [dict(group=group, congress=int(c), start_year=int(y0), person_id=pid, name=html.unescape(re.sub(r"\s+", " ", n)),
                 state=st.strip(), party=pa.strip(), chamber=ch.strip())
            for c, y0, _, pid, n, st, pa, ch in ROW_RE.findall(text)]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for g, f in [("women", "WIC"), ("black", "BAIC"), ("hispanic", "HAIC")]:
        df = parse(Path(f"Data/raw/hh_{f}.html"), g)
        last = df[df.congress == 119]
        print(g, len(df), "rows; 119th:", last.chamber.value_counts().to_dict(), "first:", df.congress.min())
