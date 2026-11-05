"""Diversity in the House: the series by Congress and the provisional 2024 x 2026 comparison.

Series (members in office during each Congress, voting members only):
  women, Black and Hispanic: House Historian lists; Native American: Wikipedia list (histograph);
  openly LGBTQ: Wikipedia list (members out while serving).
2026 (provisional): the group's members elected in 2024 who were re-elected, left or whose race is uncalled, plus
first-time winners identified so far. A new member counts only when a source names them; nothing is inferred.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

import parse_lgbtq
from build_dataset import OUT, RAW, same_person
from parse_historian import TERRITORIES

WIKI_NATIVE = RAW / "w_List_of_Native_Americans_in_the_United_States_Congress.wiki"
WIKI_HISP = RAW / "w_List_of_Hispanic_and_Latino_Americans_in_the_United_States_Congress.wiki"
WIKI_LGBTQ = RAW / "w_List_of_LGBTQ_members_of_the_United_States_Congress.wiki"
# first-time 2026 House winners from the groups below that news reports name; each is checked against the results
PRESS_NEW = {
    "lgbtq": [("IN", "J. D. Ford"), ("MI", "Jeremy Moss"), ("AZ", "JoAnna Mendoza"), ("CA", "Marni von Wilpert")],
    "black": [("CO", "Melat Kiros")],
}
PRESS_SOURCES = {
    "lgbtq": "Washington Blade, Advocate e GLAAD (4 e 5/11/2026)",
    "black": "Fast Company e ABC News (4/11/2026)",
}


def native_series() -> pd.DataFrame:
    """Native Americans in the House at the opening of each Congress, from the article's histograph."""
    t = WIKI_NATIVE.read_text(encoding="utf8")
    sec = t[t.index("== House of Representatives =="):]
    sec = sec[sec.index("===Histograph==="):]
    sec = sec[:sec.index("\n|}")]
    pts = [(pd.Timestamp(d.strip()), int(n)) for d, n in re.findall(r"\n\|([A-Z][a-z]+ \d{1,2}, \d{4})\s*\n\|(\d+)", sec)]
    pts.sort()
    rows = []
    for y in range(1907, 2027, 2):
        before = [n for d, n in pts if d <= pd.Timestamp(y, 1, 3)]
        rows.append(dict(start_year=y, House=before[-1] if before else 0))
    return pd.DataFrame(rows)


def elect_section(path: Path, title: str = "===Representatives-elect===") -> list[str]:
    t = path.read_text(encoding="utf8")
    sec = t[t.index(title):]
    sec = sec[:sec.index("\n|}")]
    return [f"{a} {b}" for a, b in re.findall(r"\{\{sortname\|([^|}]+)\|([^|}]+)", sec)]


def main() -> None:
    groups = pd.read_csv(OUT / "members_by_group_and_congress.csv")
    voting = groups[~groups.state.isin(TERRITORIES) & (groups.chamber == "House")]
    series = voting.groupby(["group", "start_year"]).size().rename("House").reset_index()
    nat = native_series().assign(group="native")
    lg = parse_lgbtq.parse(WIKI_LGBTQ)
    lgs = parse_lgbtq.openly_serving(lg, range(1973, 2027, 2))[["start_year", "House"]].assign(group="lgbtq")
    series = pd.concat([series, nat, lgs], ignore_index=True)
    series.to_csv(OUT / "house_group_series.csv", index=False)

    h24 = pd.read_csv(OUT / "house_districts_2024.csv")
    h26 = pd.read_csv(OUT / "house_districts_2026.csv")
    status = pd.read_csv(OUT / "group_members_119_status_2026.csv")
    gender = pd.read_csv(OUT / "house_winners_2026_gender.csv")
    rows = []
    for g in ["women", "black", "hispanic"]:
        mem = groups[(groups.group == g) & (groups.congress == 119) & (groups.chamber == "House")]
        e24 = sum(any(st == s and same_person(n, w) for s, n in zip(mem.state, mem.name)) for st, w in zip(h24.state, h24.winner))
        stt = status[status.group == g].status_2026.value_counts()
        if g == "women":
            new = gender[(gender.gender == "F") & gender.new_member]
            new_names, src = list(new.winner), "pronomes nos artigos da Wikipedia de cada novata"
        elif g == "hispanic":
            elect = elect_section(WIKI_HISP)
            new_names = [w for w in h26[h26.called].winner if any(w.replace("í", "i") == e.replace("í", "i") for e in elect)]
            src = "Wikipedia, lista de hispânicos no Congresso (seção de eleitos)"
        else:
            new_names = [n for s, n in PRESS_NEW["black"] if ((h26.state == s) & (h26.winner == n)).any()]
            src = PRESS_SOURCES["black"]
        rows.append(dict(group=g, elected_2024=e24, reelected=int(stt.get("re-elected", 0)),
                         left=int(stt.get("left the House", 0)), uncalled=int(stt.get("race uncalled", 0)),
                         new_identified=len(new_names), new_names="; ".join(new_names), new_source=src))
    # LGBTQ and Native American: members in the House on January 3, 2025, then their 2026 outcome
    lg_house = lg[(lg.chamber == "House") & ~lg.came_out_after & ~lg.posthumous & (lg.end == 9999)]
    nat_names = [("OK", "Tom Cole"), ("KS", "Sharice Davids"), ("OK", "Josh Brecheen")]
    for g, people, new in [("lgbtq", list(lg_house.name), [n for s, n in PRESS_NEW["lgbtq"]]),
                           ("native", [n for _, n in nat_names], [n for n in elect_section(WIKI_NATIVE) if (h26.winner == n).any()])]:
        re_el = [p for p in people if (h26.winner == p).any()]
        unc = [p for p in people if not (h26.winner == p).any() and h26[~h26.called].incumbents.fillna("").str.contains(p).any()]
        new = [n for n in new if (h26.winner == n).any()]
        rows.append(dict(group=g, elected_2024=12 if g == "lgbtq" else 3, reelected=len(re_el),
                         left=len(people) - len(re_el) - len(unc), uncalled=len(unc), new_identified=len(new),
                         new_names="; ".join(new),
                         new_source=PRESS_SOURCES["lgbtq"] if g == "lgbtq" else "Wikipedia, lista de indígenas no Congresso (seção de eleitos)"))
    out = pd.DataFrame(rows)
    # women: every called winner has a gender (or "unknown"), so count them directly rather than by matching names
    w = out.group == "women"
    out.loc[w, "reelected"] = int(((gender.gender == "F") & ~gender.new_member).sum())
    out.loc[w, "unknown_gender_winners"] = int(gender.gender.isna().sum())
    out["at_least_2026"] = out.reelected + out.new_identified
    out.to_csv(OUT / "house_groups_2024_2026.csv", index=False)
    print(out.drop(columns=["new_names", "new_source"]).to_string())


if __name__ == "__main__":
    main()
