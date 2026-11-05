"""Build the static charts (PNG) and the data file of the interactive page, in Portuguese and English.

Democrats are always blue and Republicans always red; other parties and uncalled races are grey.
Titles and numbers are computed from Data/processed, never typed in. 2026 numbers are provisional.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

import parse_governors
from build_dataset import RAW, SENATE_NOT_UP

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "Data" / "processed"
DOCS = ROOT / "docs"

DEM, REP, OPEN, OTHER = "#2a78d6", "#e34948", "#c3c2b7", "#898781"
INK, INK_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 11, "text.color": INK, "axes.labelcolor": INK_2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": "#c3c2b7",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

STATE_PT = {"AL": "Alabama", "AK": "Alasca", "AZ": "Arizona", "AR": "Arkansas", "CA": "Califórnia", "CO": "Colorado",
            "CT": "Connecticut", "DE": "Delaware", "FL": "Flórida", "GA": "Geórgia", "HI": "Havaí", "ID": "Idaho",
            "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
            "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
            "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
            "NH": "Nova Hampshire", "NJ": "Nova Jersey", "NM": "Novo México", "NY": "Nova York",
            "NC": "Carolina do Norte", "ND": "Dakota do Norte", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
            "PA": "Pensilvânia", "RI": "Rhode Island", "SC": "Carolina do Sul", "SD": "Dakota do Sul",
            "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virgínia", "WA": "Washington",
            "WV": "Virgínia Ocidental", "WI": "Wisconsin", "WY": "Wyoming"}
STATE_EN = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
            "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
            "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
            "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
            "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
            "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
            "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
            "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
            "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
            "WI": "Wisconsin", "WY": "Wyoming"}

LANG = "pt"


def t(pt: str, en: str) -> str:
    return en if LANG == "en" else pt


def img_dir() -> Path:
    d = DOCS / ("en/img" if LANG == "en" else "img")
    d.mkdir(parents=True, exist_ok=True)
    return d


def source(fig, extra: str = "") -> None:
    fig.text(0.01, 0.01, t("Fonte: ", "Source: ") + extra + t(
        " · Resultados de 2026 parciais (5/11/2026), só para comparação. github.com/JeffAirData",
        " · 2026 results are provisional (Nov 5, 2026), for comparison only. github.com/JeffAirData"),
        fontsize=8.5, color=MUTED, ha="left", va="bottom")


def fmt_change(n: int) -> str:
    return f"+{n}" if n > 0 else f"{n}" if n < 0 else "0"


# ---------- numbers shared by charts, page and post ----------

def summary() -> dict:
    h24 = pd.read_csv(DATA / "house_districts_2024.csv")
    h26 = pd.read_csv(DATA / "house_districts_2026.csv")
    sen = pd.read_csv(DATA / "senate_races_2026.csv")
    gov = parse_governors.parse(RAW / "2026_United_States_gubernatorial_elections.wiki")
    gov.to_csv(DATA / "governor_races_2026.csv", index=False)
    s = dict(
        house_2024=dict(D=int((h24.winner_party == "D").sum()), R=int((h24.winner_party == "R").sum()), open=0),
        house_2026=dict(D=int((h26.winner_party == "D").sum()), R=int((h26.winner_party == "R").sum()),
                        open=int((~h26.called).sum())),
        senate_before=dict(D=SENATE_NOT_UP["D"] + int((sen.incumbent_party == "D").sum()),
                           R=SENATE_NOT_UP["R"] + int((sen.incumbent_party == "R").sum()), open=0),
        senate_2026=dict(D=SENATE_NOT_UP["D"] + int((sen.winner_party == "D").sum()),
                         R=SENATE_NOT_UP["R"] + int((sen.winner_party == "R").sum()), open=int((~sen.called).sum())),
        gov_before=dict(D=parse_governors.NOT_UP["D"] + int((gov.incumbent_party == "D").sum()),
                        R=parse_governors.NOT_UP["R"] + int((gov.incumbent_party == "R").sum()), open=0),
        gov_2026=dict(D=parse_governors.NOT_UP["D"] + int((gov.winner_party == "D").sum()),
                      R=parse_governors.NOT_UP["R"] + int((gov.winner_party == "R").sum()), open=int((~gov.called).sum())),
    )
    s["senate_flips_to_D"] = sorted(sen[(sen.incumbent_party == "R") & (sen.winner_party == "D")].race)
    s["gov_flips_to_D"] = sorted(gov[(gov.incumbent_party == "R") & (gov.winner_party == "D")].state)
    s["senate_open"] = sorted(sen[~sen.called].race)
    s["gov_open"] = sorted(gov[~gov.called].state)
    lab = h26.label.fillna("")
    s["house_flips_to_D"] = int((lab == "Democratic gain").sum())
    s["house_flips_to_R"] = int((lab == "Republican gain").sum())
    return s


# ---------- charts ----------

def chart_national(s: dict) -> None:
    """Three chambers, before and after: stacked bars, Democrats blue, Republicans red, uncalled grey."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 7.2))
    blocks = [(t("Câmara (435 cadeiras)", "House (435 seats)"), s["house_2024"], s["house_2026"], 218,
               t("eleição de 2024", "2024 election")),
              (t("Senado (100 cadeiras)", "Senate (100 seats)"), s["senate_before"], s["senate_2026"], 51,
               t("antes da eleição", "before the election")),
              (t("Governadores (50 estados)", "Governors (50 states)"), s["gov_before"], s["gov_2026"], None,
               t("antes da eleição", "before the election"))]
    for ax, (title, before, after, maj, before_label) in zip(axes, blocks):
        total = before["D"] + before["R"] + before["open"]
        for y, d, lab in [(1, before, before_label), (0, after, t("2026, parcial", "2026, provisional"))]:
            left = 0
            for k, c in (("D", DEM), ("open", OPEN), ("R", REP)):
                if d[k]:
                    ax.barh(y, d[k], left=left, color=c, height=0.62, edgecolor=SURFACE, linewidth=1)
                    ax.text(left + d[k] / 2, y, str(d[k]), ha="center", va="center",
                            color="white" if k != "open" else INK, fontsize=11, fontweight="bold")
                    left += d[k]
            ax.text(-total * 0.01, y, lab, ha="right", va="center", fontsize=10.5, color=INK_2)
        if maj is None:
            ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", pad=14)
            ax.set_xlim(0, total)
            ax.set_ylim(-0.5, 1.7)
            ax.axis("off")
            continue
        ax.axvline(maj, color=INK, lw=1, ls=(0, (2, 2)))
        ax.text(maj + total * 0.006, 1.5, t(f"maioria: {maj}", f"majority: {maj}"), ha="left", fontsize=9, color=INK_2)
        ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", pad=14)
        ax.set_xlim(0, total)
        ax.set_ylim(-0.5, 1.7)
        ax.axis("off")
    fig.legend(handles=[Patch(color=DEM, label=t("Democratas", "Democrats")),
                        Patch(color=REP, label=t("Republicanos", "Republicans")),
                        Patch(color=OPEN, label=t("sem resultado ainda", "not yet called"))],
               loc="upper left", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.005, 0.955))
    fig.suptitle(t("Democratas viram a Câmara, o Senado e os governos estaduais",
                   "Democrats flip the House, the Senate and the governorships"),
                 x=0.01, ha="left", fontsize=15, fontweight="bold", y=0.995)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.83, bottom=0.07, hspace=0.75)
    source(fig, "Wikipedia (AP, DDHQ e secretarias estaduais), House Clerk" if LANG == "pt" else
           "Wikipedia (AP, DDHQ and state election offices), House Clerk")
    fig.savefig(img_dir() / "01_nacional.png", dpi=150)
    plt.close(fig)


