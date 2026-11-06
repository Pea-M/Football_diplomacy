# Phase 3 verification report

This report checks the saved panels and layer outputs without changing any raw source files or overwriting the analysis data. It is a verification-only stop point before Phase 4.

## 1) Panel definitions

| panel | rows | column names + dtypes | year range | distinct origins | distinct destinations | distinct pairs | non-zero rows |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| panel_talent | 1790808 | year: int64; country_i_iso3: str; country_j_iso3: str; talent_flow_count: float64; transfer_fee_sum_eur: float64; has_flow: bool; zero_fill_indicator: bool | 1993-2021 | 249 | 249 | 61752 | 6681 |
| panel_fixtures | 895404 | year: int64; country_i_iso3: str; country_j_iso3: str; match_count: float64; friendly_count: float64; competitive_count: float64; neutral_venue_share: float64; has_fixture: bool; zero_fill_indicator: bool | 1993-2021 | 248 | 248 | 30876 | 20210 |

## 2) Talent destinations

The actual T1 destination universe in the non-domestic transfer target is: ARG, AUS, AUT, BEL, BRA, CHE, CZE, DEU, DNK, ESP, FRA, GBR, GRC, HRV, ITA, JPN, KOR, MEX, NLD, NOR, POL, PRT, ROU, RUS, SAU, SRB, SWE, TUR, UKR, USA.

This is the 30-country league-country list after England and Scotland were merged to GBR, and no other destination appears in the actual transfer target.

## 3) Transfer row ledger

| step | n_rows | loss vs previous | % lost |
| --- | ---: | ---: | ---: |
| raw_rows | 175165 | 0 | 0.00% |
| after_dropping_future_dated | 100851 | 74314 | 42.43% |
| within_1993_2021 | 100851 | 0 | 0.00% |
| with_mapped_origin | 100417 | 434 | 0.43% |
| with_mapped_destination | 37770 | 62647 | 62.39% |
| after_removing_domestic_moves | 16399 | 21222 | 56.19% |
| panel_talent_target_sum | 16399 | 0 | 0.00% |

The final two numbers match exactly: 16,399 rows remain after removing domestic moves and the panel target sum is also 16,399. Domestic moves are excluded from the T1 target, while the panel value is the aggregated pair-year total used in the talent panel.

## 4) Domestic moves in T1 target

Domestic moves are currently excluded from the T1 target. Among rows with a mapped destination, there are 21,222 origin == destination rows, and they are outside the target. The retained non-domestic count is 16,399.

## 5) Placeholder destinations and missing competitions

- Placeholder club names like Retired / Without Club / Unknown / No Club / Clubless / Free Agent: 1338 rows
- Clubs with no competition: 62272 rows
- Rows excluded because the destination club is placeholder-like or has no competition: 62272 rows

## 6) Coverage drift

| destination_iso3 | year | cross_border_transfers |
| --- | ---: | ---: |
| ARG | 2005 | 3 |
| ARG | 2007 | 1 |
| ARG | 2008 | 1 |
| ARG | 2009 | 3 |
| ARG | 2010 | 2 |
| ARG | 2011 | 4 |
| ARG | 2012 | 7 |
| ARG | 2013 | 4 |
| ARG | 2014 | 5 |
| ARG | 2015 | 12 |
| AUS | 2007 | 1 |
| AUS | 2008 | 1 |
| AUS | 2010 | 1 |
| AUS | 2012 | 4 |
| AUS | 2013 | 5 |
| AUS | 2015 | 3 |
| AUS | 2016 | 4 |
| AUS | 2017 | 6 |
| AUS | 2018 | 7 |
| AUS | 2019 | 9 |

The heatmap image is saved at [03b_coverage_heatmap.png](./figures/03b_coverage_heatmap.png). Destination-years with fewer than 20 transfers are masked in the heatmap as requested.

## 7) Fixtures: friendly vs competitive

- Friendly raw rows: 18258
- Competitive raw rows: 31682
- Friendly zero share in exported panel: 99.13%
- Competitive zero share in exported panel: 98.55%
- Friendly non-zero rows: 7823
- Competitive non-zero rows: 13020

The friendly label used in the code is exactly `Friendly`. Wales and Northern Ireland are merged to `GBR`, and `GBR-GBR` fixture pairs are dropped before aggregation.

## 8) Phase 1-2 leftovers

- Full unmatched football-name table rows: 97
- Full unmatched COW-code table rows: 22
- Rows with `is_continuator_mapped = True`: 6
- Actual last year in `gml-ndy-2.2.1.csv`: 2010
- Conflict column names used: ccode1, ccode2, year, midongoing, midonset, dispnum, fatality, fatalpre, hiact, hostlev, outcome, ongo2010

## 9) Zero-fill rule

The saved panels are full zero-fill grids: every country-pair-year in the selected analytic universe is present even when the count is zero. That means the panel includes structural zeros, not just observed pairs. This is compatible with the zero-fill design, but it does not satisfy the stricter “pairs that did not exist that year must be absent, not zero” rule in the current exports.
