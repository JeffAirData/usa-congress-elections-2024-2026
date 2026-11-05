"""Parse the district-by-district House tables of a Wikipedia election article (raw wikitext).

One row per district: state, district, the outgoing member(s) and their party, the winner and party,
and the article's own label (Democratic gain, Republican hold, ...). A race counts as called only when
the article marks a winner with {{aye}}; every other race is left uncalled, never guessed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
          "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
          "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
          "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
          "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
# seats per state from the 2020 census apportionment, used in 2022, 2024 and 2026
SEATS = {"AL": 7, "AK": 1, "AZ": 9, "AR": 4, "CA": 52, "CO": 8, "CT": 5, "DE": 1, "FL": 28, "GA": 14, "HI": 2, "ID": 2,
         "IL": 17, "IN": 9, "IA": 4, "KS": 4, "KY": 6, "LA": 6, "ME": 2, "MD": 8, "MA": 9, "MI": 13, "MN": 8, "MS": 4,
         "MO": 8, "MT": 2, "NE": 3, "NV": 4, "NH": 2, "NJ": 12, "NM": 3, "NY": 26, "NC": 14, "ND": 1, "OH": 15, "OK": 5,
         "OR": 6, "PA": 17, "RI": 2, "SC": 7, "SD": 1, "TN": 9, "TX": 38, "UT": 4, "VT": 1, "VA": 11, "WA": 10, "WV": 2,
         "WI": 8, "WY": 1}
DIST_RE = re.compile(r"^!.*?\{\{ushr\|([A-Z]{2})\|([A-Za-z0-9]+)\|X\}\}", re.M)
AYE_RE = re.compile(r"\{\{aye\}\}\s*(.*?)\s*\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*(?:[\d.,]+\s*%)?\s*$", re.I)


def clean(s: str) -> str:
    s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{sortname\|([^|}]+)\|([^|}]+)[^}]*\}\}", r"\1 \2", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"'''?|<br\s*/?>", " ", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    return re.sub(r"\s+", " ", s).strip(" |")


def party_code(txt: str) -> str | None:
    t = txt.lower()
    if "democratic" in t or "dfl" in t:
        return "D"
    if "republican" in t:
        return "R"
    if "independent" in t:
        return "I"
    if "libertarian" in t:
        return "L"
    return None


def parse(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf8")
    heads = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^==\s*([^=].*?)\s*==\s*$", text, flags=re.M)]
    rows = []
    for i, (pos, name) in enumerate(heads):
        if name not in STATES:
            continue
        sec = text[pos:heads[i + 1][0] if i + 1 < len(heads) else len(text)]
        marks = list(DIST_RE.finditer(sec))
        for j, m in enumerate(marks):
            if j + 1 < len(marks):
                blk = sec[m.start():marks[j + 1].start()]
            else:  # the last district ends where its table closes
                blk = sec[m.start():].split("\n|}", 1)[0]
            st, dist = m.group(1), m.group(2)
            members = [clean(x) for x in re.findall(r"\{\{sortname\|[^}]*\}\}", blk)]
            new_seat = bool(re.search(r"None\s*\{\{small\|\(new seat\)\}\}", blk, re.I))
            party_cells = re.findall(r"^\|\s*style=\"[^\"]*background-color:#(?:B0CEFF|FFB6B6|DCDCDC)[^\"]*\"\s*\|\s*([^\n]+)$", blk, re.M)
            party_cells += re.findall(r"^\|\s*\{\{party shading/Text/(\w+)\}\}", blk, re.M | re.I)
            inc_parties = [party_code(p) for p in party_cells]
            winner = winner_party = winner_link = None
            for line in blk.splitlines():
                mm = AYE_RE.search(line)
                if mm:
                    winner, winner_party = clean(mm.group(1)), party_code(mm.group(2)) or clean(mm.group(2))
                    lk = re.search(r"\[\[([^|\]]+)", mm.group(1))
                    winner_link = lk.group(1).strip() if lk else None
                    break
            notes = " | ".join(clean(x) for x in re.findall(r"((?:Incumbent|New member|Member)[^\n]*?)(?:<br|\n|$)", blk))
            label = re.search(r"(Democratic|Republican|Independent)\s+(gain|hold)", blk)
            rows.append(dict(state=st, district=("AL" if dist in ("AL", "0") else int(dist)),
                             incumbents="; ".join(members), incumbent_parties="; ".join(p or "?" for p in inc_parties),
                             notes=notes, new_seat=new_seat, winner=winner, winner_party=winner_party, winner_link=winner_link, called=winner is not None,
                             label=(f"{label.group(1)} {label.group(2)}" if label else None)))
    df = pd.DataFrame(rows)
    counts = df.groupby("state").size()
    bad = {s: (int(counts.get(s, 0)), n) for s, n in SEATS.items() if counts.get(s, 0) != n}
    if bad:
        raise SystemExit(f"districts parsed != apportioned seats: {bad}")
    return df


if __name__ == "__main__":
    df = parse(Path(sys.argv[1]))
    print(len(df), "districts,", int(df.called.sum()), "called")
    print(df.winner_party.value_counts(dropna=False).to_string())