def chart_states() -> None:
    """Seats that changed party in 2026, per state, from each district's result (gain = the seat changed hands)."""
    h = pd.read_csv(DATA / "house_districts_2026.csv")
    lab = h.label.fillna("")
    st = pd.DataFrame({"D": h[lab == "Democratic gain"].groupby("state").size(),
                       "R": h[lab == "Republican gain"].groupby("state").size()}).fillna(0).astype(int)
    st["open"] = h[~h.called].groupby("state").size()
    st = st.fillna(0).astype(int)
    st = st[(st.D > 0) | (st.R > 0)]
    st["name"] = st.index.map(STATE_PT if LANG == "pt" else STATE_EN)
    st = st.sort_values(["D", "R", "name"], ascending=[True, False, False])
    fig, ax = plt.subplots(figsize=(10, 0.34 * len(st) + 2.1))
    y = list(range(len(st)))
    ax.barh(y, st.D, color=DEM, height=0.62)
    ax.barh(y, -st.R, color=REP, height=0.62)
    for i, (_, r) in enumerate(st.iterrows()):
        ax.text(-r.R - 0.25, i, r["name"], ha="right", va="center", fontsize=9.5, color=INK)
        if r.D:
            ax.text(r.D + 0.12, i, str(r.D), va="center", fontsize=9, color=DEM, fontweight="bold")
        if r.R:
            ax.text(-r.R + 0.12, i, str(r.R), va="center", fontsize=9, color="white", fontweight="bold")
        if r.open:
            ax.text(st.D.max() + 1.4, i, t(f"{r.open} em aberto", f"{r.open} uncalled"), va="center", fontsize=8.5, color=MUTED)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-st.R.max() - 4.2, st.D.max() + 3.2)
    ax.set_xticks(range(-int(st.R.max()), int(st.D.max()) + 1))
    ax.set_xticklabels([str(abs(v)) for v in range(-int(st.R.max()), int(st.D.max()) + 1)])
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel(t("cadeiras que passaram para cada partido", "seats that changed hands, by the party that won them"))
    nd, nr = int(st.D.sum()), int(st.R.sum())
    ax.set_title(t(f"{nd} cadeiras passaram para os Democratas e {nr} para os Republicanos",
                   f"{nd} seats flipped to Democrats and {nr} to Republicans"), loc="left", fontsize=14, fontweight="bold", pad=26)
    ax.text(0, 1.015, t(f"Em {int((st.D > 0).sum())} estados. Inclui cadeiras de mapas redesenhados. Ainda há {int(h.called.eq(False).sum())} cadeiras em aberto.",
                        f"In {int((st.D > 0).sum())} states. Includes seats on redrawn maps. {int(h.called.eq(False).sum())} seats are still uncalled."),
            transform=ax.transAxes, fontsize=9.5, color=INK_2)
    ax.legend(handles=[Patch(color=DEM, label=t("ganhas pelos Democratas", "won by Democrats")),
                       Patch(color=REP, label=t("ganhas pelos Republicanos", "won by Republicans"))],
              loc="lower right", frameon=False)
    fig.subplots_adjust(left=0.03, right=0.98, top=1 - 1.1 / (0.34 * len(st) + 2.1), bottom=0.9 / (0.34 * len(st) + 2.1))
    source(fig, "Wikipedia (AP, DDHQ e secretarias estaduais)" if LANG == "pt" else "Wikipedia (AP, DDHQ and state election offices)")
    fig.savefig(img_dir() / "02_estados.png", dpi=150)
    plt.close(fig)


