"""Build the GitHub Pages site in two languages: docs/index.html (Portuguese) and docs/en/index.html (English).

One button at the top switches language. Every number comes from Data/processed/summary_2026.json and the group
tables, so the two pages always say the same thing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "Data" / "processed"
DOCS = ROOT / "docs"
REPO = "https://github.com/JeffAirData/eua-eleicoes-congresso-2024-2026"

PT_STATES = {"Iowa": "Iowa", "Kansas": "Kansas", "Maine": "Maine", "North Carolina": "Carolina do Norte",
             "Ohio (special)": "Ohio (eleição especial)", "South Carolina": "Carolina do Sul", "Texas": "Texas",
             "Georgia": "Geórgia", "Nevada": "Nevada", "Ohio": "Ohio", "Alaska": "Alasca", "Michigan": "Michigan",
             "Mississippi": "Mississippi", "California": "Califórnia", "Oklahoma": "Oklahoma"}


def lst(items, lang):
    names = [PT_STATES.get(i, i) if lang == "pt" else i for i in items]
    sep, last = (", ", " e ") if lang == "pt" else (", ", " and ")
    return names[0] if len(names) == 1 else sep.join(names[:-1]) + last + names[-1]


def texts(lang: str) -> dict:
    s = json.loads((DATA / "summary_2026.json").read_text(encoding="utf8"))
    g = pd.read_csv(DATA / "house_groups_2024_2026.csv").set_index("group")
    h24, h26, sb, s26, gb, g26, w = (s["house_2024"], s["house_2026"], s["senate_before"], s["senate_2026"],
                                    s["gov_before"], s["gov_2026"], s["women"])
    loss_min, loss_max = h24["R"] - h26["R"] - h26["open"], h24["R"] - h26["R"]
    pt = lang == "pt"
    mid = pd.read_csv(DATA / "midterm_president_party_change.csv")
    n_mid, n_loss = len(mid), int((mid.change < 0).sum())
    worst = mid.loc[mid.change.idxmin()]
    T = {}
    T["lang"] = "pt-BR" if pt else "en"
    T["title"] = "Eleições nos EUA: Congresso e governadores, 2024 x 2026" if pt else "U.S. elections: Congress and governors, 2024 vs 2026"
    T["switch"] = ('<a href="en/" class="switch" hreflang="en">English version</a>' if pt
                   else '<a href="../" class="switch" hreflang="pt-BR">Versão em português</a>')
    T["img"] = "img/"
    T["leg_d"], T["leg_r"] = ("Democratas", "Republicanos") if pt else ("Democrats", "Republicans")
    T["data"] = "data.json" if pt else "../data.json"
    T["warn"] = (f"<strong>Resultados parciais.</strong> Retrato de 5 de novembro de 2026, dois dias depois da eleição: "
                 f"{h26['open']} cadeiras da Câmara, {s26['open']} do Senado e {g26['open']} governos ainda sem vencedor. "
                 f"Os números servem para comparar, não são definitivos." if pt else
                 f"<strong>Provisional results.</strong> A snapshot from November 5, 2026, two days after the election: "
                 f"{h26['open']} House seats, {s26['open']} Senate seats and {g26['open']} governorships still uncalled. "
                 f"The numbers are for comparison and are not final.")
    T["lead"] = (f"Os Democratas passaram de {h24['D']} para pelo menos {h26['D']} cadeiras na Câmara, "
                 f"de {sb['D']} para {s26['D']} no Senado e de {gb['D']} para {g26['D']} governos estaduais. "
                 f"Comparei com a eleição de 2024 e com a série histórica desde 1913." if pt else
                 f"Democrats went from {h24['D']} to at least {h26['D']} House seats, from {sb['D']} to {s26['D']} "
                 f"in the Senate and from {gb['D']} to {g26['D']} governorships. I compared them with the 2024 election "
                 f"and with the historical series since 1913.")
    T["h_parties"] = "1. Câmara, Senado e governadores" if pt else "1. House, Senate and governors"
    T["p_parties"] = (
        f"<ul><li><strong>Câmara:</strong> {h24['D']} D x {h24['R']} R em 2024; agora {h26['D']} D x {h26['R']} R, "
        f"com {h26['open']} em aberto. A maioria é 218: os Democratas já a têm.</li>"
        f"<li><strong>Senado:</strong> {sb['D']} D x {sb['R']} R antes da eleição (os dois independentes votam com os Democratas); "
        f"agora {s26['D']} D x {s26['R']} R. Passaram para os Democratas: {lst(s['senate_flips_to_D'], lang)}. "
        f"Em aberto: {lst(s['senate_open'], lang)}.</li>"
        f"<li><strong>Governadores:</strong> {gb['D']} D x {gb['R']} R antes; agora {g26['D']} D x {g26['R']} R. "
        f"Viraram para os Democratas: {lst(s['gov_flips_to_D'], lang)}. Em aberto: {lst(s['gov_open'], lang)}.</li></ul>"
        if pt else
        f"<ul><li><strong>House:</strong> {h24['D']} D vs {h24['R']} R in 2024; now {h26['D']} D vs {h26['R']} R, "
        f"with {h26['open']} uncalled. A majority is 218: Democrats already have it.</li>"
        f"<li><strong>Senate:</strong> {sb['D']} D vs {sb['R']} R before the election (both independents caucus with Democrats); "
        f"now {s26['D']} D vs {s26['R']} R. Flipped to Democrats: {lst(s['senate_flips_to_D'], lang)}. "
        f"Uncalled: {lst(s['senate_open'], lang)}.</li>"
        f"<li><strong>Governors:</strong> {gb['D']} D vs {gb['R']} R before; now {g26['D']} D vs {g26['R']} R. "
        f"Flipped to Democrats: {lst(s['gov_flips_to_D'], lang)}. Uncalled: {lst(s['gov_open'], lang)}.</li></ul>")
    T["h_states"] = "2. Estado por estado" if pt else "2. State by state"
    T["p_states"] = (f"{s['house_flips_to_D']} cadeiras passaram para os Democratas e {s['house_flips_to_R']} para os Republicanos. "
                     f"Vários estados redesenharam os distritos entre 2025 e 2026, por isso a comparação é pela bancada de cada estado "
                     f"e pelo partido que ganhou cada cadeira." if pt else
                     f"{s['house_flips_to_D']} seats flipped to Democrats and {s['house_flips_to_R']} to Republicans. "
                     f"Several states redrew their maps in 2025 and 2026, so the comparison is by each state's delegation "
                     f"and by the party that won each seat.")
    T["pick"] = "Escolha um estado" if pt else "Pick a state"
    T["h_history"] = "3. A série histórica" if pt else "3. The historical series"
    T["p_history"] = (f"De 1946 a 2022, o partido do presidente perdeu cadeiras na Câmara em {n_loss} de {n_mid} eleições de meio de mandato. "
                      f"A maior perda foi a de {int(worst.year)}: {-int(worst.change)} cadeiras. Em 2026, os Republicanos perdem entre {loss_min} e {loss_max}, "
                      f"dependendo das {h26['open']} cadeiras em aberto. Se a perda passar de {-int(worst.change)}, será a maior desde 1946." if pt else
                      f"From 1946 to 2022 the president's party lost House seats in {n_loss} of {n_mid} midterms. The biggest loss was in "
                      f"{int(worst.year)}: {-int(worst.change)} seats. In 2026 Republicans lose between {loss_min} and {loss_max}, depending on the "
                      f"{h26['open']} uncalled seats. A loss above {-int(worst.change)} would be the biggest since 1946.")
    T["h_div"] = "4. Mulheres, negros, hispânicos, indígenas e LGBTQ+" if pt else "4. Women, Black, Hispanic, Native American and LGBTQ+ members"
    T["p_div"] = (
        f"<ul><li><strong>Mulheres:</strong> {g.loc['women','elected_2024']} eleitas para a Câmara em 2024 e pelo menos "
        f"{g.loc['women','at_least_2026']} em 2026, com {h26['open']} cadeiras em aberto. A mudança está nos partidos: "
        f"as democratas passaram de {w['D_2024']} para {w['D_2026']}; as republicanas, de {w['R_2024']} para {w['R_2026']}. "
        f"As {g.loc['women','new_identified']} novatas já confirmadas são todas democratas.</li>"
        f"<li><strong>Hispânicos:</strong> {g.loc['hispanic','elected_2024']} em 2024 e pelo menos {g.loc['hispanic','at_least_2026']} em 2026, "
        f"com {g.loc['hispanic','new_identified']} novatos.</li>"
        f"<li><strong>Indígenas:</strong> {g.loc['native','elected_2024']} na Câmara em 2024 e {g.loc['native','at_least_2026']} em 2026, "
        f"com Claire Valdez (Nova York). No Senado, Peggy Flanagan (Minnesota) será a primeira mulher indígena eleita senadora.</li>"
        f"<li><strong>LGBTQ+:</strong> {g.loc['lgbtq','elected_2024']} na Câmara no início de 2025 e pelo menos "
        f"{g.loc['lgbtq','at_least_2026']} em 2026. No Senado, Chris Pappas (New Hampshire) é o primeiro homem abertamente gay eleito "
        f"senador e se junta a Tammy Baldwin.</li>"
        f"<li><strong>Negros:</strong> {g.loc['black','elected_2024']} eleitos em 2024; {g.loc['black','reelected']} foram reeleitos. "
        f"Ainda não há lista dos novatos. A imprensa destaca Melat Kiros, primeira congressista negra do Colorado, e Juliana Stratton, "
        f"eleita senadora por Illinois.</li></ul>"
        if pt else
        f"<ul><li><strong>Women:</strong> {g.loc['women','elected_2024']} elected to the House in 2024 and at least "
        f"{g.loc['women','at_least_2026']} in 2026, with {h26['open']} seats uncalled. The change is in the parties: "
        f"Democratic women went from {w['D_2024']} to {w['D_2026']}; Republican women from {w['R_2024']} to {w['R_2026']}. "
        f"All {g.loc['women','new_identified']} first-time women confirmed so far are Democrats.</li>"
        f"<li><strong>Hispanic Americans:</strong> {g.loc['hispanic','elected_2024']} in 2024 and at least {g.loc['hispanic','at_least_2026']} "
        f"in 2026, with {g.loc['hispanic','new_identified']} first-time winners.</li>"
        f"<li><strong>Native Americans:</strong> {g.loc['native','elected_2024']} in the House in 2024 and {g.loc['native','at_least_2026']} in 2026, "
        f"with Claire Valdez (New York). In the Senate, Peggy Flanagan (Minnesota) will be the first Native American woman elected senator.</li>"
        f"<li><strong>LGBTQ+:</strong> {g.loc['lgbtq','elected_2024']} in the House at the start of 2025 and at least "
        f"{g.loc['lgbtq','at_least_2026']} in 2026. In the Senate, Chris Pappas (New Hampshire) is the first openly gay man elected "
        f"senator and joins Tammy Baldwin.</li>"
        f"<li><strong>Black Americans:</strong> {g.loc['black','elected_2024']} elected in 2024; {g.loc['black','reelected']} were re-elected. "
        f"There is no list of first-time winners yet. The press highlights Melat Kiros, Colorado's first Black congresswoman, "
        f"and Juliana Stratton, elected senator for Illinois.</li></ul>")
    T["h_method"] = "Como ler os números" if pt else "How to read the numbers"
    T["p_method"] = (
        "<ul><li>Azul é sempre Democrata e vermelho, sempre Republicano. Outros partidos e disputas sem resultado ficam em cinza.</li>"
        "<li>Uma disputa só conta como decidida quando a fonte marca o vencedor. Nenhum resultado é estimado.</li>"
        "<li>2024 bate com o resultado oficial da Câmara: 220 Republicanos e 215 Democratas.</li>"
        "<li>A série histórica da Câmara é a tabela oficial <em>Party Divisions</em> do Historiador da Câmara.</li>"
        "<li>Mulheres, negros e hispânicos por legislatura vêm das listas oficiais do Historiador da Câmara; indígenas e LGBTQ+, "
        "das listas da Wikipedia. A linha conta quem passou pela Câmara em cada legislatura, inclusive substitutos; os pontos contam "
        "só os eleitos em novembro.</li>"
        "<li>Mulheres eleitas em 2026: para quem já está na Câmara, o tratamento oficial do Clerk (Mr./Ms.); para as novatas, os "
        "pronomes do artigo da Wikipedia de cada uma. Quem não tem fonte fica de fora; nada é deduzido pelo primeiro nome.</li>"
        "<li>Novatos dos outros grupos só entram quando uma fonte os nomeia. Por isso 2026 é um mínimo, não um total.</li>"
        "<li>Novato quer dizer quem não está na Câmara atual; alguns, como Elaine Luria, já foram deputados antes.</li></ul>"
        if pt else
        "<ul><li>Blue is always Democratic and red always Republican. Other parties and uncalled races are grey.</li>"
        "<li>A race counts as called only when the source marks a winner. No result is estimated.</li>"
        "<li>2024 matches the official House result: 220 Republicans and 215 Democrats.</li>"
        "<li>The House series is the House Historian's official <em>Party Divisions</em> table.</li>"
        "<li>Women, Black and Hispanic members by Congress come from the House Historian's official lists; Native American and "
        "LGBTQ+ members from Wikipedia's lists. The line counts everyone who served during each Congress, replacements included; "
        "the dots count only those elected in November.</li>"
        "<li>Women elected in 2026: the Clerk's courtesy title (Mr./Ms.) for current members; for first-time winners, the pronouns "
        "in each one's Wikipedia article. Winners with no source are left out; nothing is inferred from first names.</li>"
        "<li>First-time winners of the other groups count only when a source names them, so 2026 is a minimum, not a total.</li>"
        "<li>First-time means not in the current House; a few, such as Elaine Luria, served before.</li></ul>")
    T["sources"] = (
        "Fontes: Wikipedia (artigos das eleições de 2024 e 2026 para Câmara, Senado e governadores, que citam AP, DDHQ e as "
        "secretarias estaduais), House Clerk (MemberData.xml), House Historian (Party Divisions e listas de mulheres, negros e "
        "hispânicos), unitedstates/congress-legislators e a imprensa citada no texto."
        if pt else
        "Sources: Wikipedia (the 2024 and 2026 House, Senate and governor election articles, which cite AP, DDHQ and state "
        "election offices), House Clerk (MemberData.xml), House Historian (Party Divisions and the lists of women, Black and "
        "Hispanic members), unitedstates/congress-legislators and the press cited in the text.")
    T["code"] = f'{"Código e dados" if pt else "Code and data"}: <a href="{REPO}">{REPO.replace("https://", "")}</a>'
    T["alt"] = {k: v for k, v in zip(
        ["01_nacional", "02_estados", "03_midterms", "04_camara_historico", "05_diversidade_serie", "06_grupos_2024_2026", "07_mulheres_partido"],
        (["Barras de Câmara, Senado e governadores antes e depois da eleição", "Cadeiras que mudaram de partido, por estado",
          "Cadeiras ganhas ou perdidas pelo partido do presidente em cada eleição de meio de mandato desde 1946",
          "Cadeiras de cada partido na Câmara desde 1913", "Membros de cada grupo na Câmara por legislatura desde 1945",
          "Eleitos de cada grupo em 2024 e o que se sabe de 2026", "Mulheres eleitas para a Câmara por partido, 2024 e 2026"] if pt else
         ["Bars for House, Senate and governors before and after the election", "Seats that changed party, by state",
          "Seats gained or lost by the president's party in every midterm since 1946", "House seats held by each party since 1913",
          "Members of each group in the House by Congress since 1945", "Members of each group elected in 2024 and what is known of 2026",
          "Women elected to the House by party, 2024 and 2026"]))}
    T["js"] = dict(seats=("cadeiras" if pt else "seats"), d=("Distrito" if pt else "District"), open=("em aberto" if pt else "uncalled"),
                   gain=("mudou de partido" if pt else "changed party"), nameKey=lang, al=("único" if pt else "at large"))
    return T


PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light; --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
          --line:#e1e0d9; --dem:#2a78d6; --rep:#e34948; --open:#c3c2b7; --warn:#fbf3df; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif; background: var(--page); color: var(--ink); margin: 0; }}
  main {{ max-width: 920px; margin: 0 auto; padding: 16px 16px 48px; }}
  .top {{ display: flex; justify-content: flex-end; margin-bottom: 8px; }}
  .switch {{ display: inline-block; padding: 8px 14px; border: 2px solid var(--dem); border-radius: 999px; color: var(--dem);
            font-weight: 700; text-decoration: none; }}
  .switch:hover {{ background: var(--dem); color: #fff; }}
  h1 {{ font-size: 1.9rem; line-height: 1.2; margin: 0 0 8px; }}
  h2 {{ font-size: 1.4rem; margin: 40px 0 8px; }}
  p, li {{ color: var(--ink-2); line-height: 1.55; }}
  .lead {{ font-size: 1.15rem; color: var(--ink); }}
  .warn {{ background: var(--warn); border-left: 4px solid #d99a1e; padding: 12px 14px; border-radius: 6px; color: var(--ink); }}
  img {{ width: 100%; height: auto; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); margin: 12px 0; }}
  .legend {{ display: flex; gap: 16px; flex-wrap: wrap; color: var(--ink-2); font-size: .95rem; margin: 6px 0 10px; }}
  .sw {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }}
  section.box {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin: 16px 0; }}
  select {{ width: 100%; font: inherit; font-size: 1.05rem; padding: 10px 12px; border: 2px solid var(--dem); border-radius: 8px; background: #fff; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-variant-numeric: tabular-nums; }}
  th, td {{ text-align: left; padding: 6px 4px; border-bottom: 1px solid var(--line); font-size: .95rem; vertical-align: top; }}
  .D {{ color: var(--dem); font-weight: 700; }} .R {{ color: var(--rep); font-weight: 700; }} .O {{ color: var(--muted); }}
  .flip {{ background: var(--warn); }}
  .totals {{ display: flex; gap: 18px; flex-wrap: wrap; margin-top: 10px; }}
  footer {{ margin-top: 40px; font-size: .9rem; color: var(--muted); }}
  footer a, main a {{ color: var(--dem); }}
</style>
</head>
<body>
<main>
<div class="top">{switch}</div>
<h1>{title}</h1>
<p class="warn">{warn}</p>
<p class="lead">{lead}</p>
<div class="legend"><span><span class="sw" style="background:var(--dem)"></span>{leg_d}</span>
<span><span class="sw" style="background:var(--rep)"></span>{leg_r}</span>
<span><span class="sw" style="background:var(--open)"></span>{js_open}</span></div>

<h2 id="parte-1">{h_parties}</h2>
{p_parties}
<img src="{img}01_nacional.png" alt="{alt_01}">

<h2 id="parte-2">{h_states}</h2>
<p>{p_states}</p>
<img src="{img}02_estados.png" alt="{alt_02}">
<section class="box">
  <label for="st"><strong>{pick}</strong></label>
  <select id="st"></select>
  <div class="totals" id="tot"></div>
  <table><thead><tr><th>{js_d}</th><th>2024</th><th>2026</th></tr></thead><tbody id="rows"></tbody></table>
</section>

<h2 id="parte-3">{h_history}</h2>
<p>{p_history}</p>
<img src="{img}03_midterms.png" alt="{alt_03}">
<img src="{img}04_camara_historico.png" alt="{alt_04}">

<h2 id="parte-4">{h_div}</h2>
{p_div}
<img src="{img}05_diversidade_serie.png" alt="{alt_05}">
<img src="{img}06_grupos_2024_2026.png" alt="{alt_06}">
<img src="{img}07_mulheres_partido.png" alt="{alt_07}">

<h2>{h_method}</h2>
{p_method}
<footer><p>{sources}</p><p>{code}</p></footer>
</main>
<script>
const L = {js};
const sel = document.getElementById("st"), rows = document.getElementById("rows"), tot = document.getElementById("tot");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}}[c]));
const cell = (w, p) => w ? `<span class="${{p === "D" || p === "R" ? p : "O"}}">${{esc(w)}} (${{esc(p)}})</span>` : `<span class="O">${{L.open}}</span>`;
fetch("{data}").then(r => r.json()).then(d => {{
  const st = Object.entries(d.states).sort((a, b) => a[1][L.nameKey].localeCompare(b[1][L.nameKey]));
  sel.innerHTML = st.map(([k, v]) => `<option value="${{k}}">${{esc(v[L.nameKey])}} (${{v.seats}} ${{L.seats}})</option>`).join("");
  const show = k => {{
    const v = d.states[k];
    tot.innerHTML = `<span>2024: <span class="D">${{v.D_2024}} D</span> · <span class="R">${{v.R_2024}} R</span></span>` +
      `<span>2026: <span class="D">${{v.D_2026}} D</span> · <span class="R">${{v.R_2026}} R</span>` + (v.open ? ` · <span class="O">${{v.open}} ${{L.open}}</span>` : "") + `</span>`;
    rows.innerHTML = v.districts.map(x => `<tr class="${{x.label && x.label.endsWith("gain") ? "flip" : ""}}"><td>${{x.d === "AL" ? L.al : x.d}}` +
      `${{x.label && x.label.endsWith("gain") ? `<br><small>${{L.gain}}</small>` : ""}}</td><td>${{cell(x.w24, x.p24)}}</td><td>${{cell(x.w26, x.p26)}}</td></tr>`).join("");
  }};
  sel.value = "NC"; show("NC");
  sel.addEventListener("change", e => show(e.target.value));
}});
</script>
</body>
</html>
"""


def main() -> None:
    for lang, out in (("pt", DOCS / "index.html"), ("en", DOCS / "en" / "index.html")):
        T = texts(lang)
        alt = {f"alt_{k[:2]}": v for k, v in T.pop("alt").items()}
        js = T.pop("js")
        html = PAGE.format(**T, **alt, js=json.dumps(js, ensure_ascii=False), js_d=js["d"], js_open=js["open"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
