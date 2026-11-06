# Phase 1A: football and Transfermarkt country names to ISO3

## Scope
- Used only these read-only inputs: `DATASET/raw/international_results/results.csv`, `DATASET/raw/international_results/former_names.csv`, `DATASET/raw/transfermarkt/countries.csv`, `DATASET/raw/transfermarkt/competitions.csv`, and `DATASET/raw/transfermarkt/players.csv`.
- I did not edit any raw files. The working outputs are under `DATASET/interim/` and the summary report is under `CODE FILES/reports/`.
- For home nations, I followed the project rule: England, Scotland, Wales, and Northern Ireland map to `GBR` for joins, while keeping the original fixture names in the data table.

## Provisional mapping summary
- Unique names reviewed: 368
- Matched and kept in the provisional map: 272
- Unmatched and waiting for approval: 96
- Home-nation rows matched to `GBR`: 22
- Action taken: I did not auto-resolve defunct states or ambiguous territories without your approval.

## Manual home-nation rule applied
| raw_name | iso3 | note |
|---|---:|---|
| England | GBR | special home-nation rule for fixtures and destination joins |
| Scotland | GBR | special home-nation rule for fixtures and destination joins |
| Wales | GBR | special home-nation rule for fixtures and destination joins |
| Northern Ireland | GBR | special home-nation rule for fixtures and destination joins |

## Transfermarkt destination-flow impact of home nations
- I checked the transfer dataset by joining each destination club to its league country. The share of known destination flows that land in England, Scotland, Wales, or Northern Ireland is about 9.94%.
- This means those four names will affect roughly one in ten destination-country flows, so the `GBR` rule is important for the T1 destination universe.
- I have not dropped those rows yet; the final step will be to drop only `GBR-GBR` pairs after the full country map is approved.

## Unmatched names waiting for approval
### fixtures
| raw_name |
|---|
| Abkhazia |
| Alderney |
| Ambazonia |
| Andalusia |
| Arameans Suryoye |
| Artsakh |
| Asturias |
| Aymara |
| Barawa |
| Basque Country |
| Biafra |
| Bonaire |
| Brittany |
| Canary Islands |
| Canton Ticino |
| Cascadia |
| Catalonia |
| Chagos Islands |
| Chameria |
| Chechnya |
| Cilento |
| Corsica |
| County of Nice |
| Crimea |
| Darfur |
| Donetsk PR |
| Délvidék |
| East Turkestan |
| Elba Island |
| Ellan Vannin |
| Felvidék |
| Franconia |
| Frøya |
| Galicia |
| German DR |
| Gotland |
| Gozo |
| Găgăuzia |
| Hitra |
| Hmong |
| Isle of Wight |
| Kabylia |
| Kernow |
| Kosovo |
| Kurdistan |
| Kárpátalja |
| Luhansk PR |
| Madrid |
| Manchukuo |
| Mapuche |
| Matabeleland |
| Maule Sur |
| Menorca |
| Micronesia |
| Occitania |
| Orkney |
| Padania |
| Panjab |
| Provence |
| Quebec |
| Raetia |
| Republic of St. Pauli |
| Rhodes |
| Romani people |
| Rouet-Provence |
| Ryūkyū |
| Saare County |
| Saarland |
| Saint Martin |
| Sark |
| Saugeais |
| Sealand |
| Seborga |
| Shetland |
| Silesia |
| Somaliland |
| South Ossetia |
| South Yemen |
| Surrey |
| Székely Land |
| Sápmi |
| Tamil Eelam |
| Tibet |
| Two Sicilies |
| Western Isles |
| Ynys Môn |
| Yorkshire |
| Yoruba Nation |
| Zanzibar |

### transfermarkt_players
| raw_name |
|---|
| CSSR |
| Jugoslawien (SFR) |
| Neukaledonien |
| Saint-Martin |
| UdSSR |
| Yugoslavia (Republic) |

### transfermarkt_countries
| raw_name |
|---|
| Ireland |

## Defunct or historical names that need a decision
- `Czechoslovakia`
- `Yugoslavia`
- `USSR` / `Soviet Union`
- `East Germany (GDR)` / `West Germany`
- `Serbia and Montenegro`
- `Kosovo`
- `Curaçao` / `Curacao` and other former territories

## Save locations
- Provisional country map: `DATASET/interim/country_map.csv`
- Unmatched-name table: `DATASET/interim/country_map_unmatched.csv`
- Row ledger: `DATASET/interim/row_ledger.csv`

## Next step
Please confirm whether I should resolve the ambiguous names above by successor-state mapping (for example, Czechoslovakia -> Czech Republic/Slovakia, Yugoslavia -> Serbia/Slovenia/Croatia/Bosnia/etc.) or whether you want a stricter “country names only” approach for the final map. I will not do that until you tell me which path to take.
