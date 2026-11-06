# Phase 1B: COW codes to ISO3 and GML conflict-layer audit

## Source and scope
- Data source used: `DATASET/raw/cow_mid/gml_2.2.1/gml-ndy-2.2.1.csv`
- Backup MIE file not used: `DATASET/raw/cow_mid/mie_1.0/mie-1.0.csv`
- COW states file is not available in this project, so I used the `countrycode` package with `origin="cown"` and `destination="iso3c"` as required.
- I did not resolve the ambiguous historical state codes automatically; they are listed below for your approval.

## GML year coverage and key conflict columns
- Year range: 1816 to 2010
- Unique COW codes used in dyad-years: 215 in `ccode1` and 215 in `ccode2`
- Confirmed conflict flags: `midongoing` and `midonset` are present and usable as dyad-year conflict flags.
- Hostility/fatality fields present: `hostlev`, `fatality`, `fatalpre`, `hiact`, `outcome`, `settle`, `recip`, `numa`, `numb`.
- `hostlev` is the hostility level, `fatality` is the fatality count/level, and `fatalpre` tracks pre-war fatality or pre-conflict fatality intensity, while `midongoing` and `midonset` capture ongoing and onset status.

## Main overlap windows
- Main transfer and CEPII analysis window: 1993-2021
- Conflict analysis overlap from the GML dyad-year file: 1993-2010
- Because the GML file ends in 2010, I do not mix it with the 2021-era transfer and gravity analysis; the conflict layer should be assessed on a separate legal window.

## COW-to-ISO3 mapping status
- Total unique COW codes seen in GML: 216
- Matched to current ISO3 via `countrycode`: 193
- Flagged for manual resolution: 23

## Unmatched or ambiguous historical COW codes (waiting for approval)
| ccode | cow_name | iso3 | reason |
|---:|---|---|---|
| 240 | Hanover | NA | historical_or_unmapped_cow_code |
| 245 | Bavaria | NA | historical_or_unmapped_cow_code |
| 260 | nan | NA | historical_or_unmapped_cow_code |
| 265 | German Democratic Republic | NA | historical_or_unmapped_cow_code |
| 267 | Baden | NA | historical_or_unmapped_cow_code |
| 269 | Saxony | NA | historical_or_unmapped_cow_code |
| 271 | Wuerttemburg | NA | historical_or_unmapped_cow_code |
| 273 | Hesse Electoral | NA | historical_or_unmapped_cow_code |
| 275 | Hesse Grand Ducal | NA | historical_or_unmapped_cow_code |
| 280 | Mecklenburg Schwerin | NA | historical_or_unmapped_cow_code |
| 300 | Austria-Hungary | NA | historical_or_unmapped_cow_code |
| 315 | Czechoslovakia | NA | historical_or_unmapped_cow_code |
| 329 | Two Sicilies | NA | historical_or_unmapped_cow_code |
| 332 | Modena | NA | historical_or_unmapped_cow_code |
| 335 | Parma | NA | historical_or_unmapped_cow_code |
| 337 | Tuscany | NA | historical_or_unmapped_cow_code |
| 345 | Yugoslavia | NA | historical_or_unmapped_cow_code |
| 347 | Kosovo | NA | historical_or_unmapped_cow_code |
| 511 | Zanzibar | NA | historical_or_unmapped_cow_code |
| 678 | Yemen Arab Republic | NA | historical_or_unmapped_cow_code |
| 680 | Yemen People's Republic | NA | historical_or_unmapped_cow_code |
| 730 | nan | NA | historical_or_unmapped_cow_code |
| 817 | Republic of Vietnam | NA | historical_or_unmapped_cow_code |

## Why these are ambiguous
- Several are defunct states or historical boundaries rather than current sovereign states (for example `Czechoslovakia`, `Yugoslavia`, `German Democratic Republic`, `Yemen Arab Republic`, `Republic of Vietnam`).
- For these, the right ISO3 assignment depends on the year and on successor-state mapping decisions. That is why I stopped instead of guessing.

## Save locations
- Provisional COW map: `DATASET/interim/cow_map_provisional.csv`
- Unmatched/ambiguous COW codes: `DATASET/interim/cow_map_unmatched.csv`
- Row ledger: `DATASET/interim/row_ledger.csv`

## Next step
Please confirm whether I should resolve the historical COW codes above to successor states using the CEPII year windows and the project rule for defunct states, or whether you want a stricter current-country-only map. I will not apply the successor-state mapping until you tell me which route to take.