def chart_midterms(s: dict) -> None:
    """Seats won or lost by the president's party in every midterm since 1946, 2026 as a provisional range."""
    from house_history import MIDTERM_PRESIDENT
    pdv = pd.read_csv(DATA / "house_party_divisions.csv").set_index("election")
    rows = []
    for y, p in MIDTERM_PRESIDENT.items():
        if y == 2026:
            continue
        rows.append(dict(year=y, party=p, change=int(pdv.loc[y, p] - pdv.loc[y - 2, p])))
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "midterm_president_party_change.csv", index=False)
    now = s["house_2026"]["R"] - s["house_2024"]["R"]
    best = now + s["house_2026"]["open"]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.bar(df.year, df.change, color=[DEM if p == "D" else REP for p in df.party], width=2.6)
    ax.bar([2026], [best], color=REP, width=2.6, alpha=0.95)
    ax.bar([2026], [now - best], bottom=[best], color=REP, width=2.6, alpha=0.35, hatch="////", edgecolor=SURFACE)
    for _, r in df.iterrows():
        ax.text(r.year, r.change + (1.5 if r.change >= 0 else -1.5), fmt_change(r.change), ha="center",
                va="bottom" if r.change >= 0 else "top", fontsize=8.5, color=INK_2)
    ax.text(2026, now - 2, t(f"de {best} a {now}:\n{s['house_2026']['R']} já eleitos,\n{s['house_2026']['open']} em aberto",
                             f"{best} to {now}:\n{s['house_2026']['R']} called,\n{s['house_2026']['open']} uncalled"),
            ha="center", va="top", fontsize=8.5, color=REP, fontweight="bold")
    ax.axhline(0, color=INK, lw=0.8)
    worst = df.loc[df.change.idxmin()]
    ax.set_title(t("Em eleições de meio de mandato, o partido do presidente quase sempre perde cadeiras",
                   "In midterms the president's party almost always loses House seats"),
                 loc="left", fontsize=14, fontweight="bold", pad=26)
    ax.text(0, 1.02, t(f"Cadeiras ganhas ou perdidas na Câmara pelo partido do presidente. Maior perda desde 1946: "
                       f"{worst.change} em {worst.year}.",
                       f"House seats gained or lost by the president's party. Biggest loss since 1946: "
                       f"{worst.change} in {worst.year}."), transform=ax.transAxes, fontsize=10, color=INK_2)
    ax.set_xticks(list(df.year) + [2026])
    ax.set_xticklabels([str(y) for y in list(df.year) + [2026]], rotation=90, fontsize=9)
    ax.set_ylim(min(now, df.change.min()) - 24, 22)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(handles=[Patch(color=DEM, label=t("presidente democrata", "Democratic president")),
                       Patch(color=REP, label=t("presidente republicano", "Republican president"))],
              loc="lower left", frameon=False)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.86, bottom=0.17)
    source(fig, "House Historian (Party Divisions) e Wikipedia" if LANG == "pt" else "House Historian (Party Divisions) and Wikipedia")
    fig.savefig(img_dir() / "03_midterms.png", dpi=150)
    plt.close(fig)


