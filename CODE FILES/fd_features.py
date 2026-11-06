"""
Football Diplomacy - STEP 1 of 3: build the modelling tables ONCE (replaces the 4A data prep).

Every feature comes from year t-1 and is attached to target year t (no leakage).
Fixes vs the earlier 4A script:
  - CEPII and conflict features are now LAGGED (were same-year).
  - lag_reverse_flow is the real j->i flow (was a copy of lag_target).
  - Conflict is joined via COW code -> ISO3 (was never matching, so all NaN).
  - same_confederation is NaN when unknown (was 1 for every unmatched pair).
  - T2 country match totals count both sides of a pair (were half-counted).
  - T2 gravity features are symmetric (gdp sum / abs diff), as the pair is unordered.
  - CEPII is read once with only the needed columns and cached (was the main slowdown).

Outputs:
  dataset/processed/model_T1.parquet, model_T2.parquet, meta.json
  CODE FILES/reports/06_features_check.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ===================== SETTINGS: the bot may edit ONLY this block =====================
ROOT = Path('/Users/rise/Documents/AIS')
RAW = ROOT / 'dataset' / 'raw'
INTERIM = ROOT / 'dataset' / 'interim'
PROCESSED = ROOT / 'dataset' / 'processed'
REPORTS = ROOT / 'CODE FILES' / 'reports'

PANEL_T1 = INTERIM / 'panel_talent.parquet'      # point to the *_v2 file if one exists
PANEL_T2 = INTERIM / 'panel_fixtures.parquet'
I, J, Y = 'country_i_iso3', 'country_j_iso3', 'year'
T1_TARGET = 'talent_flow_count'
T2_TARGET, T2_COMP, T2_ALL = 'friendly_count', 'competitive_count', 'match_count'
LEAGUE_ISO3 = ['ARG','AUS','AUT','BEL','BRA','HRV','CZE','DNK','GBR','FRA','DEU','GRC','ITA','JPN','KOR','MEX','NLD','NOR','POL','PRT','ROU','RUS','SAU','SRB','ESP','SWE','CHE','TUR','UKR','USA']

CEPII_CSV = RAW / 'cepii_gravity' / 'Gravity_V202211.csv'
GML_CSV = RAW / 'cow_mid' / 'gml_2.2.1' / 'gml-ndy-2.2.1.csv'
GML_COLS = {'midonset': 'conflict_onset', 'midongoing': 'conflict_ongoing', 'hostlev': 'max_hostility'}
COW_MAP = INTERIM / 'cow_to_iso3.csv'     # columns: ccode, iso3, and EITHER year OR start_year + end_year
CONFED_MAP = INTERIM / 'confed_map.csv'   # columns: iso3, confederation
FIRST_TARGET_YEAR, LAST_TARGET_YEAR = 1994, 2021
# =====================================================================================

CONF_OUT = list(GML_COLS.values())


def pos_log(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors='coerce')
    return np.log(s.where(s > 0))


def pair_key(a: pd.Series, b: pd.Series) -> np.ndarray:
    a, b = a.astype(str), b.astype(str)
    return np.where(a <= b, a + '|' + b, b + '|' + a)


def load_cepii() -> pd.DataFrame:
    cache = INTERIM / 'cepii_slim.parquet'
    if cache.exists():
        return pd.read_parquet(cache)
    wanted = ['year', 'iso3_o', 'iso3_d', 'distw_harmonic', 'dist', 'contig', 'comlang_off',
              'gdp_o', 'gdp_d', 'pop_o', 'pop_d', 'fta_wto', 'rta_coverage', 'eu_o', 'eu_d',
              'wto_o', 'wto_d', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever']
    header = pd.read_csv(CEPII_CSV, nrows=0).columns
    use = [c for c in wanted if c in header]
    try:
        c = pd.read_csv(CEPII_CSV, usecols=use, engine='pyarrow')
    except Exception:
        c = pd.read_csv(CEPII_CSV, usecols=use, low_memory=False)
    c = c[c['year'].between(FIRST_TARGET_YEAR - 1, LAST_TARGET_YEAR - 1)].copy()
    c.to_parquet(cache, index=False)
    return c


def cepii_features(c: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    f = pd.DataFrame({Y: c['year'].astype(int) + 1,          # t-1 values -> target year t
                      I: c['iso3_o'].astype(str), J: c['iso3_d'].astype(str)})
    dist = c['distw_harmonic'] if 'distw_harmonic' in c else c['dist']
    if 'dist' in c:
        dist = dist.fillna(c['dist'])
    f['log_distw'] = pos_log(dist)
    for k in ['contig', 'comlang_off', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever', 'wto_o', 'wto_d']:
        f[k] = pd.to_numeric(c[k], errors='coerce')
    for v in ['gdp', 'pop']:
        f[f'log_{v}_o'] = pos_log(c[f'{v}_o'])
        f[f'log_{v}_d'] = pos_log(c[f'{v}_d'])
    if 'fta_wto' in c:
        f['rta'] = pd.to_numeric(c['fta_wto'], errors='coerce')
    else:
        f['rta'] = (pd.to_numeric(c['rta_coverage'], errors='coerce') > 0).astype(float)
    f['eu'] = ((pd.to_numeric(c['eu_o'], errors='coerce') == 1)
               & (pd.to_numeric(c['eu_d'], errors='coerce') == 1)).astype(float)
    n0 = len(f)
    f = f.drop_duplicates([Y, I, J])
    return f, n0 - len(f)


def conflict_features():
    if not COW_MAP.exists():
        return None, None, 'WARNING: cow_to_iso3.csv not found - conflict features are all NaN'
    g = pd.read_csv(GML_CSV, usecols=['ccode1', 'ccode2', 'year', *GML_COLS])
    gml_last = int(g['year'].max())
    m = pd.read_csv(COW_MAP)
    if 'year' not in m.columns:
        s = m['start_year'].fillna(1816).astype(int)
        e = m['end_year'].fillna(2030).astype(int)
        m = m.assign(year=[list(range(a, b + 1)) for a, b in zip(s, e)]).explode('year')
    m = m[['ccode', 'iso3', 'year']].dropna()
    m['year'] = m['year'].astype(int)
    m['ccode'] = m['ccode'].astype(int)
    m = m.drop_duplicates(['ccode', 'year'])
    n_raw = len(g)
    g = g.merge(m.rename(columns={'ccode': 'ccode1', 'iso3': 'iso_a'}), on=['ccode1', 'year'], how='inner')
    g = g.merge(m.rename(columns={'ccode': 'ccode2', 'iso3': 'iso_b'}), on=['ccode2', 'year'], how='inner')
    g['pair_key'] = pair_key(g['iso_a'], g['iso_b'])
    g = g.rename(columns=GML_COLS).groupby(['pair_key', 'year'], as_index=False)[CONF_OUT].max()
    g['year'] = g['year'] + 1                                 # t-1 -> t
    g = g.rename(columns={'year': Y})
    return g, gml_last, f'GML dyad-years: {n_raw:,} raw -> {len(g):,} mapped to ISO3 pairs; GML last year = {gml_last}'


def keep_existing(p, cep, log, name):
    alive = cep[[Y, I]].drop_duplicates().assign(_ok=1)
    n, flows = len(p), p.iloc[:, 3].sum()
    p = p.merge(alive.rename(columns={'_ok': '_oi'}), on=[Y, I], how='left')
    p = p.merge(alive.rename(columns={I: J, '_ok': '_oj'}), on=[Y, J], how='left')
    p = p[p['_oi'].notna() & p['_oj'].notna()].drop(columns=['_oi', '_oj'])
    log.append(f'{name}: existence filter kept {len(p):,} of {n:,} rows; target kept {p.iloc[:, 3].sum():,} of {flows:,}')
    return p


def add_target_lags(p: pd.DataFrame, target: str, directed: bool) -> pd.DataFrame:
    prev = p[[I, J, Y, target]].copy()
    prev[Y] += 1
    p = p.merge(prev.rename(columns={target: 'lag_target'}), on=[I, J, Y], how='left')
    if directed:
        rev = prev.rename(columns={I: J, J: I, target: 'lag_reverse_flow'})
        p = p.merge(rev, on=[I, J, Y], how='left')
        p['log1p_lag_reverse'] = np.log1p(p['lag_reverse_flow'])
    p['log1p_lag_target'] = np.log1p(p['lag_target'])
    return p


def lagged_total(p: pd.DataFrame, by: str, value: str, name: str) -> pd.DataFrame:
    t = p.groupby([by, Y], as_index=False)[value].sum()
    t[Y] += 1
    return t.rename(columns={value: name})


def build_t1(cep, conf, log) -> pd.DataFrame:
    p = pd.read_parquet(PANEL_T1)[[I, J, Y, T1_TARGET]].copy()
    p[I], p[J] = p[I].astype(str), p[J].astype(str)
    n = len(p)
    dom = int(p.loc[p[I] == p[J], T1_TARGET].sum())
    p = p[p[I] != p[J]]
    log.append(f'T1: dropped {n - len(p):,} domestic rows (origin == destination), carrying {dom:,} moves')
    p = p.groupby([I, J, Y], as_index=False)[T1_TARGET].sum()
    n0 = p[T1_TARGET].sum()
    p = p[p[J].isin(LEAGUE_ISO3)]
    log.append(f'T1: league-destination filter kept target {p[T1_TARGET].sum():,} of {n0:,}')
    p = keep_existing(p, cep, log, 'T1')
    p = add_target_lags(p, T1_TARGET, directed=True)
    p = p.merge(lagged_total(p, J, T1_TARGET, 'tot_in_dest'), on=[J, Y], how='left')
    p = p.merge(lagged_total(p, I, T1_TARGET, 'tot_out_orig'), on=[I, Y], how='left')
    p['log1p_tot_in_dest'] = np.log1p(p['tot_in_dest'])
    p['log1p_tot_out_orig'] = np.log1p(p['tot_out_orig'])
    p = p.merge(cep, on=[Y, I, J], how='left')
    p['pair_key'] = pair_key(p[I], p[J])
    if conf is not None:
        p = p.merge(conf, on=['pair_key', Y], how='left')
    else:
        p[CONF_OUT] = np.nan
    return p[p[Y].between(2010, LAST_TARGET_YEAR)].reset_index(drop=True)


def build_t2(cep, conf, log) -> pd.DataFrame:
    p = pd.read_parquet(PANEL_T2)[[I, J, Y, T2_TARGET, T2_COMP, T2_ALL]].copy()
    p[I], p[J] = p[I].astype(str), p[J].astype(str)
    p = p[p[I] != p[J]]
    a = np.where(p[I] <= p[J], p[I], p[J])
    b = np.where(p[I] <= p[J], p[J], p[I])
    p[I], p[J] = a, b
    n = len(p)
    p = p.groupby([I, J, Y], as_index=False)[[T2_TARGET, T2_COMP, T2_ALL]].max()
    log.append(f'T2: {n - len(p):,} duplicate rows collapsed by unordered pair (should be 0 if panel was undirected)')
    p = keep_existing(p, cep, log, 'T2')
    p = add_target_lags(p, T2_TARGET, directed=False)
    comp = p[[I, J, Y, T2_COMP]].copy()
    comp[Y] += 1
    p = p.merge(comp.rename(columns={T2_COMP: 'lag_competitive'}), on=[I, J, Y], how='left')
    p['log1p_lag_competitive'] = np.log1p(p['lag_competitive'])
    long = pd.concat([p[[I, Y, T2_ALL]].rename(columns={I: 'c'}), p[[J, Y, T2_ALL]].rename(columns={J: 'c'})])
    tot = long.groupby(['c', Y], as_index=False)[T2_ALL].sum()
    tot[Y] += 1
    for side in (I, J):
        p = p.merge(tot.rename(columns={'c': side, T2_ALL: f'tot_{side}'}), on=[side, Y], how='left')
    ti, tj = np.log1p(p[f'tot_{I}']), np.log1p(p[f'tot_{J}'])
    p['log1p_tot_matches_min'] = np.minimum(ti, tj)
    p['log1p_tot_matches_max'] = np.maximum(ti, tj)

    s = cep.copy()
    s['pair_key'] = pair_key(s[I], s[J])
    for v in ['gdp', 'pop']:
        s[f'log_{v}_sum'] = s[f'log_{v}_o'] + s[f'log_{v}_d']
        s[f'log_{v}_absdiff'] = (s[f'log_{v}_o'] - s[f'log_{v}_d']).abs()
    s['wto_both'] = s['wto_o'] * s['wto_d']
    sym = ['log_distw', 'contig', 'comlang_off', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever',
           'rta', 'eu', 'wto_both', 'log_gdp_sum', 'log_gdp_absdiff', 'log_pop_sum', 'log_pop_absdiff']
    s = s.groupby(['pair_key', Y], as_index=False)[sym].max()

    p['pair_key'] = pair_key(p[I], p[J])
    p = p.merge(s, on=['pair_key', Y], how='left')
    if conf is not None:
        p = p.merge(conf, on=['pair_key', Y], how='left')
    else:
        p[CONF_OUT] = np.nan
    if CONFED_MAP.exists():
        cm = pd.read_csv(CONFED_MAP)
        cm = dict(zip(cm['iso3'].astype(str), cm['confederation'].astype(str).str.upper().str.strip()))
        ci, cj = p[I].map(cm), p[J].map(cm)
        p['same_confederation'] = np.where(ci.isna() | cj.isna(), np.nan, (ci == cj).astype(float))
    else:
        p['same_confederation'] = np.nan
        log.append('WARNING: confed_map.csv not found - same_confederation is all NaN')
    return p[p[Y].between(FIRST_TARGET_YEAR, LAST_TARGET_YEAR)].reset_index(drop=True)


def pct(s: pd.Series) -> str:
    return f'{100 * s.notna().mean():.1f}%'


def check(name, p, target, directed, gml_last) -> list[str]:
    assert not p.duplicated([I, J, Y]).any(), f'{name}: duplicate pair-years'
    assert (p[I] != p[J]).all(), f'{name}: domestic rows present'
    by_year = p.groupby(Y)[target].sum()
    out = [f'## {name}',
           f'- rows {len(p):,} | years {p[Y].min()}-{p[Y].max()} | origins {p[I].nunique()} | '
           f'{"destinations" if directed else "second countries"} {p[J].nunique()} | pairs {p["pair_key"].nunique():,}',
           f'- non-zero rows {int((p[target] > 0).sum()):,} ({100 * (p[target] > 0).mean():.2f}%) | target total {int(p[target].sum()):,}',
           f'- target per year: first 3 {by_year.head(3).astype(int).to_dict()} | last 3 {by_year.tail(3).astype(int).to_dict()}',
           f'- coverage: distance {pct(p["log_distw"])} | UN disagreement {pct(p["diplo_disagreement"])} | lag_target {pct(p["lag_target"])}',
           f'- GBR present: {"GBR" in set(p[I]) | set(p[J])} | ENG/SCO present (should be False): {bool({"ENG", "SCO"} & (set(p[I]) | set(p[J])))}']
    if gml_last is not None:
        w = p[p[Y] <= gml_last + 1]
        out.append(f'- conflict coverage in target years <= {gml_last + 1}: {pct(w["conflict_onset"])}; '
                   f'pair-years with an ongoing MID: {int((w["conflict_ongoing"] > 0).sum())}')
    if directed:
        both = p[['lag_target', 'lag_reverse_flow']].dropna()
        corr = both.corr().iloc[0, 1] if len(both) > 2 else np.nan
        out.append(f'- destinations list: {sorted(p[J].unique())}')
        out.append(f'- lag_target vs lag_reverse_flow correlation (must be < 1): {corr:.3f}')
    else:
        out.append(f'- same_confederation coverage {pct(p["same_confederation"])}, share same {p["same_confederation"].mean():.2f}')
    return out


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    cep, dups = cepii_features(load_cepii())
    log.append(f'CEPII: {len(cep):,} lagged pair-years; {dups} duplicate pair-years dropped')
    conf, gml_last, msg = conflict_features()
    log.append(msg)
    t1 = build_t1(cep, conf, log)
    t2 = build_t2(cep, conf, log)
    t1.to_parquet(PROCESSED / 'model_T1.parquet', index=False)
    t2.to_parquet(PROCESSED / 'model_T2.parquet', index=False)
    (PROCESSED / 'meta.json').write_text(json.dumps({'gml_last_year': gml_last, 'rows_T1': len(t1), 'rows_T2': len(t2)}))
    lines = ['# Feature build check', ''] + [f'- {x}' for x in log] + ['']
    lines += check('T1 talent flows (directed)', t1, T1_TARGET, True, gml_last) + ['']
    lines += check('T2 friendlies (undirected)', t2, T2_TARGET, False, gml_last)
    text = '\n'.join(lines) + '\n'
    (REPORTS / '06_features_check.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()