"""Build every processed table from the raw files in Data/raw.

House 2024 x 2026 by district and by state; Senate 2026; the official party division of the House for each
Congress; members of Congress by group (women, Black, Hispanic) for each Congress; and the 2026 status of
the members of those groups. 2026 results are provisional: a race is "called" only when the source marks a winner.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd

import parse_historian
import parse_house
import parse_senate

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "Data" / "raw", ROOT / "Data" / "processed"
WIKI_2024 = RAW / "2024_United_States_House_of_Representatives_elections.wiki"
WIKI_2026 = RAW / "2026_United_States_House_of_Representatives_elections.wiki"
WIKI_SEN = RAW / "2026_United_States_Senate_elections.wiki"
# Senate seats not up in 2026 (classes 1 and 3 minus the Florida and Ohio specials); independents caucus with Democrats
SENATE_NOT_UP = {"D": 34, "R": 31}
STATE_NAMES = dict(zip(sorted(parse_house.SEATS), [None] * 50))


def party_divisions() -> pd.DataFrame:
    """Official House party division at the start of each Congress (House Historian)."""
    t = (RAW / "hh_party_divisions.html").read_text(encoding="utf8", errors="ignore")
    tx = html.unescape(re.sub(r"<[^>]+>", "|", t))
    tx = re.sub(r"\s*\|[\s|]*", "|", tx)
    rows = []
    for m in re.finditer(r"\|(\d+)(?:st|nd|rd|th) \((\d{4})[–-](\d{4})\)\|(\d{3})\|(?:(\d)\|)?(\d+)\|(\d+)\|", tx):
        c, y0, _, seats, _, d, r = m.groups()
        rows.append(dict(congress=int(c), start_year=int(y0), election=int(y0) - 1, seats=int(seats), D=int(d), R=int(r)))
    df = pd.DataFrame(rows).drop_duplicates("congress")
    df = df[df.congress >= 63]  # the 435-seat era begins with the 63rd Congress (1913)
    df["midterm"] = df.election % 4 == 2
    return df.reset_index(drop=True)


def norm(s: str) -> str:
    import unicodedata
    s = re.sub(r"<sup>.*?</sup>|\b(Jr|Sr|II|III|IV)\b\.?", "", s)
    return re.sub(r"[^A-Z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper())


def given_initials(historian_name: str) -> set[str]:
    """Initials of every given name and nickname: 'TITUS, Alice Costandina (Dina)' -> {'A', 'C', 'D'}."""
    rest = re.sub(r"<sup>.*?</sup>", "", historian_name.split(",", 1)[1] if "," in historian_name else historian_name)
    return {norm(w)[:1] for w in re.split(r"[\s()]+", rest) if norm(w)}


# nicknames used on the ballot whose initial differs from the legal first name
NICKNAMES = {"LIZZIE": "E", "BOBBY": "R", "CHUY": "J", "BETSY": "E"}


def same_person(historian_name: str, full_name: str) -> bool:
    """Historian 'TORRES, Norma Judith' vs 'Norma Torres': same surname at the end, same first initial."""
    n = norm(full_name)
    first = norm(full_name.split()[0]) if full_name else ""
    initial = NICKNAMES.get(first, first[:1])
    return bool(full_name) and n.endswith(surname(historian_name)) and (initial in given_initials(historian_name) or first[:1] in given_initials(historian_name))


def surname(historian_name: str) -> str:
    """'WASSERMAN SCHULTZ, Debbie' -> 'WASSERMANSCHULTZ' (the Historian writes surnames first)."""
    return norm(historian_name.split(",")[0])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    h24, h26 = parse_house.parse(WIKI_2024), parse_house.parse(WIKI_2026)
    h24.to_csv(OUT / "house_districts_2024.csv", index=False)
    h26.to_csv(OUT / "house_districts_2026.csv", index=False)

    s24 = h24.pivot_table(index="state", columns="winner_party", values="district", aggfunc="count", fill_value=0)
    s26 = h26.assign(winner_party=h26.winner_party.fillna("uncalled")).pivot_table(
        index="state", columns="winner_party", values="district", aggfunc="count", fill_value=0)
    st = pd.DataFrame({"seats": pd.Series(parse_house.SEATS)})
    st["D_2024"], st["R_2024"] = s24.get("D", 0), s24.get("R", 0)
    st["D_2026"], st["R_2026"], st["uncalled_2026"] = s26.get("D", 0), s26.get("R", 0), s26.get("uncalled", 0)
    st = st.fillna(0).astype(int)
    st["D_change"] = st.D_2026 - st.D_2024
    st["R_change"] = st.R_2026 - st.R_2024
    st.index.name = "state"
    st.to_csv(OUT / "house_states_2024_2026.csv")

    sen = parse_senate.parse(WIKI_SEN)
    sen.to_csv(OUT / "senate_races_2026.csv", index=False)

    pdv = party_divisions()
    pdv.to_csv(OUT / "house_party_divisions.csv", index=False)

    groups = pd.concat([parse_historian.parse(RAW / f"hh_{f}.html", g)
                        for g, f in [("women", "WIC"), ("black", "BAIC"), ("hispanic", "HAIC")]], ignore_index=True)
    groups.to_csv(OUT / "members_by_group_and_congress.csv", index=False)
    counts = (groups.assign(voting=~groups.state.isin(parse_historian.TERRITORIES))
              .groupby(["group", "congress", "start_year", "chamber"]).size().unstack("chamber", fill_value=0).reset_index())
    counts.to_csv(OUT / "group_counts_by_congress.csv", index=False)

    # 2026 status of every House member of the 119th Congress who belongs to a group
    g119 = groups[(groups.congress == 119) & (groups.chamber == "House") & ~groups.state.isin(parse_historian.TERRITORIES)].copy()
    g119["key"] = g119.name.map(surname)
    status = []
    for _, r in g119.iterrows():
        here = h26[h26.state == r.state]
        won = here[here.winner.fillna("").map(lambda w: same_person(r["name"], w))]
        mine = here[here.incumbents.fillna("").map(lambda s: any(same_person(r["name"], x) for x in s.split("; ") if x))]
        if len(won):
            s = "re-elected"
        elif len(mine) and (mine.called.all() or mine.notes.str.contains("retired|lost|resigned|died", case=False).all()):
            s = "left the House"
        elif len(mine):
            s = "race uncalled"
        else:
            s = "left the House"  # not on the 2026 ballot for the House: resigned, died or ran for another office
        status.append(s)
    g119["status_2026"] = status
    g119["name"] = g119.name.str.replace(r"\s*<sup>.*?</sup>", "", regex=True)
    g119.drop(columns="key").to_csv(OUT / "group_members_119_status_2026.csv", index=False)
    print(g119.groupby(["group", "status_2026"]).size().to_string())


if __name__ == "__main__":
    main()


def pronoun_gender(path: Path) -> str | None:
    """'F' or 'M' from the pronouns of a Wikipedia article's prose; None when they do not clearly agree."""
    if not path.exists():
        return None
    t = path.read_text(encoding="utf8", errors="ignore")
    t = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"\{\{[^{}]*\}\}", " ", re.sub(r"\{\{[^{}]*\}\}", " ", t))
    f = len(re.findall(r"\b(she|her|hers|herself)\b", t, re.I))
    m = len(re.findall(r"\b(he|his|him|himself)\b", t, re.I))
    if f >= 3 and f >= 3 * max(m, 1):
        return "F"
    if m >= 3 and m >= 3 * max(f, 1):
        return "M"
    return None


