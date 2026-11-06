from __future__ import annotations

from itertools import combinations, product
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path('/Users/rise/Documents/AIS')
RAW = ROOT / 'dataset' / 'raw'
INTERIM = ROOT / 'dataset' / 'interim'
REPORTS = ROOT / 'CODE FILES' / 'reports'
FIGURES = REPORTS / 'figures'


def append_ledger(step: str, before_rows: int, after_rows: int, description: str) -> None:
    ledger_path = INTERIM / 'row_ledger.csv'
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if ledger_path.exists():
        ledger = pd.read_csv(ledger_path)
    else:
        ledger = pd.DataFrame(columns=['step', 'before_rows', 'after_rows', 'description'])
    row = pd.DataFrame([{
        'step': step,
        'before_rows': int(before_rows),
        'after_rows': int(after_rows),
        'description': description,
    }])
    ledger = pd.concat([ledger, row], ignore_index=True)
    ledger.to_csv(ledger_path, index=False)


def build_country_universe() -> list[str]:
    cepp = pd.read_csv(RAW / 'cepii_gravity' / 'Countries_V202211.csv')
    cepp_iso = set(cepp['iso3'].dropna().astype(str))
    cargo = pd.read_csv(INTERIM / 'country_map.csv')
    map_iso = set(cargo['iso3'].dropna().astype(str))
    transfers = pd.read_csv(INTERIM / 'transfers_layer.csv')
    transfers_iso = set(transfers['nationality_iso3'].dropna().astype(str)) | set(transfers['destination_iso3'].dropna().astype(str))
    fixtures = pd.read_csv(INTERIM / 'fixtures_layer.csv')
    fixtures_iso = set(fixtures['country_i_iso3'].dropna().astype(str)) | set(fixtures['country_j_iso3'].dropna().astype(str))
    universe = sorted(cepp_iso | map_iso | transfers_iso | fixtures_iso)
    return universe


def build_talent_panel(country_universe: list[str], years: list[int]) -> pd.DataFrame:
    transfers = pd.read_csv(INTERIM / 'transfers_layer.csv')
    transfers_before = len(transfers)
    transfers = transfers.copy()
    transfers['year'] = pd.to_numeric(transfers['year'], errors='coerce').astype('Int64')
    transfers['nationality_iso3'] = transfers['nationality_iso3'].astype(str)
    transfers['destination_iso3'] = transfers['destination_iso3'].astype(str)
    transfers['transfer_count'] = pd.to_numeric(transfers['transfer_count'], errors='coerce').fillna(0).astype(float)
    transfers['transfer_fee_sum_eur'] = pd.to_numeric(transfers['transfer_fee_sum_eur'], errors='coerce').fillna(0)

    grid = pd.DataFrame(
        [(year, i, j) for year in years for i in country_universe for j in country_universe if i != j],
        columns=['year', 'country_i_iso3', 'country_j_iso3'],
    )
    before_grid = len(grid)
    merged = grid.merge(
        transfers[['year', 'nationality_iso3', 'destination_iso3', 'transfer_count', 'transfer_fee_sum_eur']].rename(
            columns={'nationality_iso3': 'country_i_iso3', 'destination_iso3': 'country_j_iso3'}
        ),
        on=['year', 'country_i_iso3', 'country_j_iso3'],
        how='left',
    )
    merged['talent_flow_count'] = merged['transfer_count'].fillna(0.0)
    merged['transfer_fee_sum_eur'] = merged['transfer_fee_sum_eur'].fillna(0.0)
    merged = merged[['year', 'country_i_iso3', 'country_j_iso3', 'talent_flow_count', 'transfer_fee_sum_eur']].copy()
    merged['has_flow'] = merged['talent_flow_count'] > 0
    merged['zero_fill_indicator'] = merged['talent_flow_count'] == 0
    append_ledger(
        'phase3_talent_panel_zero_fill',
        before_rows=transfers_before,
        after_rows=len(merged),
        description='Zero-filled directed talent panel built from the year x nationality x destination transfer layer for all non-self country pairs.',
    )
    return merged


