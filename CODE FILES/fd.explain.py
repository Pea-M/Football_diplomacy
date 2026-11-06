"""
Football Diplomacy - STEP 3 of 3: interpretation + result figures for the PPT (replaces Phase 5).
Needs fd_models.py in the same folder. Refits the best model per target (no pickles).

Outputs in CODE FILES/reports/figures/final/ and CODE FILES/reports/08_interpretation.md:
  fig1_ablation_<split>.png      D2 by feature set, with/without lag (the headline chart)
  fig2_importance_<T>.png        permutation importance on the 2017-2019 test years
  fig3_pdp_<T>.png               partial dependence: UN disagreement, distance, colonial ties
  fig4_irr_<T>.png               Poisson GLM incidence-rate ratios (per 1 SD), cluster-robust CIs
  fig5_calibration_<T>.png       predicted vs actual by prediction decile
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.metrics import make_scorer

from fd_models import PROCESSED, REPORTS, RESULTS, TARGET, features, make_model, pdev

FIG = REPORTS / 'figures' / 'final'
EXPECT = {'log_distw': '-', 'contig': '+', 'comlang_off': '+', 'col45': '+', 'comcol': '+',
          'col_dep_ever': '+', 'diplo_disagreement': '-', 'log_gdp_d': '+', 'log_gdp_sum': '+',
          'same_confederation': '+', 'rta': '+', 'eu': '+'}
PDP_COLS = ['diplo_disagreement', 'log_distw', 'col45', 'comcol']


def fig_ablation(master: pd.DataFrame, split: str) -> None:
    s = master[(master['split'] == split) & (master['fset'].isin(['G', 'G+P'])) & (master['model'] != 'Persistence')]
    if s.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
    for ax, t in zip(axes, ['T1', 'T2']):
        d = s[s['target'] == t].copy()
        d['config'] = d['fset'] + np.where(d['lag'], ' + lag', '')
        pv = d.pivot_table(index='model', columns='config', values='d2_explained_mean')
        err = d.pivot_table(index='model', columns='config', values='d2_explained_std').reindex_like(pv)
        pv.plot.bar(ax=ax, yerr=err if split == 'gkf' else None, rot=0, capsize=3)
        ax.set_title(f'{t}: deviance explained ({split} split)')
        ax.set_ylabel('D2 (higher = better)')
        ax.set_xlabel('')
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / f'fig1_ablation_{split}.png', dpi=200)
    plt.close(fig)


def glm_irr(t: str, df: pd.DataFrame) -> pd.DataFrame:
    cols = features(t, 'G+P', False)
    d = df.loc[df['year'] <= 2019, cols + [TARGET[t], 'pair_key']].dropna()
    X = d[cols].copy()
    X = X.loc[:, X.std() > 0]
    cont = [c for c in X.columns if X[c].nunique() > 2]
    X[cont] = (X[cont] - X[cont].mean()) / X[cont].std()
    res = sm.GLM(d[TARGET[t]].astype(float), sm.add_constant(X.astype(float)), family=sm.families.Poisson()).fit(
        cov_type='cluster', cov_kwds={'groups': pd.factorize(d['pair_key'])[0]})
    ci = res.conf_int()
    out = pd.DataFrame({'feature': res.params.index, 'coef': res.params.values, 'irr': np.exp(res.params.values),
                        'ci_low': np.exp(ci[0].values), 'ci_high': np.exp(ci[1].values), 'p': res.pvalues.values})
    out = out[out['feature'] != 'const']
    out['scale'] = np.where(out['feature'].isin(cont), 'per 1 SD', 'yes vs no')
    out['expected'] = out['feature'].map(EXPECT).fillna('?')
    found = np.where(out['coef'] > 0, '+', '-')
    out['found'] = np.where(out['p'] < 0.05, found, 'n.s.')
    out['matches'] = np.where(out['expected'] == '?', '-', np.where(out['found'] == out['expected'], 'yes',
                              np.where(out['found'] == 'n.s.', 'n.s.', 'NO')))
    out.attrs['n'] = len(d)
    o = out.sort_values('irr')
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(o) + 1.5))
    ax.errorbar(o['irr'], range(len(o)), xerr=[o['irr'] - o['ci_low'], o['ci_high'] - o['irr']], fmt='o', capsize=3)
    ax.axvline(1, color='grey', ls='--')
    ax.set_yticks(range(len(o)))
    ax.set_yticklabels(o['feature'])
    ax.set_xscale('log')
    ax.set_xlabel('Incidence-rate ratio (log scale; >1 = more links)')
    ax.set_title(f'{t}: Poisson GLM, G+P, no lag (n={len(d):,}, pair-clustered 95% CI)')
    fig.tight_layout()
    fig.savefig(FIG / f'fig4_irr_{t}.png', dpi=200)
    plt.close(fig)
    return out


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    master = pd.read_csv(RESULTS / 'master_results.csv')
    best = json.loads((RESULTS / 'best_models.json').read_text())
    for split in ['time', 'gkf', 'conflict']:
        fig_ablation(master, split)
    md = ['# Interpretation (associations, not causal effects)', '']
    scorer = make_scorer(lambda a, b: -pdev(a, b))
    rng = np.random.default_rng(42)
    for t in ['T1', 'T2']:
        df = pd.read_parquet(PROCESSED / f'model_{t}.parquet')
        yr = df['year'].to_numpy()
        y = df[TARGET[t]].to_numpy(dtype=float)
        cols = features(t, 'G+P', False)
        tr, te = np.where(yr <= 2016)[0], np.where((yr >= 2017) & (yr <= 2019))[0]
        est = make_model(best[t]).fit(df.iloc[tr][cols], y[tr])

        te_s = rng.choice(te, min(len(te), 60000), replace=False)
        pi = permutation_importance(est, df.iloc[te_s][cols], y[te_s], scoring=scorer, n_repeats=5, random_state=42)
        imp = pd.DataFrame({'feature': cols, 'importance': pi.importances_mean, 'std': pi.importances_std})
        imp = imp.sort_values('importance', ascending=False)
        top = imp.head(15).iloc[::-1]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(top['feature'], top['importance'], xerr=top['std'])
        ax.set_xlabel('Increase in Poisson deviance when shuffled')
        ax.set_title(f'{t}: permutation importance ({best[t]}, test 2017-2019)')
        fig.tight_layout()
        fig.savefig(FIG / f'fig2_importance_{t}.png', dpi=200)
        plt.close(fig)

        pdp_cols = [c for c in PDP_COLS if c in cols]
        xs = df.iloc[te][cols].dropna(subset=pdp_cols)
        xs = xs.sample(min(len(xs), 5000), random_state=42)
        disp = PartialDependenceDisplay.from_estimator(est, xs, pdp_cols, method='brute', grid_resolution=20,
                                                       n_cols=len(pdp_cols))
        disp.figure_.set_size_inches(4 * len(pdp_cols), 3.5)
        disp.figure_.suptitle(f'{t}: partial dependence ({best[t]})')
        disp.figure_.tight_layout()
        disp.figure_.savefig(FIG / f'fig3_pdp_{t}.png', dpi=200)
        plt.close(disp.figure_)

        p = np.clip(est.predict(df.iloc[te][cols]), 0, None)
        cal = pd.DataFrame({'pred': p, 'actual': y[te]})
        cal['bin'] = pd.qcut(cal['pred'].rank(method='first'), 10, labels=False)
        cal = cal.groupby('bin')[['pred', 'actual']].mean()
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(cal['pred'], cal['actual'], 'o-')
        lim = max(cal.max())
        ax.plot([0, lim], [0, lim], '--', color='grey')
        ax.set_xlabel('Mean predicted')
        ax.set_ylabel('Mean actual')
        ax.set_title(f'{t}: calibration by decile (test 2017-2019)')
        fig.tight_layout()
        fig.savefig(FIG / f'fig5_calibration_{t}.png', dpi=200)
        plt.close(fig)

        irr = glm_irr(t, df)
        md += [f'## {t} - best model {best[t]}', '', '### Permutation importance (top 10)', '```',
               imp.head(10).round(4).to_string(index=False), '```', '',
               f'### Poisson GLM sign check (G+P, no lag, 1994-2019, n={irr.attrs["n"]:,}, pair-clustered SEs)', '```',
               irr[['feature', 'scale', 'irr', 'ci_low', 'ci_high', 'p', 'expected', 'found', 'matches']]
               .round(3).to_string(index=False), '```', '']
        print(f'{t} done')
    (REPORTS / '08_interpretation.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('\n'.join(md))


if __name__ == '__main__':
    main()