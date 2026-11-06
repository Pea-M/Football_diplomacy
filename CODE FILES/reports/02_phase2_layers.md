# Phase 2 layer build summary

This phase created the four interim data layers required for the football-geopolitics panel.

## Files created
- dataset/interim/transfers_layer.csv
- dataset/interim/fixtures_layer.csv
- dataset/interim/cepii_gravity_layer.csv
- dataset/interim/cow_mid_layer.csv
- dataset/interim/row_ledger.csv (updated with before/after counts)
- CODE FILES/reports/02_phase2_layers_summary.csv

## Key findings
- Transfers were filtered to 1993-2021 and merged with player nationality and league-country destination information. The resulting layer aggregates year x nationality x destination-country flows with transfer counts and fee totals.
- Fixtures were filtered to 1993-2021, mapped to ISO3, dropped GBR-GBR pairs, and aggregated to year x country pair with friendly, competitive, and neutral-venue counts.
- The CEPII layer kept the country-pair-year variables required for the gravity and geopolitics model: distance, contiguity, language, colonial ties, diplomatic disagreement, GDP, and population.
- The COW MID layer was filtered to the verified GML overlap (1993-2010), mapped from COW codes to ISO3, and reduced to onset, ongoing, and hostility indicators.

## Aggregate checks

| layer | raw_rows | window_rows | after_player_join | after_club_join | after_comp_join | known_nationality_share | known_destination_share | agg_rows | mapped_rows | after_gbr_drop | final_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transfers | 175165 | 100851 | 100851.0 | 100851.0 | 100851.0 | 0.9956966217489167 | 0.37451289526132614 | 7209.0 |  |  |  |
| fixtures | 49940 | 26162 |  |  |  |  |  | 20210.0 | 25230.0 | 25199.0 |  |
| cepii_gravity | 4699296 | 1841616 |  |  |  |  |  |  |  |  | 1841616.0 |
| cow_mid | 842685 | 324968 |  |  |  |  |  |  | 324389.0 |  | 324389.0 |