def chart_house_history(s: dict) -> None:
    """Democratic and Republican seats at the start of every Congress since 1913, 2027 provisional."""
    pdv = pd.read_csv(DATA / "house_party_divisions.csv")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pdv.start_year, pdv.D, color=DEM, lw=2.2)
    ax.plot(pdv.start_year, pdv.R, color=REP, lw=2.2)
    h, o = s["house_2026"], s["house_2026"]["open"]
    for k, c in (("D", DEM), ("R", REP)):
        ax.plot([2025, 2027], [pdv.iloc[-1][k], h[k]], color=c, lw=2.2, ls=(0, (2, 1.5)))
        ax.vlines(2027, h[k], h[k] + o, color=c, lw=5, alpha=0.3)
        ax.scatter([2027], [h[k]], color=c, s=30, zorder=3)
        ax.text(2028.2, h[k] + o / 2, f"{h[k]}–{h[k] + o}", va="center", fontsize=9.5, color=c, fontweight="bold")
    ax.axhline(218, color=INK, lw=0.8, ls=(0, (2, 2)))
    ax.text(2033.5, 222, t("maioria: 218", "majority: 218"), fontsize=9, color=INK_2, ha="right")
    ax.set_xlim(1911, 2034)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_ylabel(t("cadeiras no início de cada legislatura", "seats at the start of each Congress"))
    ax.set_title(t("Câmara dos EUA desde 1913: cadeiras de cada partido", "U.S. House since 1913: seats held by each party"),
                 loc="left", fontsize=14, fontweight="bold", pad=10)
    ax.legend(handles=[Patch(color=DEM, label=t("Democratas", "Democrats")),
                       Patch(color=REP, label=t("Republicanos", "Republicans"))], loc="upper right", frameon=False, ncol=2)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.9, bottom=0.12)
    source(fig, "House Historian (Party Divisions) e Wikipedia" if LANG == "pt" else "House Historian (Party Divisions) and Wikipedia")
    fig.savefig(img_dir() / "04_camara_historico.png", dpi=150)
    plt.close(fig)


GROUP_NAMES = {"women": ("Mulheres", "Women"), "black": ("Negros", "Black Americans"),
               "hispanic": ("Hispânicos", "Hispanic Americans"), "native": ("Indígenas", "Native Americans"),
               "lgbtq": ("LGBTQ+ assumidos", "Openly LGBTQ+")}


