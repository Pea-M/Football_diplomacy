from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, mean_absolute_error
from sklearn.model_selection import GroupKFold

ROOT = Path('/Users/rise/Documents/AIS')
RAW = ROOT / 'dataset' / 'raw'
INTERIM = ROOT / 'dataset' / 'interim'
REPORTS = ROOT / 'CODE FILES' / 'reports'
RESULTS = ROOT / 'results'


def pair_key(a: str, b: str) -> tuple[str, str]:
    aa, bb = str(a), str(b)
    return (aa, bb) if aa <= bb else (bb, aa)


def append_ledger(step: str, before_rows: int, after_rows: int, description: str) -> None:
    ledger_path = INTERIM / 'row_ledger.csv'
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if ledger_path.exists():
        ledger = pd.read_csv(ledger_path)
    else:
        ledger = pd.DataFrame(columns=['step', 'before_rows', 'after_rows', 'description'])
    ledger = pd.concat([
        ledger,
        pd.DataFrame([{'step': step, 'before_rows': int(before_rows), 'after_rows': int(after_rows), 'description': description}])
    ], ignore_index=True)
    ledger.to_csv(ledger_path, index=False)


def prepare_t1_df() -> pd.DataFrame:
    df = pd.read_parquet(INTERIM / 'panel_talent.parquet').copy()
    df = df[df['year'].between(1994, 2021)].copy()
    df = df[df['country_i_iso3'] != df['country_j_iso3']].copy()
    df = df.sort_values(['country_i_iso3', 'country_j_iso3', 'year']).copy()
    df['pair_key'] = df.apply(lambda r: pair_key(r['country_i_iso3'], r['country_j_iso3']), axis=1)
    # lagged target and reverse-flow target
    df['lag_target'] = df.groupby(['country_i_iso3', 'country_j_iso3'])['talent_flow_count'].shift(1)
    df['lag_reverse_flow'] = df.groupby(['country_j_iso3', 'country_i_iso3'])['talent_flow_count'].shift(1)
    # lagged country totals used in the T1 features
    inflow = df.groupby(['year', 'country_j_iso3'], as_index=False)['talent_flow_count'].sum().rename(columns={'talent_flow_count': 'total_inflow_destination'})
    inflow['lag_total_inflow_destination'] = inflow.groupby('country_j_iso3')['total_inflow_destination'].shift(1)
    outflow = df.groupby(['year', 'country_i_iso3'], as_index=False)['talent_flow_count'].sum().rename(columns={'talent_flow_count': 'total_outflow_origin'})
    outflow['lag_total_outflow_origin'] = outflow.groupby('country_i_iso3')['total_outflow_origin'].shift(1)
    df = df.merge(inflow[['year', 'country_j_iso3', 'lag_total_inflow_destination']], on=['year', 'country_j_iso3'], how='left')
    df = df.merge(outflow[['year', 'country_i_iso3', 'lag_total_outflow_origin']], on=['year', 'country_i_iso3'], how='left')
    df['log_1p_inflow_to_destination'] = np.log1p(df['lag_total_inflow_destination'].fillna(0.0))
    df['log_1p_outflow_from_origin'] = np.log1p(df['lag_total_outflow_origin'].fillna(0.0))
    return df


