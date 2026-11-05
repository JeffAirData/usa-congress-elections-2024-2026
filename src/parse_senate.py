"""Parse the 2026 Senate races table ("Elections leading to the next Congress") from the Wikipedia article."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

from parse_house import AYE_RE, clean, party_code


SECTIONS = ("=== Elections leading to the next Congress ===", "=== Special elections during the preceding Congress ===")


def parse(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf8")
    return pd.concat([parse_section(text, s) for s in SECTIONS], ignore_index=True)


def parse_section(text: str, title: str) -> pd.DataFrame:
    sec = text[text.index(title):]
    sec = sec[:sec.index("\n|}")]
    rows = []
    for blk in re.split(r"\n\|-", sec)[1:]:
        m = re.search(r"^!\s*\[\[[^|\]]+\|([^\]]+)\]\]", blk.strip(), re.M)
        if not m:
            continue
        if "Shading PVI" not in blk:  # header rows
            continue
        inc = re.search(r"\{\{sortname\|[^}]*\}\}|^\|\s*\[\[[^\]]+\]\]\s*$", blk, re.M)
        inc_party = re.search(r"\{\{Party shading/(\w+)\}\}\s*\|\s*(\w+)", blk)
        winner = winner_party = None
        for line in blk.splitlines():
            mm = AYE_RE.search(line)
            if mm:
                winner, winner_party = clean(mm.group(1)), party_code(mm.group(2))
                break
        rows.append(dict(race=clean(m.group(1)) + (" (special)" if "special" in title.lower() else ""), incumbent=clean(inc.group(0)) if inc else None,
                         incumbent_party=party_code(inc_party.group(2)) if inc_party else None,
                         winner=winner, winner_party=winner_party, called=winner is not None))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = parse(Path(sys.argv[1]))
    print(df.to_string())
