"""
Football Diplomacy - STEP 2 of 3: every model, every ablation, one run (replaces 4A + 4B).

Run a smoke test first:   python fd_models.py --quick     (time split only, no RandomForest)
Then the full run:         python fd_models.py

Outputs:
  results/master_results_raw.csv   (one row per fold)
  results/master_results.csv       (mean +/- std, delta vs G)
  results/best_models.json
  CODE FILES/reports/07_model_results.md
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path('/Users/rise/Documents/AIS')
PROCESSED = ROOT / 'dataset' / 'processed'
RESULTS = ROOT / 'results'
REPORTS = ROOT / 'CODE FILES' / 'reports'
QUICK = '--quick' in sys.argv
SEED = 42

TARGET = {'T1': 'talent_flow_count', 'T2': 'friendly_count'}
GEO = ['diplo_disagreement', 'col45', 'comcol', 'col_dep_ever']
CONF = ['conflict_onset', 'conflict_ongoing', 'max_hostility']
GRAV = {
    'T1': ['log_distw', 'contig', 'comlang_off', 'log_gdp_o', 'log_gdp_d', 'log_pop_o', 'log_pop_d',
           'rta', 'eu', 'wto_o', 'wto_d', 'log1p_tot_in_dest', 'log1p_tot_out_orig'],
    'T2': ['log_distw', 'contig', 'comlang_off', 'log_gdp_sum', 'log_gdp_absdiff', 'log_pop_sum',
           'log_pop_absdiff', 'rta', 'eu', 'wto_both', 'same_confederation', 'log1p_lag_competitive',
           'log1p_tot_matches_min', 'log1p_tot_matches_max'],
}
LAGS = {'T1': ['log1p_lag_target', 'log1p_lag_reverse'], 'T2': ['log1p_lag_target']}

# split -> (feature sets, models). RandomForest only where it matters, to save time.
PLAN = {
    'time':     (['G', 'G+P'], ['Persistence', 'PoissonGLM', 'RandomForest', 'HGB_Poisson', 'TwoPart']),
    'gkf':      (['G', 'G+P'], ['Persistence', 'PoissonGLM', 'RandomForest', 'HGB_Poisson', 'TwoPart']),
    'covid':    (['G', 'G+P'], ['Persistence', 'PoissonGLM', 'HGB_Poisson', 'TwoPart']),
    'conflict': (['G', 'G+P', 'G+P+C'], ['Persistence', 'PoissonGLM', 'HGB_Poisson', 'TwoPart']),
}


def features(t: str, fset: str, lag: bool) -> list[str]:
    cols = list(GRAV[t])
    if 'P' in fset:
        cols += GEO
    if 'C' in fset:
        cols += CONF
    if lag:
        cols += LAGS[t]
    return cols


class TwoPart(RegressorMixin, BaseEstimator):
    """Hurdle model: P(y > 0) x E[y | y > 0], both parts gradient-boosted."""

    def __init__(self, random_state: int = SEED):
        self.random_state = random_state

    def fit(self, X, y):
        y = np.asarray(y, dtype=float)
        pos = y > 0
        Xp = X.loc[pos] if hasattr(X, 'loc') else X[pos]
        self.clf_ = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, min_samples_leaf=50,
                                                   l2_regularization=1.0, early_stopping=True,
                                                   random_state=self.random_state).fit(X, pos.astype(int))
        self.reg_ = HistGradientBoostingRegressor(loss='poisson', max_iter=300, learning_rate=0.05,
                                                  min_samples_leaf=20, l2_regularization=1.0, early_stopping=True,
                                                  random_state=self.random_state).fit(Xp, y[pos])
        return self

    def predict(self, X):
        return self.clf_.predict_proba(X)[:, 1] * self.reg_.predict(X)


def make_model(name: str):
    if name == 'PoissonGLM':
        return make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler(),
                             PoissonRegressor(alpha=1e-4, max_iter=1000))
    if name == 'RandomForest':
        return make_pipeline(SimpleImputer(strategy='median', add_indicator=True),
                             RandomForestRegressor(n_estimators=150, min_samples_leaf=20, max_features=0.5,
                                                   max_samples=0.3, n_jobs=-1, random_state=SEED))
    if name == 'HGB_Poisson':
        return HistGradientBoostingRegressor(loss='poisson', max_iter=500, learning_rate=0.05, max_leaf_nodes=31,
                                             min_samples_leaf=50, l2_regularization=1.0, early_stopping=True,
                                             random_state=SEED)
    if name == 'TwoPart':
        return TwoPart()
    raise ValueError(name)


def pdev(y, p) -> float:
    """Mean Poisson deviance (lower is better)."""
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), 1e-8, None)
    term = np.zeros_like(y)
    m = y > 0
    term[m] = y[m] * np.log(y[m] / p[m])
    return float(np.mean(2 * (term - (y - p))))


def metrics(y, p, train_mean: float) -> dict:
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), 0, None)
    dev = pdev(y, p)
    dev0 = pdev(y, np.full_like(y, max(train_mean, 1e-8)))
    out = {'poisson_dev': dev, 'd2_explained': 1 - dev / dev0 if dev0 > 0 else np.nan,
           'mae': float(mean_absolute_error(y, p)),
           'spearman': float(spearmanr(y, p).correlation) if np.unique(p).size > 1 else np.nan,
           'pr_auc': np.nan, 'roc_auc': np.nan, 'base_rate': float((y > 0).mean())}
    any_ = (y > 0).astype(int)
    if 0 < any_.sum() < len(any_):
        out['pr_auc'] = float(average_precision_score(any_, p))
        out['roc_auc'] = float(roc_auc_score(any_, p))
    return out


def make_splits(df: pd.DataFrame, split: str, gml_last):
    yr = df['year'].to_numpy()
    if split == 'time':
        return [(np.where(yr <= 2016)[0], np.where((yr >= 2017) & (yr <= 2019))[0])]
    if split == 'covid':
        return [(np.where(yr <= 2019)[0], np.where(yr >= 2020)[0])]
    if split == 'conflict':
        last = gml_last + 1                                    # conflict features are lagged one year
        return [(np.where(yr <= last - 3)[0], np.where((yr > last - 3) & (yr <= last))[0])]
    if split == 'gkf':
        idx = np.where(yr <= 2019)[0]
        groups = df['pair_key'].to_numpy()[idx]
        return [(idx[tr], idx[te]) for tr, te in GroupKFold(n_splits=5).split(idx, groups=groups)]
    raise ValueError(split)


def run_all(gml_last) -> pd.DataFrame:
    rows = []
    for t in ['T1', 'T2']:
        df = pd.read_parquet(PROCESSED / f'model_{t}.parquet')
        y_all = df[TARGET[t]].to_numpy(dtype=float)
        lag_raw = df['lag_target'].fillna(0).to_numpy(dtype=float)
        for split, (fsets, models) in PLAN.items():
            if (QUICK and split != 'time') or (split == 'conflict' and gml_last is None):
                continue
            folds = make_splits(df, split, gml_last)
            for fset in fsets:
                for lag in (False, True):
                    X = df[features(t, fset, lag)]
                    for m in models:
                        if (m == 'Persistence' and not lag) or (QUICK and m == 'RandomForest'):
                            continue
                        t0 = time.time()
                        for k, (tr, te) in enumerate(folds):
                            ytr, yte = y_all[tr], y_all[te]
                            ptr = None
                            if m == 'Persistence':
                                pte = lag_raw[te]
                            else:
                                est = make_model(m).fit(X.iloc[tr], ytr)
                                pte = est.predict(X.iloc[te])
                                if split == 'time':
                                    ptr = est.predict(X.iloc[tr])
                            r = {'target': t, 'split': split, 'fold': k, 'fset': fset, 'lag': lag, 'model': m,
                                 'n_train': len(tr), 'n_test': len(te), **metrics(yte, pte, ytr.mean())}
                            r['train_d2'] = metrics(ytr, ptr, ytr.mean())['d2_explained'] if ptr is not None else np.nan
                            rows.append(r)
                        print(f'{t} {split:8s} {fset:6s} lag={int(lag)} {m:12s} {time.time() - t0:6.0f}s', flush=True)
        pd.DataFrame(rows).to_csv(RESULTS / 'master_results_raw.csv', index=False)   # checkpoint
    return pd.DataFrame(rows)


def summarise(raw: pd.DataFrame) -> pd.DataFrame:
    keys = ['target', 'split', 'fset', 'lag', 'model']
    mcols = ['poisson_dev', 'd2_explained', 'mae', 'spearman', 'pr_auc', 'roc_auc', 'base_rate', 'train_d2']
    agg = raw.groupby(keys)[mcols].agg(['mean', 'std'])
    agg.columns = [f'{a}_{b}' for a, b in agg.columns]
    agg = agg.reset_index()
    base = agg[agg['fset'] == 'G'].set_index(['target', 'split', 'lag', 'model'])['d2_explained_mean']
    agg['delta_d2_vs_G'] = [r.d2_explained_mean - base.get((r.target, r.split, r.lag, r.model), np.nan)
                            for r in agg.itertuples()]
    return agg


def block(df: pd.DataFrame) -> str:
    return '```\n' + df.round(3).to_string(index=False) + '\n```'


def report(agg: pd.DataFrame, best: dict) -> str:
    show = ['model', 'fset', 'lag', 'd2_explained_mean', 'd2_explained_std', 'delta_d2_vs_G',
            'poisson_dev_mean', 'spearman_mean', 'roc_auc_mean', 'pr_auc_mean', 'base_rate_mean']
    out = ['# Model results (all ablations)', '',
           'd2_explained = share of Poisson deviance explained vs a predict-the-training-mean model (1.0 = perfect).',
           'delta_d2_vs_G = gain from adding the geopolitics (P) or conflict (C) block to the same model.',
           'Persistence predicts exactly 0 wherever last year was 0, so its deviance/D2 blow up; judge it on MAE, Spearman and ROC-AUC only.', '']
    for t in ['T1', 'T2']:
        out.append(f'## {t} (best model: {best.get(t)})')
        for split in ['time', 'gkf', 'covid', 'conflict']:
            s = agg[(agg['target'] == t) & (agg['split'] == split)]
            if len(s):
                out += [f'### split = {split}', block(s[show].sort_values(['lag', 'model', 'fset'])), '']
        ov = agg[(agg['target'] == t) & (agg['split'] == 'time') & (agg['model'] != 'Persistence')]
        ov = ov.assign(gap=ov['train_d2_mean'] - ov['d2_explained_mean'])
        out += ['### Overfitting check (time split: train D2 vs test D2; gap > 0.10 = worry)',
                block(ov[['model', 'fset', 'lag', 'train_d2_mean', 'd2_explained_mean', 'gap']]), '']
    return '\n'.join(out) + '\n'


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    meta = json.loads((PROCESSED / 'meta.json').read_text())
    raw = run_all(meta.get('gml_last_year'))
    agg = summarise(raw)
    agg.to_csv(RESULTS / 'master_results.csv', index=False)
    best = {}
    for t in ['T1', 'T2']:
        c = agg[(agg['target'] == t) & (agg['split'] == 'time') & (agg['fset'] == 'G+P')
                & (~agg['lag']) & (agg['model'] != 'Persistence')]
        if len(c):
            best[t] = c.sort_values('poisson_dev_mean').iloc[0]['model']
    (RESULTS / 'best_models.json').write_text(json.dumps(best))
    text = report(agg, best)
    (REPORTS / '07_model_results.md').write_text(text, encoding='utf-8')
    print('\nBEST MODELS:', best)
    key = agg[(agg['split'].isin(['time', 'gkf'])) & (agg['model'].isin(list(best.values()) + ['Persistence']))]
    print(key[['target', 'split', 'model', 'fset', 'lag', 'd2_explained_mean', 'delta_d2_vs_G', 'roc_auc_mean']]
          .round(3).to_string(index=False))


if __name__ == '__main__':
    main()