def prepare_t2_df() -> pd.DataFrame:
    df = pd.read_parquet(INTERIM / 'panel_fixtures.parquet').copy()
    df = df[df['year'].between(1994, 2021)].copy()
    df = df[df['country_i_iso3'] != df['country_j_iso3']].copy()
    df = df.sort_values(['country_i_iso3', 'country_j_iso3', 'year']).copy()
    df['pair_key'] = df.apply(lambda r: pair_key(r['country_i_iso3'], r['country_j_iso3']), axis=1)
    df['lag_target'] = df.groupby('pair_key')['friendly_count'].shift(1)
    pair_comp = df.groupby(['pair_key', 'year'], as_index=False)['competitive_count'].sum().rename(columns={'competitive_count': 'competitive_matches_pair'})
    pair_comp['lag_competitive_matches_pair'] = pair_comp.groupby('pair_key')['competitive_matches_pair'].shift(1)
    df = df.merge(pair_comp[['year', 'pair_key', 'lag_competitive_matches_pair']], on=['year', 'pair_key'], how='left')
    matches_origin = df.groupby(['year', 'country_i_iso3'], as_index=False)['match_count'].sum().rename(columns={'match_count': 'total_matches_origin'})
    matches_origin['lag_total_matches_origin'] = matches_origin.groupby('country_i_iso3')['total_matches_origin'].shift(1)
    matches_dest = df.groupby(['year', 'country_j_iso3'], as_index=False)['match_count'].sum().rename(columns={'match_count': 'total_matches_destination'})
    matches_dest['lag_total_matches_destination'] = matches_dest.groupby('country_j_iso3')['total_matches_destination'].shift(1)
    df = df.merge(matches_origin[['year', 'country_i_iso3', 'lag_total_matches_origin']], on=['year', 'country_i_iso3'], how='left')
    df = df.merge(matches_dest[['year', 'country_j_iso3', 'lag_total_matches_destination']], on=['year', 'country_j_iso3'], how='left')
    df['log_1p_lagged_competitive'] = np.log1p(df['lag_competitive_matches_pair'].fillna(0.0))
    df['log_1p_total_matches_origin'] = np.log1p(df['lag_total_matches_origin'].fillna(0.0))
    df['log_1p_total_matches_destination'] = np.log1p(df['lag_total_matches_destination'].fillna(0.0))
    countries = pd.read_csv(RAW / 'transfermarkt' / 'countries.csv', low_memory=False)
    conf_map = {}
    for _, row in countries.iterrows():
        name = str(row.get('country_name', '')).strip()
        code = str(row.get('country_code', '')).strip()
        conf = str(row.get('confederation', '')).strip()
        if name:
            conf_map[name] = conf
        if code and code not in conf_map:
            conf_map[code] = conf
    df['same_confederation'] = df.apply(lambda r: int(conf_map.get(str(r['country_i_iso3']), '') == conf_map.get(str(r['country_j_iso3']), '')), axis=1)
    return df