def chart_diversity_series() -> None:
    """Members of each group in the House during each Congress; elected-in-November points for 2025 and 2027."""
    ser = pd.read_csv(DATA / "house_group_series.csv")
    g26 = pd.read_csv(DATA / "house_groups_2024_2026.csv").set_index("group")
    fig, axes = plt.subplots(1, 5, figsize=(14, 4.6))
    for ax, g in zip(axes, ["women", "black", "hispanic", "native", "lgbtq"]):
        d = ser[(ser.group == g) & (ser.start_year >= 1945)]
        ax.plot(d.start_year, d.House, color=INK_2, lw=1.6)
        e24, e26 = int(g26.loc[g, "elected_2024"]), int(g26.loc[g, "at_least_2026"])
        ax.scatter([2025], [e24], color=INK, s=26, zorder=3)
        ymax = max(d.House.max(), e24, e26)
        n26 = t("sem lista", "no list") if g == "black" else f"≥{e26}"
        ax.text(0, 1.0, t(f"eleitos: {e24} em 2024 · {n26} em 2026", f"elected: {e24} in 2024 · {n26} in 2026"),
                transform=ax.transAxes, fontsize=9, color=INK_2, va="bottom")
        if g != "black":
            ax.scatter([2027], [e26], color=DEM, s=34, zorder=3)
        ax.set_title(t(*GROUP_NAMES[g]), loc="left", fontsize=12, fontweight="bold", pad=20)
        ax.set_xlim(1943, 2031)
        ax.set_ylim(0, ymax * 1.25 + 1)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_xticks([1950, 1990, 2025])
    fig.suptitle(t("Câmara dos EUA: quantos membros de cada grupo, legislatura por legislatura, desde 1945",
                   "U.S. House: members of each group in every Congress since 1945"),
                 x=0.01, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.875, t("Linha: quem passou pela Câmara em cada legislatura, inclusive substitutos. "
                            "Pontos: eleitos em novembro (preto, 2024; azul, 2026, mínimo já confirmado).",
                            "Line: everyone who served during each Congress, replacements included. "
                            "Dots: elected in November (black, 2024; blue, 2026, minimum confirmed so far)."),
             fontsize=9.5, color=INK_2)
    fig.subplots_adjust(left=0.04, right=0.99, top=0.72, bottom=0.13, wspace=0.3)
    source(fig, "House Historian (mulheres, negros, hispânicos), Wikipedia (indígenas, LGBTQ+)" if LANG == "pt"
           else "House Historian (women, Black and Hispanic members), Wikipedia (Native American, LGBTQ+)")
    fig.savefig(img_dir() / "05_diversidade_serie.png", dpi=150)
    plt.close(fig)


def chart_groups_2024_2026() -> None:
    """For each group: elected in 2024 vs 2026 so far (re-elected + first-time winners + still uncalled)."""
    g = pd.read_csv(DATA / "house_groups_2024_2026.csv").set_index("group")
    order = ["women", "black", "hispanic", "native", "lgbtq"]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for i, k in enumerate(order):
        r = g.loc[k]
        ax.barh(i + 0.2, r.elected_2024, height=0.36, color=GRID)
        ax.text(r.elected_2024 + 1, i + 0.2, t(f"{r.elected_2024} eleitos em 2024", f"{r.elected_2024} elected in 2024"),
                va="center", fontsize=9, color=INK_2)
        ax.barh(i - 0.2, r.reelected, height=0.36, color=INK_2)
        if k != "black":
            ax.barh(i - 0.2, r.new_identified, left=r.reelected, height=0.36, color=DEM)
        ax.barh(i - 0.2, r.uncalled, left=r.reelected + r.new_identified, height=0.36, color=OPEN, hatch="////",
                edgecolor=SURFACE)
        if k == "black":
            label = t(f"2026: {r.reelected} reeleitos; novatos ainda sem lista", f"2026: {r.reelected} re-elected; no list of new members yet")
            end_x = r.reelected
        else:
            label = (t(f"2026: {r.reelected} reeleitos + {r.new_identified} " + ("novato" if r.new_identified == 1 else "novatos"),
                       f"2026: {r.reelected} re-elected + {r.new_identified} new")
                     + (t(f" + {r.uncalled} em aberto", f" + {r.uncalled} uncalled") if r.uncalled else ""))
            end_x = r.reelected + r.new_identified + r.uncalled
        ax.text(end_x + 1, i - 0.2, label, va="center", fontsize=9, color=INK, fontweight="bold")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([t(*GROUP_NAMES[k]) for k in order], fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, g.elected_2024.max() * 1.75)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(handles=[Patch(color=GRID, label=t("eleitos em 2024", "elected in 2024")),
                       Patch(color=INK_2, label=t("reeleitos em 2026", "re-elected in 2026")),
                       Patch(color=DEM, label=t("novatos já identificados", "first-time winners identified")),
                       Patch(facecolor=OPEN, hatch="////", edgecolor=SURFACE, label=t("disputa em aberto", "race uncalled"))],
              loc="lower right", frameon=False, fontsize=9)
    ax.set_title(t("Câmara: quem foi eleito em 2024 e o que já se sabe de 2026", "House: elected in 2024 and what is known of 2026"),
                 loc="left", fontsize=14, fontweight="bold", pad=24)
    ax.text(0, 1.02, t("Novatos só entram quando uma fonte os identifica pelo nome. Nada é deduzido.",
                       "First-time winners count only when a source names them. Nothing is inferred."),
            transform=ax.transAxes, fontsize=9.5, color=INK_2)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.86, bottom=0.08)
    source(fig, "House Historian, House Clerk, Wikipedia, imprensa" if LANG == "pt" else "House Historian, House Clerk, Wikipedia, press")
    fig.savefig(img_dir() / "06_grupos_2024_2026.png", dpi=150)
    plt.close(fig)


