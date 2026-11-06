# Feature build check

- CEPII: 1,653,372 lagged pair-years; 124740 duplicate pair-years dropped
- GML dyad-years: 842,685 raw -> 790,117 mapped to ISO3 pairs; GML last year = 2010
- T1: dropped 0 domestic rows (origin == destination), carrying 0 moves
- T1: league-destination filter kept target 16,399.0 of 16,399.0
- T1: existence filter kept 203,280 of 215,760 rows; target kept 16,399.0 of 16,399.0
- T2: 0 duplicate rows collapsed by unordered pair (should be 0 if panel was undirected)
- T2: existence filter kept 823,284 of 895,404 rows; target kept 8,399.0 of 8,607.0

## T1 talent flows (directed)
- rows 87,120 | years 2010-2021 | origins 243 | destinations 30 | pairs 6,825
- non-zero rows 6,418 (7.37%) | target total 16,071
- target per year: first 3 {2010: 206, 2011: 303, 2012: 432} | last 3 {2019: 2410, 2020: 2509, 2021: 2815}
- coverage: distance 90.2% | UN disagreement 73.5% | lag_target 100.0%
- GBR present: True | ENG/SCO present (should be False): False
- conflict coverage in target years <= 2011: 76.3%; pair-years with an ongoing MID: 19
- destinations list: ['ARG', 'AUS', 'AUT', 'BEL', 'BRA', 'CHE', 'CZE', 'DEU', 'DNK', 'ESP', 'FRA', 'GBR', 'GRC', 'HRV', 'ITA', 'JPN', 'KOR', 'MEX', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'RUS', 'SAU', 'SRB', 'SWE', 'TUR', 'UKR', 'USA']
- lag_target vs lag_reverse_flow correlation (must be < 1): 0.064

## T2 friendlies (undirected)
- rows 823,284 | years 1994-2021 | origins 242 | second countries 242 | pairs 29,403
- non-zero rows 7,652 (0.93%) | target total 8,399
- target per year: first 3 {1994: 276, 1995: 191, 1996: 302} | last 3 {2019: 233, 2020: 100, 2021: 209}
- coverage: distance 86.5% | UN disagreement 55.0% | lag_target 96.4%
- GBR present: True | ENG/SCO present (should be False): False
- conflict coverage in target years <= 2011: 61.1%; pair-years with an ongoing MID: 906
- same_confederation coverage 100.0%, share same 0.17
