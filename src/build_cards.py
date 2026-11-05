"""Instagram carousel: 1080x1350 cards (4:5), one big number per card, Portuguese.

Every number comes from Data/processed, the same as the page and the LinkedIn post.
Output: publication/instagram/card_01.png ... and legenda.md (the caption).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "Data" / "processed"
OUT = ROOT / "publication" / "instagram"
PAGE_PT = "https://jeffairdata.github.io/usa-congress-elections-2024-2026/pt/"

DEM, REP, OPEN = "#2a78d6", "#e34948", "#c3c2b7"
INK, INK_2, MUTED, SURFACE, LINE = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#e1e0d9"
plt.rcParams.update({"font.family": ["Inter", "DejaVu Sans"], "text.color": INK})
W, H = 10.8, 13.5  # inches at 100 dpi -> 1080x1350


def card(n: int, total: int):
    fig = plt.figure(figsize=(W, H), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1080)
    ax.set_ylim(0, 1350)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 1338), 540, 12, boxstyle="square,pad=0", color=DEM))
    ax.add_patch(FancyBboxPatch((540, 1338), 540, 12, boxstyle="square,pad=0", color=REP))
    ax.text(80, 70, "Dados parciais de 5/11/2026 · Wikipedia (AP, DDHQ), House Historian, House Clerk",
            fontsize=15, color=MUTED, va="center")
    ax.text(1000, 70, f"{n}/{total}", fontsize=17, color=MUTED, va="center", ha="right", fontweight="bold")
    return fig, ax


def save(fig, n: int) -> None:
    fig.savefig(OUT / f"card_{n:02d}.png", dpi=100, facecolor=SURFACE)
    plt.close(fig)


def kicker(ax, txt: str, y: float = 1210) -> None:
    ax.text(80, y, txt.upper(), fontsize=22, color=INK_2, fontweight="bold", va="center")


def bar(ax, y: float, d: int, r: int, o: int, total: int, label: str, h: float = 70, faded: bool = False) -> None:
    """One horizontal bar split blue / grey / red, numbers inside."""
    x0, width = 80, 920
    a = 0.45 if faded else 1
    x = x0
    for v, c in ((d, DEM), (o, OPEN), (r, REP)):
        if v:
            w = width * v / total
            ax.add_patch(FancyBboxPatch((x, y), w - 4, h, boxstyle="square,pad=0", color=c, alpha=a))
            if w > 60:
                ax.text(x + w / 2, y + h / 2, str(v), fontsize=30, fontweight="bold", ha="center", va="center",
                        color="white" if c != OPEN else INK)
            x += w
    ax.text(x0, y + h + 22, label, fontsize=20, color=INK_2, va="center")


def big_pair(ax, y: float, before: int, after: int, color: str, label: str, prefix: str = "") -> None:
    ax.text(80, y + 50, label, fontsize=26, color=INK_2, va="center")
    ax.text(80, y - 60, f"{before}", fontsize=96, color=color, alpha=0.45, fontweight="bold", va="center")
    ax.text(330, y - 60, "→", fontsize=80, color=INK_2, va="center")
    ax.text(470, y - 60, f"{prefix}{after}", fontsize=124, color=color, fontweight="bold", va="center")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s = json.loads((DATA / "summary_2026.json").read_text(encoding="utf8"))
    g = pd.read_csv(DATA / "house_groups_2024_2026.csv").set_index("group")
    mid = pd.read_csv(DATA / "midterm_president_party_change.csv")
    worst = mid.loc[mid.change.idxmin()]
    h24, h26, sb, s26, gb, g26, w = (s["house_2024"], s["house_2026"], s["senate_before"], s["senate_2026"],
                                    s["gov_before"], s["gov_2026"], s["women"])
    lo, hi = h24["R"] - h26["R"] - h26["open"], h24["R"] - h26["R"]
    N = 8

    # 1 cover
    fig, ax = card(1, N)
    kicker(ax, "Eleições nos EUA · 3 de novembro de 2026", 1180)
    ax.text(80, 990, "A virada\ndemocrata", fontsize=120, fontweight="bold", va="center", linespacing=0.95)
    ax.text(80, 690, "Câmara, Senado e governadores:\n2024 x 2026, em números", fontsize=40, color=INK_2, va="center",
            linespacing=1.25)
    ax.add_patch(FancyBboxPatch((80, 430), 440, 110, boxstyle="round,pad=0,rounding_size=18", color=DEM))
    ax.add_patch(FancyBboxPatch((560, 430), 440, 110, boxstyle="round,pad=0,rounding_size=18", color=REP))
    ax.text(300, 485, "Democratas", fontsize=36, color="white", fontweight="bold", ha="center", va="center")
    ax.text(780, 485, "Republicanos", fontsize=36, color="white", fontweight="bold", ha="center", va="center")
    ax.text(80, 300, "Resultados parciais, dois dias depois\nda eleição. Arraste para o lado →", fontsize=30,
            color=INK, va="center", linespacing=1.3)
    save(fig, 1)

    # 2-4 chambers
    blocks = [
        (2, "Câmara dos Deputados · 435 cadeiras", h24, h26, 435, "eleição de 2024", 218,
         f"Os Democratas já passaram\ndos 218 da maioria.\n{h26['open']} cadeiras ainda em aberto."),
        (3, "Senado · 100 cadeiras", sb, s26, 100, "antes da eleição", 51,
         f"{len(s['senate_flips_to_D'])} cadeiras viraram para os\nDemocratas, entre elas Texas,\nOhio e Carolina do Norte."),
        (4, "Governadores · 50 estados", gb, g26, 50, "antes da eleição", None,
         f"Viraram para os Democratas:\nGeórgia, Iowa, Nevada,\nOhio e Texas."),
    ]
    for n, title, before, after, total, blabel, maj, note in blocks:
        fig, ax = card(n, N)
        kicker(ax, title)
        ax.text(80, 1060, "Democratas", fontsize=34, color=DEM, fontweight="bold", va="center")
        ax.text(80, 990, f"{before['D']}", fontsize=80, color=DEM, alpha=0.45, fontweight="bold", va="center")
        ax.text(330, 990, "→", fontsize=64, color=INK_2, va="center")
        ax.text(440, 990, f"{after['D']}", fontsize=104, color=DEM, fontweight="bold", va="center")
        ax.text(80, 850, "Republicanos", fontsize=34, color=REP, fontweight="bold", va="center")
        ax.text(80, 780, f"{before['R']}", fontsize=80, color=REP, alpha=0.45, fontweight="bold", va="center")
        ax.text(330, 780, "→", fontsize=64, color=INK_2, va="center")
        ax.text(440, 780, f"{after['R']}", fontsize=104, color=REP, fontweight="bold", va="center")
        bar(ax, 560, before["D"], before["R"], 0, total, blabel, faded=True)
        bar(ax, 420, after["D"], after["R"], after["open"], total, f"2026, parcial · cinza = {after['open']} em aberto")
        if maj:
            x = 80 + 920 * maj / total
            ax.plot([x, x], [400, 650], color=INK, lw=2, ls=(0, (3, 3)))
            ax.text(x + 8, 655, f"maioria: {maj}", fontsize=18, color=INK_2)
        ax.text(80, 240, note, fontsize=32, color=INK, va="center", linespacing=1.3)
        save(fig, n)

    # 5 history
    fig, ax = card(5, N)
    kicker(ax, "A série histórica")
    ax.text(80, 1030, "O partido do presidente\nquase sempre perde\nno meio do mandato", fontsize=50, fontweight="bold",
            va="center", linespacing=1.1)
    ax.text(80, 820, f"Republicanos em 2026: perda de", fontsize=32, color=INK_2, va="center")
    ax.text(80, 700, f"{lo} a {hi}", fontsize=140, color=REP, fontweight="bold", va="center")
    ax.text(80, 590, "cadeiras na Câmara", fontsize=32, color=INK_2, va="center")
    ax.add_patch(FancyBboxPatch((80, 330), 920, 180, boxstyle="round,pad=0,rounding_size=18", color=LINE))
    ax.text(120, 420, f"Maior perda desde 1946:\n{-int(worst.change)} cadeiras, em {int(worst.year)}.\n"
                      f"Se passar disso, é recorde.", fontsize=30, va="center", linespacing=1.3)
    save(fig, 5)

    # 6 women
    fig, ax = card(6, N)
    kicker(ax, "Mulheres na Câmara")
    ax.text(80, 1090, "O total quase não mudou.\nMudou o partido.", fontsize=50, fontweight="bold", va="center", linespacing=1.1)
    ax.text(80, 960, f"{g.loc['women','elected_2024']} eleitas em 2024 · pelo menos {g.loc['women','at_least_2026']} em 2026",
            fontsize=28, color=INK_2, va="center")
    big_pair(ax, 740, w["D_2024"], w["D_2026"], DEM, "Democratas")
    big_pair(ax, 460, w["R_2024"], w["R_2026"], REP, "Republicanas")
    ax.text(80, 210, f"As {g.loc['women','new_identified']} novatas já confirmadas\nsão todas democratas.", fontsize=32,
            va="center", linespacing=1.3)
    save(fig, 6)

    # 7 representation
    fig, ax = card(7, N)
    kicker(ax, "Representação na Câmara")
    rows = [("Hispânicos", g.loc["hispanic", "elected_2024"], f"≥{g.loc['hispanic','at_least_2026']}"),
            ("Indígenas", g.loc["native", "elected_2024"], f"{g.loc['native','at_least_2026']}"),
            ("LGBTQ+ assumidos", g.loc["lgbtq", "elected_2024"], f"≥{g.loc['lgbtq','at_least_2026']}")]
    for i, (lab, a, b) in enumerate(rows):
        y = 1040 - i * 200
        ax.text(80, y + 45, lab, fontsize=30, color=INK_2, va="center")
        ax.text(80, y - 30, f"{a}", fontsize=80, color=INK_2, alpha=0.5, fontweight="bold", va="center")
        ax.text(260, y - 30, "→", fontsize=60, color=INK_2, va="center")
        ax.text(370, y - 30, b, fontsize=96, color=INK, fontweight="bold", va="center")
    ax.add_patch(FancyBboxPatch((80, 170), 920, 250, boxstyle="round,pad=0,rounding_size=18", color=LINE))
    ax.text(120, 295, "No Senado, duas estreias:\nPeggy Flanagan, 1ª mulher indígena eleita\nChris Pappas, 1º homem abertamente gay eleito",
            fontsize=25, va="center", linespacing=1.35)
    save(fig, 7)

    # 8 call to action
    fig, ax = card(8, N)
    kicker(ax, "Quer ver o seu estado?")
    ax.text(80, 920, "Cada distrito,\n2024 x 2026,\nnuma página\ninterativa", fontsize=76, fontweight="bold", va="center",
            linespacing=1.0)
    ax.add_patch(FancyBboxPatch((80, 480), 920, 130, boxstyle="round,pad=0,rounding_size=24", color=DEM))
    ax.text(540, 545, "Link na bio", fontsize=56, color="white", fontweight="bold", ha="center", va="center")
    ax.text(80, 345, "Azul é Democrata, vermelho é Republicano.\nNenhum resultado em aberto foi estimado.\n"
                     "Código e dados abertos no GitHub.", fontsize=29, color=INK_2, va="center", linespacing=1.4)
    ax.text(80, 190, "github.com/JeffAirData", fontsize=30, color=INK, fontweight="bold", va="center")
    save(fig, 8)

    (OUT / "legenda.md").write_text(f"""Eleições nos EUA 2026: a virada democrata, em números 🇺🇸📊

Dois dias depois das eleições de meio de mandato, os Democratas já têm maioria na Câmara, no Senado e entre os governadores.

🔵 Câmara: {h24['D']} → {h26['D']} Democratas
🔴 Republicanos: {h24['R']} → {h26['R']} ({h26['open']} cadeiras em aberto)
🏛️ Senado: {sb['D']} → {s26['D']} Democratas
🗺️ Governadores: {gb['D']} → {g26['D']} Democratas
👩 Republicanas na Câmara: {w['R_2024']} → {w['R_2026']}

Arraste para ver a série histórica e a representação de mulheres, hispânicos, indígenas e LGBTQ+.

Resultados parciais de 5/11/2026, só para comparação.

👉 Veja cada distrito, estado por estado: link na bio

#eleicoes2026 #eua #midterms #congressoamericano #dados #datascience #visualizacaodedados #politicainternacional
""", encoding="utf8")
    print("wrote", len(list(OUT.glob("card_*.png"))), "cards and legenda.md")


if __name__ == "__main__":
    main()
