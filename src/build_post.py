"""Write the LinkedIn post drafts (Portuguese and English) from the same numbers as the page."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, PUB = ROOT / "Data" / "processed", ROOT / "publication"
PAGE = "https://jeffairdata.github.io/usa-congress-elections-2024-2026/"
CODE = "https://github.com/JeffAirData/usa-congress-elections-2024-2026"


def main() -> None:
    s = json.loads((DATA / "summary_2026.json").read_text(encoding="utf8"))
    g = pd.read_csv(DATA / "house_groups_2024_2026.csv").set_index("group")
    mid = pd.read_csv(DATA / "midterm_president_party_change.csv")
    worst = mid.loc[mid.change.idxmin()]
    h24, h26, w = s["house_2024"], s["house_2026"], s["women"]
    lo, hi = h24["R"] - h26["R"] - h26["open"], h24["R"] - h26["R"]
    PUB.mkdir(exist_ok=True)
    (PUB / "post_pt.md").write_text(f"""Imagens: `docs/pt/img/01_nacional.png` a `07_mulheres_partido.png` (carrossel).

---

Dois dias depois das eleições de meio de mandato nos EUA, os Democratas já têm maioria na Câmara, no Senado e entre os governadores.

Comparei 2026 com a eleição de 2024 e com a série histórica. Os números de 2026 ainda são parciais, servem para comparar:

- Câmara: {h24['D']} D x {h24['R']} R em 2024; agora {h26['D']} D x {h26['R']} R, com {h26['open']} cadeiras em aberto.
- Senado: {s['senate_before']['D']} D x {s['senate_before']['R']} R antes; agora {s['senate_2026']['D']} D x {s['senate_2026']['R']} R, com {s['senate_2026']['open']} em aberto.
- Governadores: {s['gov_before']['D']} D x {s['gov_before']['R']} R antes; agora {s['gov_2026']['D']} D x {s['gov_2026']['R']} R, com {s['gov_2026']['open']} em aberto.
- O partido do presidente quase sempre perde cadeiras no meio do mandato. A maior perda desde 1946 foi de {-int(worst.change)} cadeiras, em {int(worst.year)}. Os Republicanos perdem agora entre {lo} e {hi}.

Na representação:
- Mulheres na Câmara: {g.loc['women','elected_2024']} eleitas em 2024 e pelo menos {g.loc['women','at_least_2026']} em 2026. As democratas foram de {w['D_2024']} para {w['D_2026']}; as republicanas, de {w['R_2024']} para {w['R_2026']}.
- Hispânicos: de {g.loc['hispanic','elected_2024']} para pelo menos {g.loc['hispanic','at_least_2026']}. Indígenas: de {g.loc['native','elected_2024']} para {g.loc['native','at_least_2026']} na Câmara, e Peggy Flanagan será a primeira mulher indígena eleita senadora.
- LGBTQ+: de {g.loc['lgbtq','elected_2024']} para pelo menos {g.loc['lgbtq','at_least_2026']} na Câmara; Chris Pappas é o primeiro homem abertamente gay eleito senador.

Escolha um estado e veja cada distrito, 2024 x 2026:
{PAGE}pt/

Azul é Democrata, vermelho é Republicano. Nenhum resultado em aberto foi estimado.

Código e dados: {CODE}

#Eleições2026 #EUA #DadosAbertos #DataScience
""", encoding="utf8")
    (PUB / "post_en.md").write_text(f"""Images: `docs/img/01_nacional.png` to `07_mulheres_partido.png` (carousel).

---

Two days after the U.S. midterms, Democrats already hold a majority in the House, the Senate and the governorships.

I compared 2026 with the 2024 election and with the historical series. The 2026 numbers are still provisional, for comparison:

- House: {h24['D']} D vs {h24['R']} R in 2024; now {h26['D']} D vs {h26['R']} R, with {h26['open']} seats uncalled.
- Senate: {s['senate_before']['D']} D vs {s['senate_before']['R']} R before; now {s['senate_2026']['D']} D vs {s['senate_2026']['R']} R, with {s['senate_2026']['open']} uncalled.
- Governors: {s['gov_before']['D']} D vs {s['gov_before']['R']} R before; now {s['gov_2026']['D']} D vs {s['gov_2026']['R']} R, with {s['gov_2026']['open']} uncalled.
- The president's party almost always loses seats in a midterm. The biggest loss since 1946 was {-int(worst.change)} seats, in {int(worst.year)}. Republicans now lose between {lo} and {hi}.

Representation:
- Women in the House: {g.loc['women','elected_2024']} elected in 2024 and at least {g.loc['women','at_least_2026']} in 2026. Democratic women went from {w['D_2024']} to {w['D_2026']}; Republican women from {w['R_2024']} to {w['R_2026']}.
- Hispanic Americans: from {g.loc['hispanic','elected_2024']} to at least {g.loc['hispanic','at_least_2026']}. Native Americans: from {g.loc['native','elected_2024']} to {g.loc['native','at_least_2026']} in the House, and Peggy Flanagan will be the first Native American woman elected senator.
- LGBTQ+: from {g.loc['lgbtq','elected_2024']} to at least {g.loc['lgbtq','at_least_2026']} in the House; Chris Pappas is the first openly gay man elected senator.

Pick a state and see every district, 2024 vs 2026:
{PAGE}

Blue is Democratic, red is Republican. No uncalled race was estimated.

Code and data: {CODE}

#Midterms2026 #USPolitics #OpenData #DataScience
""", encoding="utf8")
    print("wrote publication/post_pt.md and post_en.md")


if __name__ == "__main__":
    main()
