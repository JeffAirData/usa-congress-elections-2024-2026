"""Download every raw source into Data/raw. Re-run it to refresh the 2026 results as more races are called.

Wikipedia pages are fetched as raw wikitext (action=raw); their revision changes as editors add AP and state calls.
"""
from __future__ import annotations

import time
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "Data" / "raw"
UA = {"User-Agent": "JeffAirData-research/1.0 (github.com/JeffAirData)"}
WIKI = "https://en.wikipedia.org/w/index.php?action=raw&redirect=yes&title="
HH = "https://history.house.gov/"
SOURCES = {
    "2024_United_States_House_of_Representatives_elections.wiki": WIKI + "2024_United_States_House_of_Representatives_elections",
    "2026_United_States_House_of_Representatives_elections.wiki": WIKI + "2026_United_States_House_of_Representatives_elections",
    "2026_United_States_Senate_elections.wiki": WIKI + "2026_United_States_Senate_elections",
    "2026_United_States_gubernatorial_elections.wiki": WIKI + "2026_United_States_gubernatorial_elections",
    "w_List_of_LGBTQ_members_of_the_United_States_Congress.wiki": WIKI + "List_of_LGBTQ_members_of_the_United_States_Congress",
    "w_List_of_Native_Americans_in_the_United_States_Congress.wiki": WIKI + "List_of_Native_Americans_in_the_United_States_Congress",
    "w_List_of_Hispanic_and_Latino_Americans_in_the_United_States_Congress.wiki": WIKI + "List_of_Hispanic_and_Latino_Americans_in_the_United_States_Congress",
    "MemberData.xml": "https://clerk.house.gov/xml/lists/MemberData.xml",
    "hh_party_divisions.html": HH + "Institution/Party-Divisions/Party-Divisions/",
    "hh_WIC.html": HH + "Exhibitions-and-Publications/WIC/Historical-Data/Women-Representatives-and-Senators-by-Congress/",
    "hh_BAIC.html": HH + "Exhibitions-and-Publications/BAIC/Historical-Data/Black-American-Representatives-and-Senators-by-Congress/",
    "hh_HAIC.html": HH + "Exhibitions-and-Publications/HAIC/Historical-Data/Hispanic-American-Representatives,-Senators,-Delegates,-and-Resident-Commissioners-by-Congress/",
    "legislators-current.yaml": "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml",
    "legislators-historical.yaml": "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-historical.yaml",
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            (RAW / name).write_bytes(r.read())
        print("ok", name)
        time.sleep(2)  # Wikipedia asks automated clients to go slowly


if __name__ == "__main__":
    main()