def build_fixtures_panel(country_universe: list[str], years: list[int]) -> pd.DataFrame:
    fixtures = pd.read_csv(INTERIM / 'fixtures_layer.csv')
    fixtures_before = len(fixtures)
    fixtures = fixtures.copy()
    fixtures['year'] = pd.to_numeric(fixtures['year'], errors='coerce').astype('Int64')
    fixtures['country_i_iso3'] = fixtures['country_i_iso3'].astype(str)
    fixtures['country_j_iso3'] = fixtures['country_j_iso3'].astype(str)
    fixtures['match_count'] = pd.to_numeric(fixtures['match_count'], errors='coerce').fillna(0)
    fixtures['friendly_count'] = pd.to_numeric(fixtures['friendly_count'], errors='coerce').fillna(0)
    fixtures['competitive_count'] = pd.to_numeric(fixtures['competitive_count'], errors='coerce').fillna(0)
    fixtures['neutral_venue_share'] = pd.to_numeric(fixtures['neutral_venue_share'], errors='coerce').fillna(0.0)

    pair_frame = pd.DataFrame(
        [(year, a, b) for year in years for a, b in combinations(country_universe, 2)],
        columns=['year', 'country_i_iso3', 'country_j_iso3'],
    )
    pair_frame['country_i_iso3'] = pair_frame['country_i_iso3'].astype(str)
    pair_frame['country_j_iso3'] = pair_frame['country_j_iso3'].astype(str)
    pair_frame['country_i_iso3'], pair_frame['country_j_iso3'] = zip(*[
        tuple(sorted((a, b))) for a, b in zip(pair_frame['country_i_iso3'], pair_frame['country_j_iso3'])
    ])
    pair_frame = pair_frame[['year', 'country_i_iso3', 'country_j_iso3']]

    merged = pair_frame.merge(
        fixtures,
        on=['year', 'country_i_iso3', 'country_j_iso3'],
        how='left',
    )
    merged['match_count'] = merged['match_count'].fillna(0)
    merged['friendly_count'] = merged['friendly_count'].fillna(0)
    merged['competitive_count'] = merged['competitive_count'].fillna(0)
    merged['neutral_venue_share'] = merged['neutral_venue_share'].fillna(0.0)
    merged['has_fixture'] = merged['match_count'] > 0
    merged['zero_fill_indicator'] = merged['match_count'] == 0
    append_ledger(
        'phase3_fixtures_panel_zero_fill',
        before_rows=fixtures_before,
        after_rows=len(merged),
        description='Zero-filled undirected fixtures panel built from year x country-pair match totals for all country pairs in the analytic universe.',
    )
    return merged


