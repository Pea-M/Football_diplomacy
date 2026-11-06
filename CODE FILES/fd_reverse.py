"""
Football Diplomacy - EXTENSION 1: flip the arrow. Does football today predict politics tomorrow?

Outcome: change in a pair's UN voting disagreement from year t to t+1 (negative = moving closer).
Inputs:  friendlies played in year t (and, from 2010, players exchanged in year t).

Two tests (no extra packages needed):
  A. Within-pair regression (pair + year fixed effects, pair-clustered SEs), plus a placebo using
     FUTURE friendlies (t+2), which must not "predict" the earlier change.
  B. ML ablation: does adding football features improve out-of-sample prediction of next year's
     political change, beyond the pair's own political history and gravity?

Run:    .venv/bin/python "CODE FILES/fd_reverse.py"
Output: CODE FILES/reports/10_reverse_arrow.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

ROOT = Path('/Users/rise/Documents/AIS')
PROCESSED = ROOT / 'dataset' / 'processed'
REPORTS = ROOT / 'CODE FILES' / 'reports'
SEED = 42


def build() -> pd.DataFrame:
    t2 = pd.read_parquet(PROCESSED / 'model_T2.parquet')
    # In the file, row year r holds covariates from r-1. Re-key UN disagreement to its real year.
    un = t2[['pair_key', 'year', 'diplo_disagreement']].assign(year=lambda d: d['year'] - 1)
    un = un.rename(columns={'diplo_disagreement': 'D'})
    fb = t2[['pair_key', 'year', 'friendly_count', 'competitive_count']]
    grav = t2[['pair_key', 'year', 'log_distw', 'log_gdp_sum', 'same_confederation', 'comlang_off',
               'contig', 'eu', 'rta', 'col_dep_ever', 'comcol']].assign(year=lambda d: d['year'] - 1)
    df = fb.merge(un, on=['pair_key', 'year'], how='left').merge(grav, on=['pair_key', 'year'], how='left')
    for k, name in [(1, 'D_next'), (-1, 'D_prev')]:
        s = un.assign(year=lambda d, k=k: d['year'] - k).rename(columns={'D': name})
        df = df.merge(s, on=['pair_key', 'year'], how='left')
    for k, name in [(-1, 'friendly_prev'), (2, 'friendly_future')]:
        s = fb[['pair_key', 'year', 'friendly_count']].assign(year=lambda d, k=k: d['year'] - k)
        df = df.merge(s.rename(columns={'friendly_count': name}), on=['pair_key', 'year'], how='left')
    t1 = pd.read_parquet(PROCESSED / 'model_T1.parquet')
    tr = t1.groupby(['pair_key', 'year'], as_index=False)['talent_flow_count'].sum()
    df = df.merge(tr.rename(columns={'talent_flow_count': 'transfers'}), on=['pair_key', 'year'], how='left')
    df['dD'] = df['D_next'] - df['D']
    df['dD_prev'] = df['D'] - df['D_prev']
    for c in ['friendly_count', 'competitive_count', 'friendly_prev', 'friendly_future', 'transfers']:
        df[f'log1p_{c}'] = np.log1p(df[c])
    return df.dropna(subset=['dD', 'D'])


def demean(df: pd.DataFrame, cols: list[str], fes: list[str], tol=1e-9, maxit=200) -> np.ndarray:
    X = df[cols].to_numpy(dtype=float).copy()
    codes = [pd.factorize(df[f])[0] for f in fes]
    for _ in range(maxit):
        old = X.copy()
        for c in codes:
            sums = np.zeros((c.max() + 1, X.shape[1]))
            np.add.at(sums, c, X)
            X -= (sums / np.bincount(c)[:, None])[c]
        if np.abs(X - old).max() < tol:
            break
    return X


def fe_ols(df: pd.DataFrame, y: str, xs: list[str], fes=('pair_key', 'year')) -> pd.DataFrame:
    d = df.dropna(subset=[y, *xs])
    Z = demean(d, [y, *xs], list(fes))
    yv, X = Z[:, 0], Z[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ yv
    u = yv - X @ beta
    g = pd.factorize(d['pair_key'])[0]
    S = np.zeros((g.max() + 1, X.shape[1]))
    np.add.at(S, g, X * u[:, None])
    G = g.max() + 1
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1)
    se = np.sqrt(np.diag(V))
    out = pd.DataFrame({'feature': xs, 'coef': beta, 'se': se, 'p': 2 * norm.sf(np.abs(beta / se))})
    out['n'] = len(d)
    out['pairs'] = G
    return out


def ml_ablation(df: pd.DataFrame) -> pd.DataFrame:
    base = ['D', 'dD_prev', 'log_distw', 'log_gdp_sum', 'same_confederation', 'comlang_off', 'contig',
            'eu', 'rta', 'col_dep_ever', 'comcol']
    foot = ['log1p_friendly_count', 'log1p_friendly_prev', 'log1p_competitive_count']
    d = df[df['year'] <= 2019].reset_index(drop=True)
    yr, y = d['year'].to_numpy(), d['dD'].to_numpy()
    rows = []
    splits = {'time (train <=2013, test 2014-2019)': [(np.where(yr <= 2013)[0], np.where(yr >= 2014)[0])],
              'unseen pairs (GroupKFold 5)': list(GroupKFold(5).split(d, groups=d['pair_key']))}
    for sname, folds in splits.items():
        for fname, cols in [('politics history + gravity', base), ('+ football', base + foot)]:
            r2, mae = [], []
            for tr, te in folds:
                m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, min_samples_leaf=100,
                                                  l2_regularization=1.0, early_stopping=True, random_state=SEED)
                p = m.fit(d.iloc[tr][cols], y[tr]).predict(d.iloc[te][cols])
                r2.append(r2_score(y[te], p))
                mae.append(mean_absolute_error(y[te], p))
            rows.append({'split': sname, 'features': fname, 'R2_mean': np.mean(r2), 'R2_std': np.std(r2),
                         'MAE_mean': np.mean(mae)})
    out = pd.DataFrame(rows)
    out['delta_R2'] = out['R2_mean'] - out.groupby('split')['R2_mean'].transform('first')
    return out


def block(df: pd.DataFrame) -> list[str]:
    return ['```', df.round(5).to_string(index=False), '```', '']


def main() -> None:
    df = build()
    sd_f = df['log1p_friendly_count'].std()
    lines = ['# Reverse arrow: does football predict next-year political change?', '',
             'Outcome dD = UN disagreement(t+1) - disagreement(t). Negative coef = more football, '
             'pair moves CLOSER politically next year. All within-pair (pair + year FE), pair-clustered SEs.', '',
             '## A1. Friendlies, 1994-2019',
             *block(fe_ols(df[df['year'] <= 2019], 'dD', ['log1p_friendly_count', 'log1p_competitive_count'])),
             '## A2. Placebo: FUTURE friendlies (t+2) must NOT predict the t->t+1 change',
             *block(fe_ols(df[df['year'] <= 2017], 'dD',
                           ['log1p_friendly_count', 'log1p_friendly_future', 'log1p_competitive_count'])),
             '## A3. Friendlies + player transfers, 2010-2019 (pairs with a league country only)',
             *block(fe_ols(df[(df['year'].between(2010, 2019)) & df['transfers'].notna()], 'dD',
                           ['log1p_friendly_count', 'log1p_transfers', 'log1p_competitive_count'])),
             f'(1 SD of log1p friendlies = {sd_f:.3f}; SD of dD = {df["dD"].std():.4f})', '',
             '## B. ML ablation: predicting next-year political change',
             *block(ml_ablation(df))]
    text = '\n'.join(lines) + '\n'
    (REPORTS / '10_reverse_arrow.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()