def get_cepii(target: str) -> pd.DataFrame:
    cepii = pd.read_csv(RAW / 'cepii_gravity' / 'Gravity_V202211.csv', low_memory=False)
    cepii = cepii[cepii['year'].between(1994, 2021)].copy()
    cepii['country_i_iso3'] = cepii['iso3_o'].astype(str)
    cepii['country_j_iso3'] = cepii['iso3_d'].astype(str)
    cepii['log_distw'] = np.log(cepii['distw_harmonic'].combine_first(cepii['dist']).replace(0, np.nan))
    cepii['log_gdp_o'] = np.log(pd.to_numeric(cepii['gdp_o'], errors='coerce').replace(0, np.nan))
    cepii['log_gdp_d'] = np.log(pd.to_numeric(cepii['gdp_d'], errors='coerce').replace(0, np.nan))
    cepii['log_pop_o'] = np.log(pd.to_numeric(cepii['pop_o'], errors='coerce').replace(0, np.nan))
    cepii['log_pop_d'] = np.log(pd.to_numeric(cepii['pop_d'], errors='coerce').replace(0, np.nan))
    cepii['rta'] = pd.to_numeric(cepii['rta_coverage'], errors='coerce').fillna(0.0)
    cepii['eu'] = ((pd.to_numeric(cepii['eu_o'], errors='coerce').fillna(0) == 1) & (pd.to_numeric(cepii['eu_d'], errors='coerce').fillna(0) == 1)).astype(float)
    cepii['wto_o'] = pd.to_numeric(cepii['wto_o'], errors='coerce')
    cepii['wto_d'] = pd.to_numeric(cepii['wto_d'], errors='coerce')
    if target == 'T1':
        cols = ['year', 'country_i_iso3', 'country_j_iso3', 'log_distw', 'contig', 'comlang_off', 'log_gdp_o', 'log_gdp_d', 'log_pop_o', 'log_pop_d', 'rta', 'eu', 'wto_o', 'wto_d', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever']
        return cepii[cols].copy()
    cepii['pair_key'] = cepii.apply(lambda r: pair_key(r['country_i_iso3'], r['country_j_iso3']), axis=1)
    cepii = cepii.groupby(['year', 'pair_key'], as_index=False).first()
    cols = ['year', 'pair_key', 'log_distw', 'contig', 'comlang_off', 'log_gdp_o', 'log_gdp_d', 'log_pop_o', 'log_pop_d', 'rta', 'eu', 'wto_o', 'wto_d', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever']
    return cepii[cols].copy()


def get_conflict() -> pd.DataFrame:
    conflict = pd.read_csv(RAW / 'cow_mid' / 'gml_2.2.1' / 'gml-ndy-2.2.1.csv', low_memory=False)
    conflict = conflict[conflict['year'].between(1994, 2010)].copy()
    conflict['pair_key'] = conflict.apply(lambda r: pair_key(r['ccode1'], r['ccode2']), axis=1)
    conflict = conflict[['year', 'pair_key', 'midonset', 'midongoing', 'hostlev']].rename(columns={'midonset': 'conflict_onset', 'midongoing': 'conflict_ongoing', 'hostlev': 'max_hostility'})
    return conflict


def feature_columns(target: str, feature_set: str, with_lag: bool) -> list[str]:
    base = ['log_distw', 'contig', 'comlang_off', 'log_gdp_o', 'log_gdp_d', 'log_pop_o', 'log_pop_d', 'rta', 'eu', 'wto_o', 'wto_d']
    geop = ['diplo_disagreement', 'col45', 'comcol', 'col_dep_ever']
    if target == 'T1':
        extra = ['log_1p_inflow_to_destination', 'log_1p_outflow_from_origin']
    else:
        extra = ['same_confederation', 'log_1p_lagged_competitive', 'log_1p_total_matches_origin', 'log_1p_total_matches_destination']
    if feature_set == 'G':
        cols = base + extra
    elif feature_set == 'G+P':
        cols = base + geop + extra
    elif feature_set == 'G+P+C':
        cols = base + geop + extra + ['conflict_onset', 'conflict_ongoing', 'max_hostility']
    else:
        raise ValueError(feature_set)
    if with_lag:
        cols += ['lag_target'] + (['lag_reverse_flow'] if target == 'T1' else [])
    return cols


def poisson_deviance(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.where(y_true > 0, 2 * (y_true * np.log((y_true + 1e-9) / np.clip(y_pred, 1e-9, None)) - (y_true - y_pred)), 2 * np.clip(y_pred, 1e-9, None))))


def pr_auc(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if np.unique(y_true).size < 2:
        return 0.0
    return float(average_precision_score(y_true > 0, y_pred))


def spearman_safe(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.size == 0 or y_pred.size == 0:
        return 0.0
    if np.unique(y_true).size <= 1 or np.unique(y_pred).size <= 1:
        return 0.0
    corr = spearmanr(y_true, y_pred).correlation
    return 0.0 if pd.isna(corr) else float(corr)


def fit_glm(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series) -> np.ndarray:
    medians = X_train.median()
    X_train2 = X_train.fillna(medians)
    X_test2 = X_test.fillna(medians)
    miss_train = X_train.isna().astype(float).add_prefix('missing_')
    miss_test = X_test.isna().astype(float).add_prefix('missing_')
    X_train2 = pd.concat([X_train2, miss_train], axis=1)
    X_test2 = pd.concat([X_test2, miss_test], axis=1)
    X_train2 = X_train2.reindex(sorted(X_train2.columns), axis=1)
    X_test2 = X_test2.reindex(columns=X_train2.columns, fill_value=0.0)
    model = sm.GLM(y_train.astype(float), sm.add_constant(X_train2.astype(float), has_constant='add'), family=sm.families.Poisson()).fit()
    pred = model.predict(sm.add_constant(X_test2.astype(float), has_constant='add'))
    return np.asarray(pred, dtype=float)


def score(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return {
        'poisson_deviance': poisson_deviance(y_true, y_pred),
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'spearman': spearman_safe(y_true, y_pred),
        'pr_auc': pr_auc(y_true, y_pred),
    }


def prep_data(target: str) -> pd.DataFrame:
    df = prepare_t1_df() if target == 'T1' else prepare_t2_df()
    cepii = get_cepii(target)
    if target == 'T1':
        df = df.merge(cepii, on=['year', 'country_i_iso3', 'country_j_iso3'], how='left')
    else:
        df = df.merge(cepii, on=['year', 'pair_key'], how='left')
    conflict = get_conflict()
    df = df.merge(conflict, on=['year', 'pair_key'], how='left')
    return df


def evaluate_split(df: pd.DataFrame, target: str, feature_set: str, with_lag: bool, split_name: str, model: str) -> dict[str, float]:
    target_col = 'talent_flow_count' if target == 'T1' else 'friendly_count'
    X = df[feature_columns(target, feature_set, with_lag)].copy()
    y = df[target_col].astype(float)
    if split_name == 'time_split':
        train_mask = df['year'] <= 2016
        test_mask = df['year'].between(2017, 2019)
    elif split_name == 'covid_stress':
        train_mask = df['year'] <= 2019
        test_mask = df['year'].between(2020, 2021)
    elif split_name == 'conflict_window':
        train_mask = df['year'] <= 2007
        test_mask = df['year'].between(2008, 2010)
    else:
        raise ValueError(split_name)

    if model == 'Persistence':
        pred = df.loc[test_mask, 'lag_target'].fillna(0.0).to_numpy(dtype=float)
        y_true = df.loc[test_mask, target_col].to_numpy(dtype=float)
    else:
        pred = fit_glm(X.loc[train_mask].copy(), X.loc[test_mask].copy(), y.loc[train_mask].copy())
        y_true = y.loc[test_mask].to_numpy(dtype=float)

    return score(y_true, pred)


def evaluate_groupkfold(df: pd.DataFrame, target: str, feature_set: str, with_lag: bool) -> dict[str, float]:
    target_col = 'talent_flow_count' if target == 'T1' else 'friendly_count'
    df = df[df['year'].between(1994, 2019)].copy()
    X = df[feature_columns(target, feature_set, with_lag)].copy()
    y = df[target_col].astype(float)
    groups = df['pair_key']
    cv = GroupKFold(n_splits=5)
    fold_scores = []
    for tr, te in cv.split(X, y, groups):
        pred = fit_glm(X.iloc[tr].copy(), X.iloc[te].copy(), y.iloc[tr].copy())
        fold_scores.append(score(y.iloc[te].to_numpy(), pred))
    return {
        'poisson_deviance_mean': float(np.mean([s['poisson_deviance'] for s in fold_scores])),
        'poisson_deviance_std': float(np.std([s['poisson_deviance'] for s in fold_scores], ddof=1)) if len(fold_scores) > 1 else 0.0,
        'mae_mean': float(np.mean([s['mae'] for s in fold_scores])),
        'mae_std': float(np.std([s['mae'] for s in fold_scores], ddof=1)) if len(fold_scores) > 1 else 0.0,
        'spearman_mean': float(np.mean([s['spearman'] for s in fold_scores])),
        'spearman_std': float(np.std([s['spearman'] for s in fold_scores], ddof=1)) if len(fold_scores) > 1 else 0.0,
        'pr_auc_mean': float(np.mean([s['pr_auc'] for s in fold_scores])),
        'pr_auc_std': float(np.std([s['pr_auc'] for s in fold_scores], ddof=1)) if len(fold_scores) > 1 else 0.0,
    }


def build_results_table() -> pd.DataFrame:
    rows = []
    for target in ['T1', 'T2']:
        df = prep_data(target)
        for feature_set in ['G', 'G+P']:
            for with_lag in [False, True]:
                for split_name in ['time_split', 'covid_stress']:
                    stats = evaluate_split(df, target, feature_set, with_lag, split_name, 'PoissonGLM')
                    rows.append({
                        'target': target,
                        'feature_set': feature_set,
                        'with_lag': with_lag,
                        'split': split_name,
                        'model': 'PoissonGLM',
                        'poisson_deviance_mean': stats['poisson_deviance'],
                        'poisson_deviance_std': 0.0,
                        'mae_mean': stats['mae'],
                        'mae_std': 0.0,
                        'spearman_mean': stats['spearman'],
                        'spearman_std': 0.0,
                        'pr_auc_mean': stats['pr_auc'],
                        'pr_auc_std': 0.0,
                    })
                    if with_lag:
                        pers = evaluate_split(df, target, feature_set, with_lag, split_name, 'Persistence')
                        rows.append({
                            'target': target,
                            'feature_set': feature_set,
                            'with_lag': with_lag,
                            'split': split_name,
                            'model': 'Persistence',
                            'poisson_deviance_mean': pers['poisson_deviance'],
                            'poisson_deviance_std': 0.0,
                            'mae_mean': pers['mae'],
                            'mae_std': 0.0,
                            'spearman_mean': pers['spearman'],
                            'spearman_std': 0.0,
                            'pr_auc_mean': pers['pr_auc'],
                            'pr_auc_std': 0.0,
                        })
                gk = evaluate_groupkfold(df, target, feature_set, with_lag)
                rows.append({
                    'target': target,
                    'feature_set': feature_set,
                    'with_lag': with_lag,
                    'split': 'groupkfold',
                    'model': 'PoissonGLM',
                    'poisson_deviance_mean': gk['poisson_deviance_mean'],
                    'poisson_deviance_std': gk['poisson_deviance_std'],
                    'mae_mean': gk['mae_mean'],
                    'mae_std': gk['mae_std'],
                    'spearman_mean': gk['spearman_mean'],
                    'spearman_std': gk['spearman_std'],
                    'pr_auc_mean': gk['pr_auc_mean'],
                    'pr_auc_std': gk['pr_auc_std'],
                })
                if with_lag:
                    y_true = df[df['year'].between(1994, 2019)][f'{"talent_flow_count" if target == "T1" else "friendly_count"}'].to_numpy(dtype=float)
                    pred = df[df['year'].between(1994, 2019)]['lag_target'].fillna(0.0).to_numpy(dtype=float)
                    p = score(y_true, pred)
                    rows.append({
                        'target': target,
                        'feature_set': feature_set,
                        'with_lag': with_lag,
                        'split': 'groupkfold',
                        'model': 'Persistence',
                        'poisson_deviance_mean': p['poisson_deviance'],
                        'poisson_deviance_std': 0.0,
                        'mae_mean': p['mae'],
                        'mae_std': 0.0,
                        'spearman_mean': p['spearman'],
                        'spearman_std': 0.0,
                        'pr_auc_mean': p['pr_auc'],
                        'pr_auc_std': 0.0,
                    })
        # conflict-window ablation for G+P+C
        if target == 'T1':
            df_conf = df[df['year'].between(1994, 2010)].copy()
            for with_lag in [False, True]:
                stats = evaluate_split(df_conf, target, 'G+P+C', with_lag, 'conflict_window', 'PoissonGLM')
                rows.append({
                    'target': target,
                    'feature_set': 'G+P+C',
                    'with_lag': with_lag,
                    'split': 'conflict_window',
                    'model': 'PoissonGLM',
                    'poisson_deviance_mean': stats['poisson_deviance'],
                    'poisson_deviance_std': 0.0,
                    'mae_mean': stats['mae'],
                    'mae_std': 0.0,
                    'spearman_mean': stats['spearman'],
                    'spearman_std': 0.0,
                    'pr_auc_mean': stats['pr_auc'],
                    'pr_auc_std': 0.0,
                })
                if with_lag:
                    pers = evaluate_split(df_conf, target, 'G+P+C', with_lag, 'conflict_window', 'Persistence')
                    rows.append({
                        'target': target,
                        'feature_set': 'G+P+C',
                        'with_lag': with_lag,
                        'split': 'conflict_window',
                        'model': 'Persistence',
                        'poisson_deviance_mean': pers['poisson_deviance'],
                        'poisson_deviance_std': 0.0,
                        'mae_mean': pers['mae'],
                        'mae_std': 0.0,
                        'spearman_mean': pers['spearman'],
                        'spearman_std': 0.0,
                        'pr_auc_mean': pers['pr_auc'],
                        'pr_auc_std': 0.0,
                    })
    return pd.DataFrame(rows)


def build_coefficients() -> pd.DataFrame:
    df = prep_data('T1')
    feature_cols = ['log_distw', 'contig', 'comlang_off', 'log_gdp_o', 'log_gdp_d', 'log_pop_o', 'log_pop_d', 'rta', 'eu', 'wto_o', 'wto_d', 'diplo_disagreement', 'col45', 'comcol', 'col_dep_ever', 'log_1p_inflow_to_destination', 'log_1p_outflow_from_origin']
    X = df[feature_cols].copy()
    y = df['talent_flow_count'].astype(float)
    X2 = X.fillna(X.median())
    missing = X.isna().astype(float).add_prefix('missing_')
    X_final = pd.concat([X2, missing], axis=1)
    model = sm.GLM(y, sm.add_constant(X_final.astype(float), has_constant='add'), family=sm.families.Poisson()).fit()
    coef = model.summary2().tables[1].reset_index().rename(columns={'index': 'feature'})
    coef['irr'] = np.exp(coef['Coef.'])
    coef['ci_low'] = np.exp(coef['Coef.'] - 1.96 * coef['Std.Err.'])
    coef['ci_high'] = np.exp(coef['Coef.'] + 1.96 * coef['Std.Err.'])
    return coef[['feature', 'Coef.', 'Std.Err.', 'irr', 'ci_low', 'ci_high']].copy()


def save_outputs() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    table = build_results_table()
    table = table.sort_values(['target', 'feature_set', 'with_lag', 'split', 'model'], kind='mergesort').reset_index(drop=True)
    table.to_csv(RESULTS / '04a_baselines.csv', index=False)
    coef = build_coefficients()
    coef.to_csv(RESULTS / '04a_glm_gplusp_noL_full.csv', index=False)

    lines = [
        '# Phase 4A baseline modelling',
        '',
        'This phase creates the lagged feature tables for T1 and T2 and reports the required baseline checks. The main time split is train <= 2016 and test 2017-2019; the COVID stress test is train <= 2019 and test 2020-2021; GroupKFold uses unordered pairs on 1994-2019.',
        '',
        '## Results',
        '',
        '| target | feature_set | with_lag | split | model | poisson_deviance_mean | poisson_deviance_std | mae_mean | mae_std | spearman_mean | spearman_std | pr_auc_mean | pr_auc_std |',
        '| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for _, row in table.iterrows():
        lines.append(f"| {row['target']} | {row['feature_set']} | {int(row['with_lag'])} | {row['split']} | {row['model']} | {row['poisson_deviance_mean']:.4f} | {row['poisson_deviance_std']:.4f} | {row['mae_mean']:.4f} | {row['mae_std']:.4f} | {row['spearman_mean']:.4f} | {row['spearman_std']:.4f} | {row['pr_auc_mean']:.4f} | {row['pr_auc_std']:.4f} |")
    lines.extend(['', '## T1 G+P baseline coefficients (Poisson GLM, no lag, full 1994-2019 sample)', '', '| feature | coefficient | std_error | irr | ci_low | ci_high |', '| --- | ---: | ---: | ---: | ---: | ---: |'])
    for _, row in coef.iterrows():
        lines.append(f"| {row['feature']} | {row['Coef.']:.4f} | {row['Std.Err.']:.4f} | {row['irr']:.4f} | {row['ci_low']:.4f} | {row['ci_high']:.4f} |")
    REPORTS.joinpath('04a_baselines.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    append_ledger('phase4a_saved', 0, len(table), 'Phase 4A baseline outputs saved.')


if __name__ == '__main__':
    save_outputs()
    print('Saved', RESULTS / '04a_baselines.csv')
    print('Saved', REPORTS / '04a_baselines.md')
    print('Saved', RESULTS / '04a_glm_gplusp_noL_full.csv')
