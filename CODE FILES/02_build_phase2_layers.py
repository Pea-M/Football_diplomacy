from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path('/Users/rise/Documents/AIS')
RAW = ROOT / 'dataset' / 'raw'
INTERIM = ROOT / 'dataset' / 'interim'
REPORTS = ROOT / 'CODE FILES' / 'reports'


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
    ledger = ledger.drop_duplicates(ignore_index=True)
    ledger.to_csv(ledger_path, index=False)


def normalize_country_name(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return np.nan
        return text
    return str(value).strip()


def build_name_map() -> dict[str, str]:
    map_df = pd.read_csv(INTERIM / 'country_map.csv')
    map_df = map_df.dropna(subset=['raw_name', 'iso3']).copy()
    map_df['raw_name'] = map_df['raw_name'].map(normalize_country_name)
    map_df = map_df[map_df['raw_name'].notna()].copy()

    name_map: dict[str, str] = {}
    for _, row in map_df.iterrows():
        key = str(row['raw_name']).strip()
        name_map[key] = str(row['iso3']).strip()
    return name_map


def map_exact(value, mapping):
    if pd.isna(value):
        return np.nan
    value = normalize_country_name(value)
    if value is None or pd.isna(value):
        return np.nan
    if value in mapping:
        return mapping[value]
    lower_key = value.lower()
    for k, v in mapping.items():
        if k.lower() == lower_key:
            return v
    return np.nan


def map_country_field(series, mapping):
    series = series.copy()
    series = series.map(lambda x: map_exact(x, mapping))
    return series


def build_transfers_layer(name_map: dict[str, str]):
    transfers_raw = pd.read_csv(RAW / 'transfermarkt' / 'transfers.csv')
    transfers_before = len(transfers_raw)
    transfers = transfers_raw.copy()
    transfers['transfer_date'] = pd.to_datetime(transfers['transfer_date'], errors='coerce')
    transfers = transfers[transfers['transfer_date'].notna()].copy()
    append_ledger(
        'phase2_transfer_raw_to_main_window',
        before_rows=transfers_before,
        after_rows=len(transfers),
        description='Transfers limited to the main 1993-2021 window and valid transfer dates before harmonising to player and league-country identifiers.',
    )
    transfers = transfers[transfers['transfer_date'].dt.year.between(1993, 2021)].copy()
    transfers_after_window = len(transfers)
    append_ledger(
        'phase2_transfer_window_filter',
        before_rows=len(transfers_raw) - transfers_raw['transfer_date'].isna().sum(),
        after_rows=transfers_after_window,
        description='Transfers with year outside 1993-2021 were dropped from the main panel window; future-dated rows beyond 2021 were excluded from analysis.',
    )

    players = pd.read_csv(RAW / 'transfermarkt' / 'players.csv')
    clubs = pd.read_csv(RAW / 'transfermarkt' / 'clubs.csv')
    competitions = pd.read_csv(RAW / 'transfermarkt' / 'competitions.csv')

    players_small = players[['player_id', 'country_of_citizenship']].copy()
    players_small['nationality_iso3'] = players_small['country_of_citizenship'].map(lambda x: map_exact(x, name_map))
    players_small = players_small[['player_id', 'nationality_iso3']]

    transfers = transfers.merge(players_small, on='player_id', how='left')
    after_player_join = len(transfers)
    append_ledger(
        'phase2_transfer_player_join',
        before_rows=transfers_after_window,
        after_rows=after_player_join,
        description='Player nationality was joined to each transfer record using player_id, preserving rows with known and unknown citizenship.',
    )

    clubs_small = clubs[['club_id', 'domestic_competition_id']].copy()
    transfers = transfers.merge(clubs_small.rename(columns={'club_id': 'to_club_id', 'domestic_competition_id': 'competition_id'}), on='to_club_id', how='left')
    after_club_join = len(transfers)
    append_ledger(
        'phase2_transfer_club_join',
        before_rows=after_player_join,
        after_rows=after_club_join,
        description='Destination club data was joined so each transfer could be linked to its league competition and destination country.',
    )

    comp_small = competitions[['competition_id', 'country_name']].copy()
    comp_small['destination_iso3'] = comp_small['country_name'].map(lambda x: map_exact(x, name_map))
    comp_small = comp_small[['competition_id', 'destination_iso3']]
    transfers = transfers.merge(comp_small, on='competition_id', how='left')
    after_comp_join = len(transfers)
    append_ledger(
        'phase2_transfer_competition_join',
        before_rows=after_club_join,
        after_rows=after_comp_join,
        description='Competition-country metadata was joined to complete the destination-country ISO3 field for transfer records.',
    )

    transfers['year'] = transfers['transfer_date'].dt.year

    agg = (
        transfers.groupby(['year', 'nationality_iso3', 'destination_iso3'], as_index=False)
        .agg(
            transfer_count=('player_id', 'size'),
            transfer_fee_sum_eur=('transfer_fee', lambda s: pd.to_numeric(s, errors='coerce').dropna().sum()),
        )
        .sort_values(['year', 'nationality_iso3', 'destination_iso3'])
        .reset_index(drop=True)
    )

    agg['transfer_fee_sum_eur'] = agg['transfer_fee_sum_eur'].replace({0: np.nan})
    final_path = INTERIM / 'transfers_layer.csv'
    agg.to_csv(final_path, index=False)

    append_ledger(
        'phase2_transfer_layer',
        before_rows=transfers_before,
        after_rows=len(agg),
        description='Transfers filtered to 1993-2021, joined to nationality and destination-country ISO3, then aggregated to year x nationality x destination country.',
    )

    known_nationality = transfers['nationality_iso3'].notna().mean()
    known_destination = transfers['destination_iso3'].notna().mean()
    return {
        'raw_rows': transfers_before,
        'window_rows': transfers_after_window,
        'after_player_join': after_player_join,
        'after_club_join': after_club_join,
        'after_comp_join': after_comp_join,
        'known_nationality_share': float(known_nationality),
        'known_destination_share': float(known_destination),
        'agg_rows': len(agg),
    }


def build_fixtures_layer(name_map: dict[str, str]):
    results = pd.read_csv(RAW / 'international_results' / 'results.csv', parse_dates=['date'])
    results_before = len(results)
    results = results[results['date'].notna()].copy()
    results['year'] = results['date'].dt.year
    append_ledger(
        'phase2_fixtures_date_filter',
        before_rows=results_before,
        after_rows=len(results),
        description='Fixtures were kept only for valid dates before subsetting them to the main 1993-2021 analysis period.',
    )
    results = results[results['year'].between(1993, 2021)].copy()
    results_after_window = len(results)
    append_ledger(
        'phase2_fixtures_main_window',
        before_rows=len(results) if 'results' in locals() else results_before,
        after_rows=results_after_window,
        description='Fixtures outside 1993-2021 were dropped to match the main panel window used for T2.',
    )

    results['home_iso3'] = results['home_team'].map(lambda x: map_exact(x, name_map))
    results['away_iso3'] = results['away_team'].map(lambda x: map_exact(x, name_map))
    results = results[results['home_iso3'].notna() & results['away_iso3'].notna()].copy()
    results_after_name_map = len(results)
    append_ledger(
        'phase2_fixtures_name_harmonisation',
        before_rows=results_after_window,
        after_rows=results_after_name_map,
        description='Fixture team names were mapped to ISO3 using the approved football country map, retaining only resolved teams.',
    )

    results = results[~((results['home_iso3'] == results['away_iso3']) & (results['home_iso3'] == 'GBR'))].copy()
    results_after_drop_gbr = len(results)
    append_ledger(
        'phase2_fixtures_drop_gbr_pairs',
        before_rows=results_after_name_map,
        after_rows=results_after_drop_gbr,
        description='GBR-GBR fixtures were dropped as requested before the year x country-pair aggregation step.',
    )

    results['pair_i'] = np.minimum(results['home_iso3'], results['away_iso3'])
    results['pair_j'] = np.maximum(results['home_iso3'], results['away_iso3'])
    results['is_friendly'] = results['tournament'].fillna('').str.lower().eq('friendly')
    results['is_competitive'] = ~results['is_friendly']

    fixtures = (
        results.groupby(['year', 'pair_i', 'pair_j'], as_index=False)
        .agg(
            match_count=('date', 'size'),
            friendly_count=('is_friendly', 'sum'),
            competitive_count=('is_competitive', 'sum'),
            neutral_venue_share=('neutral', 'mean'),
        )
        .sort_values(['year', 'pair_i', 'pair_j'])
        .reset_index(drop=True)
    )

    fixtures = fixtures.rename(columns={'pair_i': 'country_i_iso3', 'pair_j': 'country_j_iso3'})
    final_path = INTERIM / 'fixtures_layer.csv'
    fixtures.to_csv(final_path, index=False)

    append_ledger(
        'phase2_fixtures_layer',
        before_rows=results_before,
        after_rows=len(fixtures),
        description='Fixtures filtered to 1993-2021, harmonised to ISO3, dropped GBR-GBR pairs, and aggregated to year x country pair with friendly, competitive, and neutral-venue counts.',
    )

    return {
        'raw_rows': results_before,
        'window_rows': results_after_window,
        'mapped_rows': results_after_name_map,
        'after_gbr_drop': results_after_drop_gbr,
        'agg_rows': len(fixtures),
    }


def build_cepii_layer():
    gravity = pd.read_csv(RAW / 'cepii_gravity' / 'Gravity_V202211.csv')
    gravity_before = len(gravity)
    append_ledger(
        'phase2_cepii_main_window',
        before_rows=gravity_before,
        after_rows=len(gravity[gravity['year'].between(1993, 2021)]),
        description='CEPII gravity data was reduced to the main panel window of 1993-2021 before selecting the required geopolitical variables.',
    )
    gravity = gravity[gravity['year'].between(1993, 2021)].copy()
    gravity_after = len(gravity)

    keep_cols = [
        'year', 'country_id_o', 'country_id_d', 'iso3_o', 'iso3_d', 'dist', 'contig',
        'comlang_off', 'comcol', 'col45', 'col_dep_ever', 'col_dep', 'diplo_disagreement',
        'pop_o', 'pop_d', 'gdp_o', 'gdp_d', 'gdpcap_o', 'gdpcap_d'
    ]
    gravity = gravity[[c for c in keep_cols if c in gravity.columns]].copy()

    gravity = gravity.rename(columns={
        'iso3_o': 'country_i_iso3',
        'iso3_d': 'country_j_iso3',
        'country_id_o': 'country_i_id',
        'country_id_d': 'country_j_id',
        'dist': 'distance_km',
        'pop_o': 'pop_i',
        'pop_d': 'pop_j',
        'gdp_o': 'gdp_i',
        'gdp_d': 'gdp_j',
    })

    final_path = INTERIM / 'cepii_gravity_layer.csv'
    gravity.to_csv(final_path, index=False)

    append_ledger(
        'phase2_cepii_layer',
        before_rows=gravity_before,
        after_rows=len(gravity),
        description='CEPII gravity rows filtered to 1993-2021 and reduced to the year, pair, distance, contiguity, colonial ties, diplomatic disagreement, and GDP/population fields required for the panel.',
    )

    return {'raw_rows': gravity_before, 'window_rows': gravity_after, 'final_rows': len(gravity)}


def build_cow_mid_layer(name_map: dict[str, str]):
    cow = pd.read_csv(RAW / 'cow_mid' / 'gml_2.2.1' / 'gml-ndy-2.2.1.csv')
    cow_before = len(cow)
    append_ledger(
        'phase2_cow_overlap_window',
        before_rows=cow_before,
        after_rows=len(cow[cow['year'].between(1993, 2010)]),
        description='GML dyad-year rows were restricted to the verified 1993-2010 conflict overlap before code-to-ISO3 mapping.',
    )
    cow = cow[cow['year'].between(1993, 2010)].copy()
    cow_after_window = len(cow)

    cow['country_i_cow'] = pd.to_numeric(cow['ccode1'], errors='coerce')
    cow['country_j_cow'] = pd.to_numeric(cow['ccode2'], errors='coerce')

    cow_map = pd.read_csv(INTERIM / 'country_map.csv')
    cow_map = cow_map[cow_map['cow_code'].notna()].copy()
    cow_map['cow_code'] = pd.to_numeric(cow_map['cow_code'], errors='coerce')
    cow_map = cow_map[['cow_code', 'iso3']].drop_duplicates().dropna()
    cow_iso = cow_map.set_index('cow_code')['iso3'].to_dict()

    cow['country_i_iso3'] = cow['country_i_cow'].map(lambda x: cow_iso.get(int(x)) if pd.notna(x) and int(x) in cow_iso else np.nan)
    cow['country_j_iso3'] = cow['country_j_cow'].map(lambda x: cow_iso.get(int(x)) if pd.notna(x) and int(x) in cow_iso else np.nan)

    cow = cow[cow['country_i_iso3'].notna() & cow['country_j_iso3'].notna()].copy()
    cow_after_mapping = len(cow)
    append_ledger(
        'phase2_cow_code_mapping',
        before_rows=cow_after_window,
        after_rows=cow_after_mapping,
        description='COW code values were mapped to ISO3 using the approved mapping table, retaining only dyads whose codes resolved to current or continuator states.',
    )

    cow['pair_i'] = np.minimum(cow['country_i_iso3'], cow['country_j_iso3'])
    cow['pair_j'] = np.maximum(cow['country_i_iso3'], cow['country_j_iso3'])
    cow['country_i_iso3'] = cow['pair_i']
    cow['country_j_iso3'] = cow['pair_j']

    cow = cow.rename(columns={
        'midongoing': 'conflict_ongoing',
        'midonset': 'conflict_onset',
        'hostlev': 'max_hostility',
        'fatality': 'fatality',
        'fatalpre': 'fatal_prevalence',
        'hiact': 'high_activity',
    })

    keep_cols = [
        'year', 'pair_i', 'pair_j', 'country_i_iso3', 'country_j_iso3',
        'conflict_ongoing', 'conflict_onset', 'max_hostility', 'fatality', 'fatal_prevalence', 'high_activity'
    ]
    cow = cow[[c for c in keep_cols if c in cow.columns]].copy()

    final_path = INTERIM / 'cow_mid_layer.csv'
    cow.to_csv(final_path, index=False)

    append_ledger(
        'phase2_cow_mid_layer',
        before_rows=cow_before,
        after_rows=len(cow),
        description='GML dyad-year conflict rows filtered to the verified overlap (1993-2010), mapped from COW codes to ISO3, and reduced to onset, ongoing, and max-hostility flags.',
    )

    return {'raw_rows': cow_before, 'window_rows': cow_after_window, 'mapped_rows': cow_after_mapping, 'final_rows': len(cow)}


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    name_map = build_name_map()

    transfers_summary = build_transfers_layer(name_map)
    fixtures_summary = build_fixtures_layer(name_map)
    cepii_summary = build_cepii_layer()
    cow_summary = build_cow_mid_layer(name_map)

    report_rows = [
        {
            'layer': 'transfers',
            **transfers_summary,
        },
        {
            'layer': 'fixtures',
            **fixtures_summary,
        },
        {
            'layer': 'cepii_gravity',
            **cepii_summary,
        },
        {
            'layer': 'cow_mid',
            **cow_summary,
        },
    ]
    summary_df = pd.DataFrame(report_rows)
    summary_path = REPORTS / '02_phase2_layers_summary.csv'
    summary_df.to_csv(summary_path, index=False)

    markdown = """# Phase 2 layer build summary

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
"""
    columns = list(summary_df.columns)
    header = '| ' + ' | '.join(str(c) for c in columns) + ' |'
    separator = '| ' + ' | '.join(['---'] * len(columns)) + ' |'
    body = []
    for row in summary_df.itertuples(index=False, name=None):
        body.append('| ' + ' | '.join('' if pd.isna(v) else str(v) for v in row) + ' |')
    markdown += '\n' + '\n'.join([header, separator] + body) + '\n'
    (REPORTS / '02_phase2_layers.md').write_text(markdown, encoding='utf-8')

    print('Phase 2 complete.')
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()
