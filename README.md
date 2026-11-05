# Eleições nos EUA: Congresso e governadores, 2024 x 2026

As eleições de meio de mandato de 3 de novembro de 2026 comparadas com a eleição de 2024 e com a série histórica: Câmara, Senado e governadores, sempre Democratas (azul) contra Republicanos (vermelho), e a representação de mulheres, negros, hispânicos, indígenas e LGBTQ+ na Câmara.

👉 **[Abrir a página](https://jeffairdata.github.io/eua-eleicoes-congresso-2024-2026/)**: escolha um estado e veja cada distrito, 2024 x 2026.

🇺🇸 **English:** [jeffairdata.github.io/eua-eleicoes-congresso-2024-2026/en/](https://jeffairdata.github.io/eua-eleicoes-congresso-2024-2026/en/). O botão no topo de cada página troca de idioma.

> **Resultados parciais.** Retrato de 5 de novembro de 2026. Na Câmara ainda há 43 cadeiras em aberto; no Senado, 3; entre os governadores, 4. Os números de 2026 servem para comparar, não são definitivos. Para atualizar, rode `./run_all.sh --download`.

## Os quatro recortes

| | Recorte | Gráficos |
|---|---|---|
| 1 | Câmara, Senado e governadores, antes e depois | `01_nacional.png` |
| 2 | Estado por estado: cadeiras que mudaram de partido | `02_estados.png` |
| 3 | Série histórica: o partido do presidente nas eleições de meio de mandato desde 1946 e a Câmara desde 1913 | `03_midterms.png`, `04_camara_historico.png` |
| 4 | Mulheres, negros, hispânicos, indígenas e LGBTQ+ na Câmara, por legislatura, e 2024 x 2026 | `05_diversidade_serie.png`, `06_grupos_2024_2026.png`, `07_mulheres_partido.png` |

Gráficos em português em `docs/img/` e em inglês em `docs/en/img/`.

![Câmara, Senado e governadores](docs/img/01_nacional.png)
![Meio de mandato desde 1946](docs/img/03_midterms.png)
![Diversidade na Câmara](docs/img/05_diversidade_serie.png)

## Como ler os números

- **Cores fixas:** azul para Democratas, vermelho para Republicanos, cinza para outros partidos e disputas sem resultado. Os dois senadores independentes (Sanders e King) votam com os Democratas e entram no total democrata.
- **Disputa decidida** é a que a fonte marca com vencedor. Nada é estimado.
- **2024 confere com o oficial:** o parser lê 220 Republicanos e 215 Democratas, como na tabela *Party Divisions* do Historiador da Câmara.
- **Mapas redesenhados:** vários estados mudaram os distritos entre 2025 e 2026. Por isso a comparação é pela bancada de cada estado e pelo partido que ganhou cada cadeira ("ganho" quando muda de partido), não distrito a distrito.
- **Série dos grupos:** a linha conta quem passou pela Câmara em cada legislatura, inclusive substitutos; os pontos contam só os eleitos em novembro, nos dois anos com o mesmo critério.
- **Mulheres em 2026:** para quem já está na Câmara, o tratamento oficial do Clerk (Mr./Ms.); para as novatas, os pronomes do artigo da Wikipedia de cada uma. 11 vencedores sem artigo ficam de fora. Nada é deduzido pelo primeiro nome.
- **Novatos dos outros grupos** só entram quando uma fonte os nomeia: a lista de eleitos da Wikipedia para hispânicos e indígenas, e a imprensa para LGBTQ+ e negros. 2026 é um mínimo, não um total. Para negros, ainda não há lista de novatos.
- **Novato** é quem não está na Câmara atual; alguns, como Elaine Luria, já foram deputados antes.
- **LGBTQ+** conta quem já era assumido durante o mandato; quem se assumiu depois ou foi identificado postumamente fica de fora.

## Fontes

| Dado | Fonte |
|---|---|
| Resultados de 2024 e 2026, distrito a distrito; Senado e governadores 2026 | Wikipedia, artigos das eleições (citam AP, Decision Desk HQ e secretarias estaduais), texto bruto com revisão fixada em `Data/raw/` |
| Câmara por partido em cada legislatura, desde 1913 | [House Historian, Party Divisions](https://history.house.gov/Institution/Party-Divisions/Party-Divisions/) |
| Mulheres, negros e hispânicos por legislatura | House Historian: [mulheres](https://history.house.gov/Exhibitions-and-Publications/WIC/Historical-Data/Women-Representatives-and-Senators-by-Congress/), [negros](https://history.house.gov/Exhibitions-and-Publications/BAIC/Historical-Data/Black-American-Representatives-and-Senators-by-Congress/), [hispânicos](https://history.house.gov/Exhibitions-and-Publications/HAIC/Historical-Data/Hispanic-American-Representatives,-Senators,-Delegates,-and-Resident-Commissioners-by-Congress/) |
| Indígenas e LGBTQ+ | Wikipedia: *List of Native Americans in the United States Congress*, *List of LGBTQ members of the United States Congress* |
| Membros atuais e tratamento (Mr./Ms.) | [House Clerk, MemberData.xml](https://clerk.house.gov/xml/lists/MemberData.xml) |
| Novatos LGBTQ+ e negros de 2026 | Washington Blade, Advocate, GLAAD, Fast Company e ABC News (4 e 5/11/2026) |

Quando a AP e as secretarias estaduais fecharem a contagem, a fonte final será o Clerk da Câmara (*Statistics of the Congressional Election*), e as contagens oficiais de diversidade virão do CAWP (mulheres), do CRS e do Pew.

---

## Para quem quer os dados

Em `Data/processed/`:

| Arquivo | Conteúdo |
|---|---|
| `house_districts_2024.csv`, `house_districts_2026.csv` | um distrito por linha: membros anteriores, vencedor, partido, se já foi decidido, rótulo (ganho ou manutenção) |
| `house_states_2024_2026.csv` | uma linha por estado: cadeiras D e R em 2024 e em 2026, em aberto |
| `senate_races_2026.csv`, `governor_races_2026.csv` | as 35 disputas do Senado e as 36 de governador |
| `house_party_divisions.csv` | Câmara por partido no início de cada legislatura desde 1913 |
| `midterm_president_party_change.csv` | cadeiras ganhas ou perdidas pelo partido do presidente em cada meio de mandato desde 1946 |
| `members_by_group_and_congress.csv` | cada mulher, negro e hispânico em cada legislatura (Historiador da Câmara) |
| `house_group_series.csv` | contagem por grupo e legislatura, os cinco grupos |
| `group_members_119_status_2026.csv` | o que aconteceu em 2026 com cada membro desses grupos da Câmara atual |
| `house_winners_2026_gender.csv` | gênero de cada vencedor de 2026 e como foi obtido |
| `house_groups_2024_2026.csv` | resumo 2024 x 2026 por grupo |
| `summary_2026.json` | os números do texto |

Para refazer tudo:

```bash
pip install -r requirements.txt
./run_all.sh --download
```
