"""Parse the 2026 governor races table ("Race summary / States") from the Wikipedia article."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

from parse_house import AYE_RE, clean, party_code

# governorships not on the 2026 ballot, from the article's partisan composition: 26 R and 24 D before,
# 18 R and 18 D up in 2026
NOT_UP = {"D": 6, "R": 8}


def parse(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf8")
    sec = text[text.index("=== States ==="):text.index("=== Territories and federal district ===")]
    rows = []
    for blk in re.split(r"\n\|-", sec)[1:]:
        m = re.search(r"^!\s*\[\[[^|\]]+\|([^\]]+)\]\]", blk.strip(), re.M)
        if not m:
            continue
        inc = re.search(r"\{\{sortname\|[^}]*\}\}", blk)
        inc_party = re.search(r"\{\{party shading/(?:Text/)?([^}|/]+)\}\}", blk, re.I)
        winner = winner_party = None
        for line in blk.splitlines():
            mm = AYE_RE.search(line)
            if mm:
                winner, winner_party = clean(mm.group(1)), party_code(mm.group(2))
                break
        rows.append(dict(state=clean(m.group(1)), incumbent=clean(inc.group(0)) if inc else None,
                         incumbent_party=party_code(inc_party.group(1)) if inc_party else None,
                         winner=winner, winner_party=winner_party, called=winner is not None))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = parse(Path(sys.argv[1]))
    print(len(df)); print(df.incumbent_party.value_counts(dropna=False).to_dict(), df.winner_party.value_counts(dropna=False).to_dict())
    print(df[~df.called | (df.incumbent_party != df.winner_party)].to_string())