def chart_women_party() -> dict:
    """Women elected to the House by party: 2024 vs 2026 so far."""
    from build_dataset import women_2024
    w24 = women_2024()
    gen = pd.read_csv(DATA / "house_winners_2026_gender.csv")
    a = w24[w24.woman].winner_party.value_counts()
    b = gen[gen.gender == "F"].winner_party.value_counts()
    res = dict(D_2024=int(a.get("D", 0)), R_2024=int(a.get("R", 0)), D_2026=int(b.get("D", 0)), R_2026=int(b.get("R", 0)),
               unknown=int(gen.gender.isna().sum()))
    fig, ax = plt.subplots(figsize=(8, 4.4))
    x = [0, 1]
    ax.bar([i - 0.18 for i in x], [res["D_2024"], res["R_2024"]], width=0.34, color=[DEM, REP], alpha=0.4)
    ax.bar([i + 0.18 for i in x], [res["D_2026"], res["R_2026"]], width=0.34, color=[DEM, REP])
    for i, (v0, v1) in enumerate([(res["D_2024"], res["D_2026"]), (res["R_2024"], res["R_2026"])]):
        ax.text(i - 0.18, v0 + 2, f"{v0}\n2024", ha="center", fontsize=10, color=INK_2)
        ax.text(i + 0.18, v1 + 2, f"{v1}\n2026", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([t("Democratas", "Democrats"), t("Republicanas", "Republicans")], fontsize=11)
    ax.set_ylim(0, max(res.values()) * 1.3)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title(t("Mulheres eleitas para a Câmara, por partido", "Women elected to the House, by party"),
                 loc="left", fontsize=14, fontweight="bold", pad=24)
    ax.text(0, 1.03, t(f"2026: cadeiras já decididas; {res['unknown']} vencedores sem fonte para o gênero ficam de fora.",
                       f"2026: called seats only; {res['unknown']} winners with no source for gender are left out."),
            transform=ax.transAxes, fontsize=9.5, color=INK_2)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.14)
    source(fig, "House Historian, House Clerk, Wikipedia" if LANG == "pt" else "House Historian, House Clerk, Wikipedia")
    fig.savefig(img_dir() / "07_mulheres_partido.png", dpi=150)
    plt.close(fig)
    return res


def page_data(s: dict, women: dict) -> None:
    """One JSON for the interactive page: every district of both elections, per state."""
    h24 = pd.read_csv(DATA / "house_districts_2024.csv")
    h26 = pd.read_csv(DATA / "house_districts_2026.csv")
    st = pd.read_csv(DATA / "house_states_2024_2026.csv")
    out = {"summary": s, "women": women, "states": {}}
    for _, r in st.iterrows():
        a = h24[h24.state == r.state]
        b = h26[h26.state == r.state]
        out["states"][r.state] = dict(
            pt=STATE_PT[r.state], en=STATE_EN[r.state], seats=int(r.seats),
            D_2024=int(r.D_2024), R_2024=int(r.R_2024), D_2026=int(r.D_2026), R_2026=int(r.R_2026), open=int(r.uncalled_2026),
            districts=[dict(d=str(x.district), w24=y.winner, p24=y.winner_party, w26=(x.winner if x.called else None),
                            p26=(x.winner_party if x.called else None), label=x.label if isinstance(x.label, str) else None)
                       for (_, x), (_, y) in zip(b.iterrows(), a.iterrows())])
    (DOCS / "data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf8")


def main() -> None:
    global LANG
    s = summary()
    women = {}
    for LANG in ("pt", "en"):
        chart_national(s)
        chart_states()
        chart_midterms(s)
        chart_house_history(s)
        chart_diversity_series()
        chart_groups_2024_2026()
        women = chart_women_party()
    page_data(s, women)
    (DATA / "summary_2026.json").write_text(json.dumps({**s, "women": women}, ensure_ascii=False, indent=1), encoding="utf8")
    print(json.dumps(s, ensure_ascii=False))
    print(women)


if __name__ == "__main__":
    main()
