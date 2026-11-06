# Phase 1 final harmonisation report

## Approved mapping rules applied
- I mapped each name/code to the state that actually existed in that year using the CEPII `first_year` and `last_year` windows where needed.
- I applied the approved continuator mapping rules: `USSR -> RUS`, `Yugoslavia / FR Yugoslavia / Serbia and Montenegro -> SRB`, `West Germany -> DEU`.
- I did not split any defunct state across multiple successors.
- I excluded and logged ambiguous multi-successor cases such as `Czechoslovakia`, `East Germany`, `German Democratic Republic`, and `Kosovo` without resolving them.
- Entities with no COW code were kept in football layers if CEPII reports an ISO3; their conflict value remains missing (`NaN`) rather than zero.

## Files created
- Final country map: `DATASET/interim/country_map.csv`
- Unmatched football names: `DATASET/interim/country_map_unmatched.csv`
- Unmatched COW codes: `DATASET/interim/cow_map_unmatched.csv`
- Row ledger: `DATASET/interim/row_ledger.csv`

## How many rows the continuator mapping touches
- Football rows: 689
- GML dyad-year rows: 36275
- These are the rows that will be run with and without the continuator-mapped set in the later sensitivity analysis.

## Unmatched football names
| source | raw_name | reason |
|---|---|---|
| international_results_away | Ambazonia | no_iso3_match_or_nonstate_entity |
| international_results_away | Asturias | no_iso3_match_or_nonstate_entity |
| international_results_away | Cilento | no_iso3_match_or_nonstate_entity |
| international_results_away | East Turkestan | no_iso3_match_or_nonstate_entity |
| international_results_away | Maule Sur | no_iso3_match_or_nonstate_entity |
| international_results_away | South Yemen | no_iso3_match_or_nonstate_entity |
| international_results_away | Surrey | no_iso3_match_or_nonstate_entity |
| international_results_away | Two Sicilies | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Abkhazia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Alderney | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Andalusia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Arameans Suryoye | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Artsakh | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Aymara | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Barawa | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Basque Country | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Biafra | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Brittany | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Canton Ticino | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Cascadia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Catalonia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Chagos Islands | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Chameria | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Chechnya | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Corsica | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | County of Nice | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Czechoslovakia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Darfur | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Donetsk PR | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Ellan Vannin | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Felvidék | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Franconia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Frøya | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Galicia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | German DR | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Gotland | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Gozo | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Hitra | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Hmong | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Isle of Wight | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Kabylia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Kernow | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Kurdistan | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Kárpátalja | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Luhansk PR | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Manchukuo | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Matabeleland | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Menorca | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Micronesia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Occitania | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Orkney | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Padania | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Panjab | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Provence | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Quebec | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Raetia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Rhodes | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Romani people | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Rouet-Provence | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Saare County | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Saarland | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Saint Martin | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Sark | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Sealand | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Shetland | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Somaliland | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | South Ossetia | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Székely Land | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Sápmi | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Tamil Eelam | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Tibet | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Western Isles | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Ynys Môn | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Yorkshire | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home | Zanzibar | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home;transfermarkt_countries;transfermarkt_players_birth_country;transfermarkt_players_citizenship | Kosovo | no_iso3_match_or_nonstate_entity |
| international_results_away;international_results_home;transfermarkt_players_citizenship | Bonaire | no_iso3_match_or_nonstate_entity |
| international_results_away;transfermarkt_players_birth_country | Crimea | no_iso3_match_or_nonstate_entity |
| international_results_home | Canary Islands | no_iso3_match_or_nonstate_entity |
| international_results_home | Délvidék | no_iso3_match_or_nonstate_entity |
| international_results_home | Elba Island | no_iso3_match_or_nonstate_entity |
| international_results_home | Găgăuzia | no_iso3_match_or_nonstate_entity |
| international_results_home | Madrid | no_iso3_match_or_nonstate_entity |
| international_results_home | Mapuche | no_iso3_match_or_nonstate_entity |
| international_results_home | Republic of St. Pauli | no_iso3_match_or_nonstate_entity |
| international_results_home | Ryūkyū | no_iso3_match_or_nonstate_entity |
| international_results_home | Saugeais | no_iso3_match_or_nonstate_entity |
| international_results_home | Seborga | no_iso3_match_or_nonstate_entity |
| international_results_home | Silesia | no_iso3_match_or_nonstate_entity |
| international_results_home | Yoruba Nation | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country | CSSR | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country | East Germany (GDR) | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country | Netherlands Antilles | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country | UdSSR | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country | Yugoslavia (Republic) | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_birth_country;transfermarkt_players_citizenship | Neukaledonien | no_iso3_match_or_nonstate_entity |
| transfermarkt_players_citizenship | Saint-Martin | no_iso3_match_or_nonstate_entity |

## Unmatched / excluded COW codes
| cow_code | raw_name | reason |
|---:|---|---|
| 240 | Hanover | excluded_ambiguous_defunct_state |
| 245 | Bavaria | excluded_ambiguous_defunct_state |
| 260 | NA | excluded_ambiguous_defunct_state |
| 265 | German Democratic Republic | excluded_ambiguous_defunct_state |
| 267 | Baden | excluded_ambiguous_defunct_state |
| 269 | Saxony | excluded_ambiguous_defunct_state |
| 271 | Wuerttemburg | excluded_ambiguous_defunct_state |
| 273 | Hesse Electoral | excluded_ambiguous_defunct_state |
| 275 | Hesse Grand Ducal | excluded_ambiguous_defunct_state |
| 280 | Mecklenburg Schwerin | excluded_ambiguous_defunct_state |
| 300 | Austria-Hungary | excluded_ambiguous_defunct_state |
| 315 | Czechoslovakia | excluded_ambiguous_defunct_state |
| 329 | Two Sicilies | excluded_ambiguous_defunct_state |
| 332 | Modena | excluded_ambiguous_defunct_state |
| 335 | Parma | excluded_ambiguous_defunct_state |
| 337 | Tuscany | excluded_ambiguous_defunct_state |
| 347 | Kosovo | excluded_ambiguous_defunct_state |
| 511 | Zanzibar | excluded_ambiguous_defunct_state |
| 678 | Yemen Arab Republic | excluded_ambiguous_defunct_state |
| 680 | Yemen People's Republic | excluded_ambiguous_defunct_state |
| 730 | NA | excluded_ambiguous_defunct_state |
| 817 | Republic of Vietnam | excluded_ambiguous_defunct_state |

## Stop point
This Phase 1 result is ready. I have not launched Phase 2 until you confirm the map is approved and you say “go”.
