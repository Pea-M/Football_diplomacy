"""
Football Diplomacy - STEP 4: within-pair test (pair fixed effects).

Question: when the SAME two countries drift apart at the UN (relative to their own normal),
do they swap fewer players / play fewer friendlies?
Everything permanent about a pair (distance, language, colonial history) is cancelled out by the
pair fixed effect; country-year effects absorb each country's own good/bad years (GDP, league size).

Also a placebo: FUTURE disagreement should NOT predict today's football. If it does, the
"effect" is a trend, not a reaction.

Install once:  .venv/bin/pip install pyfixest
Run:           .venv/bin/python "CODE FILES/fd_fixed_effects.py"
Output:        CODE FILES/reports/09_fixed_effects.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf

ROOT = Path('/Users/rise/Documents/AIS')
PROCESSED = ROOT / 'dataset' / 'processed'
REPORTS = ROOT / 'CODE FILES' / 'reports'
I, J, Y = 'country_i_iso3', 'country_j_iso3', 'year'
SPECS = {
    # target: (outcome, fixed effects, panel end year)
    'T1': ('talent_flow_count', f'pair_key + {I}^{Y} + {J}^{Y}', 2019),
    'T2': ('friendly_count', f'pair_key + {I}^{Y} + {J}^{Y}', 2019),
}
TIME_VARYING = ['diplo_disagreement', 'rta', 'eu']


def add_lead(df: pd.DataFrame) -> pd.DataFrame:
    """diplo_disagreement in the file is year t-1; the lead is the value at t+1 (placebo)."""
    lead = df[['pair_key', Y, 'diplo_disagreement']].copy()
    lead[Y] -= 2
    return df.merge(lead.rename(columns={'diplo_disagreement': 'disagreement_future'}),
                    on=['pair_key', Y], how='left')


def keep_varying(df: pd.DataFrame, y: str) -> pd.DataFrame:
    """Pairs that never have a link carry no information under pair FE; dropping them is standard."""
    ever = df.groupby('pair_key')[y].transform('sum') > 0
    return df[ever]


def run(t: str) -> list[str]:
    y, fe, last = SPECS[t]
    df = pd.read_parquet(PROCESSED / f'model_{t}.parquet')
    df = add_lead(df[df[Y] <= last + 2])
    df = keep_varying(df[df[Y] <= last], y)
    out = [f'## {t}: {y}', f'- pairs with at least one link: {df["pair_key"].nunique():,}; rows: {len(df):,}', '']
    models = {
        'within-pair': f'{y} ~ {" + ".join(TIME_VARYING)} | {fe}',
        'placebo (future)': f'{y} ~ {" + ".join(TIME_VARYING)} + disagreement_future | {fe}',
    }
    for name, fml in models.items():
        d = df.dropna(subset=[c for c in TIME_VARYING + (['disagreement_future'] if 'future' in fml else [])])
        sd = d['diplo_disagreement'].std()
        m = pf.fepois(fml, data=d, vcov={'CRV1': 'pair_key'})
        tb = m.tidy().reset_index().rename(columns={'Coefficient': 'feature'})
        tb['effect_%'] = np.where(tb['feature'].str.contains('disagreement'),
                                  100 * (np.exp(tb['Estimate'] * sd) - 1),       # per 1 SD
                                  100 * (np.exp(tb['Estimate']) - 1))            # yes vs no
        tb['scale'] = np.where(tb['feature'].str.contains('disagreement'), 'per 1 SD', 'yes vs no')
        out += [f'### {name}  (n={m._N:,})', '```',
                tb[['feature', 'scale', 'effect_%', 'Estimate', 'Std. Error', 'Pr(>|t|)']].round(4).to_string(index=False),
                '```', '']
    return out


def main() -> None:
    lines = ['# Within-pair (fixed-effects Poisson) results', '',
             'Fixed effects: country pair + origin-year + destination-year. SEs clustered by pair.',
             'Read: effect_% = change in expected links for the same pair when the variable moves; '
             'placebo row "disagreement_future" should be ~0 / not significant.', '']
    for t in ['T1', 'T2']:
        lines += run(t)
        print(f'{t} done', flush=True)
    text = '\n'.join(lines) + '\n'
    (REPORTS / '09_fixed_effects.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()