def save_figures(talent_panel: pd.DataFrame, fixtures_panel: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    talent_zero_share = (talent_panel['talent_flow_count'] == 0).mean()
    fixture_zero_share = (fixtures_panel['match_count'] == 0).mean()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Talent', 'Fixtures'], [talent_zero_share, fixture_zero_share], color=['#4C78A8', '#F58518'])
    ax.set_title('Share of pair-years with zero flow/matches')
    ax.set_ylabel('Share')
    ax.set_ylim(0, 1.05)
    for p, v in zip(ax.patches, [talent_zero_share, fixture_zero_share]):
        ax.text(p.get_x() + p.get_width()/2, v + 0.02, f'{v:.1%}', ha='center', va='bottom')
    plt.tight_layout()
    fig.savefig(FIGURES / 'phase3_zero_share.png', dpi=200)
    plt.close(fig)

    talent_top = talent_panel[talent_panel['talent_flow_count'] > 0].groupby(['country_i_iso3', 'country_j_iso3'], as_index=False)['talent_flow_count'].sum().sort_values('talent_flow_count', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(talent_top['country_i_iso3'] + '->' + talent_top['country_j_iso3'], talent_top['talent_flow_count'], color='#4C78A8')
    ax.invert_yaxis()
    ax.set_title('Top talent-flow pairs (all years summed)')
    ax.set_xlabel('Transfers')
    plt.tight_layout()
    fig.savefig(FIGURES / 'phase3_top_talent_pairs.png', dpi=200)
    plt.close(fig)

    fixture_top = fixtures_panel[fixtures_panel['match_count'] > 0].groupby(['country_i_iso3', 'country_j_iso3'], as_index=False)['match_count'].sum().sort_values('match_count', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(fixture_top['country_i_iso3'] + '-' + fixture_top['country_j_iso3'], fixture_top['match_count'], color='#F58518')
    ax.invert_yaxis()
    ax.set_title('Top fixture pairs (all years summed)')
    ax.set_xlabel('Matches')
    plt.tight_layout()
    fig.savefig(FIGURES / 'phase3_top_fixture_pairs.png', dpi=200)
    plt.close(fig)

    talent_year = talent_panel.groupby('year', as_index=False)['talent_flow_count'].sum().rename(columns={'talent_flow_count': 'total_talent_flow'})
    fixture_year = fixtures_panel.groupby('year', as_index=False)['match_count'].sum().rename(columns={'match_count': 'total_matches'})
    trend = talent_year.merge(fixture_year, on='year', how='outer').sort_values('year')
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(trend['year'], trend['total_talent_flow'], color='#4C78A8', marker='o')
    axes[0].set_title('Talent flow trend by year')
    axes[0].set_ylabel('Transfers')
    axes[1].plot(trend['year'], trend['total_matches'], color='#F58518', marker='o')
    axes[1].set_title('Fixture count trend by year')
    axes[1].set_ylabel('Matches')
    axes[1].set_xlabel('Year')
    plt.tight_layout()
    fig.savefig(FIGURES / 'phase3_yearly_trends.png', dpi=200)
    plt.close(fig)

    missing_df = pd.DataFrame({
        'talent_flow_count': talent_panel['talent_flow_count'].isna().mean(),
        'transfer_fee_sum_eur': talent_panel['transfer_fee_sum_eur'].isna().mean(),
        'fixture_match_count': fixtures_panel['match_count'].isna().mean(),
        'fixture_friendly_count': fixtures_panel['friendly_count'].isna().mean(),
        'fixture_competitive_count': fixtures_panel['competitive_count'].isna().mean(),
        'fixture_neutral_venue_share': fixtures_panel['neutral_venue_share'].isna().mean(),
    }, index=['missing_share'])
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.heatmap(missing_df, annot=True, fmt='.2%', cmap='YlOrRd', cbar=False, ax=ax)
    ax.set_title('Missingness share in the panel inputs')
    plt.tight_layout()
    fig.savefig(FIGURES / 'phase3_missingness.png', dpi=200)
    plt.close(fig)


def build_summary(talent_panel: pd.DataFrame, fixtures_panel: pd.DataFrame) -> pd.DataFrame:
    talent_summary = {
        'panel': 'talent',
        'n_rows': int(len(talent_panel)),
        'non_zero_rows': int((talent_panel['talent_flow_count'] > 0).sum()),
        'zero_share': float((talent_panel['talent_flow_count'] == 0).mean()),
        'top_origin': talent_panel[talent_panel['talent_flow_count'] > 0].groupby('country_i_iso3')['talent_flow_count'].sum().idxmax() if (talent_panel['talent_flow_count'] > 0).any() else np.nan,
        'top_destination': talent_panel[talent_panel['talent_flow_count'] > 0].groupby('country_j_iso3')['talent_flow_count'].sum().idxmax() if (talent_panel['talent_flow_count'] > 0).any() else np.nan,
        'avg_flow': float(talent_panel['talent_flow_count'].mean()),
    }
    fixtures_summary = {
        'panel': 'fixtures',
        'n_rows': int(len(fixtures_panel)),
        'non_zero_rows': int((fixtures_panel['match_count'] > 0).sum()),
        'zero_share': float((fixtures_panel['match_count'] == 0).mean()),
        'top_pair': fixtures_panel[fixtures_panel['match_count'] > 0].groupby(['country_i_iso3', 'country_j_iso3'])['match_count'].sum().idxmax() if (fixtures_panel['match_count'] > 0).any() else np.nan,
        'avg_matches': float(fixtures_panel['match_count'].mean()),
    }
    summary = pd.DataFrame([talent_summary, fixtures_summary])
    summary.to_csv(REPORTS / '03_phase3_panel_eda_summary.csv', index=False)
    return summary


def write_markdown(summary: pd.DataFrame) -> None:
    talent = summary[summary['panel'] == 'talent'].iloc[0]
    fixtures = summary[summary['panel'] == 'fixtures'].iloc[0]
    text = f"""# Phase 3 panel and EDA summary

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
- Talent flows have a zero share of {talent['zero_share']:.1%}. This means most directed country-pairs are inactive in a given year, which is expected in a sparse transfer panel.
- Fixtures have a zero share of {fixtures['zero_share']:.1%}. The fixture panel is also sparse because most country pairs do not meet in a given year.
- The largest talent-flow origin was {talent['top_origin']} and the largest destination was {talent['top_destination']}. These values are taken from the full zero-filled panel totals, not from raw rows only.
- The busiest fixture pair was {fixtures['top_pair']}. A few repeated dyads dominate the match totals, while most pairs are zero in most years.
- Missingness is near zero after zero-filling, which is the correct pattern for a panel intended for later model training and lagged geopolitics joins.

## What worries me
- The zero-filled panel is intentionally sparse, and this could make the early model baselines look unstable if the universe is too broad.
- The directed talent panel is built over the full country universe, so a few very active countries can dominate the totals even when many country pairs are zero.
"""
    (REPORTS / '03_phase3_panel_eda.md').write_text(text, encoding='utf-8')


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    years = list(range(1993, 2022))
    country_universe = build_country_universe()

    talent_panel = build_talent_panel(country_universe, years)
    fixtures_panel = build_fixtures_panel(country_universe, years)

    talent_panel.to_parquet(INTERIM / 'panel_talent.parquet', index=False)
    fixtures_panel.to_parquet(INTERIM / 'panel_fixtures.parquet', index=False)

    append_ledger(
        'phase3_panel_exports',
        before_rows=len(talent_panel) + len(fixtures_panel),
        after_rows=len(talent_panel) + len(fixtures_panel),
        description='Directed and undirected zero-filled panel datasets were exported as Parquet files after the final fill step.',
    )

    save_figures(talent_panel, fixtures_panel)
    summary = build_summary(talent_panel, fixtures_panel)
    write_markdown(summary)

    print('Phase 3 complete.')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