def winners_gender() -> pd.DataFrame:
    """Gender of every called 2026 House winner: the Clerk's courtesy title for current members, pronouns otherwise."""
    from download_winner_pages import CACHE, current_members, norm as norm2
    h = pd.read_csv(OUT / "house_districts_2026.csv")
    cur = current_members()
    out = []
    for _, r in h[h.called].iterrows():
        known = cur[(cur.state == r.state) & cur.lastname.map(norm2).map(lambda k: norm2(r.winner).endswith(k))]
        if len(known):
            g, how = ("M" if known.iloc[0].courtesy == "Mr." else "F"), "Clerk courtesy title"
        else:
            f = CACHE / (re.sub(r"[^\w]+", "_", r.winner_link) + ".wiki") if isinstance(r.winner_link, str) else Path("/nonexistent")
            g, how = pronoun_gender(f), "pronouns in Wikipedia article"
        out.append(dict(state=r.state, district=r.district, winner=r.winner, winner_party=r.winner_party,
                        gender=g, method=how, new_member=not len(known)))
    return pd.DataFrame(out)


def women_2024() -> pd.DataFrame:
    """Women among the 435 House winners of November 2024 (Historian's 119th-Congress list, matched by state and surname)."""
    h = pd.read_csv(OUT / "house_districts_2024.csv")
    w = pd.read_csv(OUT / "members_by_group_and_congress.csv")
    w = w[(w.group == "women") & (w.congress == 119) & (w.chamber == "House")]
    keys = set(zip(w.state, w.name.map(surname)))
    h["woman"] = [any(st == s and same_person(n, win) for s, n in zip(w.state, w.name)) for st, win in zip(h.state, h.winner)]
    return h


if __name__ == "__main__" and "gender" in __import__("sys").argv:
    g = winners_gender()
    g.to_csv(OUT / "house_winners_2026_gender.csv", index=False)
    print(g.gender.value_counts(dropna=False).to_string())
    print(g[g.gender.isna()].to_string())
    w24 = women_2024()
    print("women elected 2024:", int(w24.woman.sum()), w24[w24.woman].winner_party.value_counts().to_dict())
    print("women elected 2026:", g[g.gender == "F"].winner_party.value_counts().to_dict(), "new:", int(((g.gender == "F") & g.new_member).sum()))
