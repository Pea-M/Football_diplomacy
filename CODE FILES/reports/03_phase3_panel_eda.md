# Phase 3 panel and EDA summary

This phase created the zero-filled panel objects for the talent and fixture targets and wrote the first plain-English diagnostics.

## Files created
- dataset/interim/panel_talent.parquet
- dataset/interim/panel_fixtures.parquet
- CODE FILES/reports/03_phase3_panel_eda_summary.csv
- CODE FILES/reports/figures/phase3_zero_share.png
- CODE FILES/reports/figures/phase3_top_talent_pairs.png
- CODE FILES/reports/figures/phase3_top_fixture_pairs.png
- CODE FILES/reports/figures/phase3_yearly_trends.png
- CODE FILES/reports/figures/phase3_missingness.png

## Plain-English readout
- Talent flows have a zero share of 99.6%. This means most directed country-pairs are inactive in a given year, which is expected in a sparse transfer panel.
- Fixtures have a zero share of 97.7%. The fixture panel is also sparse because most country pairs do not meet in a given year.
- The largest talent-flow origin was BRA and the largest destination was GBR. These values are taken from the full zero-filled panel totals, not from raw rows only.
- The busiest fixture pair was ('MEX', 'USA'). A few repeated dyads dominate the match totals, while most pairs are zero in most years.
- Missingness is near zero after zero-filling, which is the correct pattern for a panel intended for later model training and lagged geopolitics joins.

## What worries me
- The zero-filled panel is intentionally sparse, and this could make the early model baselines look unstable if the universe is too broad.
- The directed talent panel is built over the full country universe, so a few very active countries can dominate the totals even when many country pairs are zero.
