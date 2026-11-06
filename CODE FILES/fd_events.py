"""
Football Diplomacy - EXTENSION 2: political shocks as natural experiments (reads RAW files, so it
covers 2022-2025 and does not touch the existing pipeline).

  Event A - Qatar blockade (Jun 2017 - Jan 2021): Saudi Arabia, UAE, Bahrain and Egypt cut ties with Qatar.
            Did football between them stop, and did it come back after the blockade ended?
  Event B - Russia 2022: after the invasion of Ukraine, WHO kept playing Russia, and from WHERE did
            Russian clubs keep signing players? Split by how each country voted on UN resolution ES-11/1
            (2 March 2022): yes = condemned, abstain, no.

Needs one small hand-made file: dataset/raw/un_es11_1_votes.csv with columns: country,vote
  (vote = yes / no / abstain / absent; country names as Transfermarkt and the results file spell them).
Run:    .venv/bin/python "CODE FILES/fd_events.py"
Output: CODE FILES/reports/11_events.md and figures/events/*.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# ===================== SETTINGS: edit only if a path or column name differs =====================
ROOT = Path('/Users/rise/Documents/AIS')
RAW = ROOT / 'dataset' / 'raw'
RESULTS_CSV = RAW / 'international_results' / 'results.csv'
TM = RAW / 'transfermarkt'
VOTES_CSV = RAW / 'un_es11_1_votes.csv'
REPORTS = ROOT / 'CODE FILES' / 'reports'
FIG = REPORTS / 'figures' / 'events'
BLOCKADERS = ['Saudi Arabia', 'United Arab Emirates', 'Bahrain', 'Egypt']
RUSSIA_LEAGUE_COUNTRY = 'Russia'
# ===============================================================================================


def matches() -> pd.DataFrame:
    r = pd.read_csv(RESULTS_CSV, parse_dates=['date'])
    r['year'] = r['date'].dt.year
    r['friendly'] = r['tournament'].str.strip().eq('Friendly')
    return r


def opponents(r: pd.DataFrame, team: str) -> pd.DataFrame:
    a = r[r['home_team'] == team].assign(opp=lambda d: d['away_team'])
    b = r[r['away_team'] == team].assign(opp=lambda d: d['home_team'])
    return pd.concat([a, b])


def event_qatar(r: pd.DataFrame) -> list[str]:
    q = opponents(r, 'Qatar')
    q = q[q['year'].between(2010, 2025)]
    q['group'] = q['opp'].isin(BLOCKADERS).map({True: 'blockading 4', False: 'everyone else'})
    t = q.pivot_table(index='year', columns=['group', 'friendly'], values='date', aggfunc='count', fill_value=0)
    t.columns = [f'{g} | {"friendly" if f else "competitive"}' for g, f in t.columns]
    fig, ax = plt.subplots(figsize=(8, 4))
    for c in t.columns:
        if c.startswith('blockading'):
            ax.plot(t.index, t[c], marker='o', label=c)
    ax.axvspan(2017.4, 2021.0, color='grey', alpha=0.2, label='blockade')
    ax.set_title('Qatar vs the four blockading states: matches per year')
    ax.set_ylabel('matches')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / 'qatar_blockade.png', dpi=200)
    plt.close(fig)
    period = pd.cut(q['date'], pd.to_datetime(['2010-01-01', '2017-06-05', '2021-01-05', '2026-12-31']),
                    labels=['before', 'blockade', 'after'])
    s = q.groupby([period, 'group'], observed=True).size().unstack(fill_value=0)
    years = pd.Series({'before': 7.43, 'blockade': 3.58, 'after': 5.0})   # approx years per period
    s = s.div(years, axis=0).round(2)
    return ['## Event A: Qatar blockade', 'Matches per year (all types), by period:', '```', s.to_string(), '```',
            'By year and type:', '```', t.to_string(), '```', '']


def load_votes() -> pd.Series | None:
    if not VOTES_CSV.exists():
        return None
    v = pd.read_csv(VOTES_CSV)
    return v.assign(vote=v['vote'].str.lower().str.strip()).set_index('country')['vote']


def event_russia_matches(r: pd.DataFrame, votes) -> list[str]:
    q = opponents(r, 'Russia')
    q = q[q['year'].between(2018, 2025)]
    q['period'] = (q['date'] >= '2022-02-24').map({False: 'pre-invasion', True: 'post-invasion'})
    q['vote'] = q['opp'].map(votes).fillna('unmatched') if votes is not None else 'n/a'
    tab = q.groupby(['period', 'vote']).size().unstack(fill_value=0)
    post = q[q['period'] == 'post-invasion'][['date', 'opp', 'vote', 'tournament']].sort_values('date')
    return ['## Event B1: who still plays Russia', 'Matches by period and opponent UN vote:', '```', tab.to_string(),
            '```', 'Post-invasion opponents:', '```', post.to_string(index=False), '```', '']


def event_russia_transfers(votes) -> list[str]:
    t = pd.read_csv(TM / 'transfers.csv', usecols=['player_id', 'transfer_date', 'to_club_id'])
    clubs = pd.read_csv(TM / 'clubs.csv', usecols=['club_id', 'domestic_competition_id'])
    comps = pd.read_csv(TM / 'competitions.csv', usecols=['competition_id', 'country_name'])
    players = pd.read_csv(TM / 'players.csv', usecols=['player_id', 'country_of_citizenship'])
    t['year'] = pd.to_datetime(t['transfer_date'], errors='coerce').dt.year
    t = t[t['year'].between(2018, 2025)]
    t = t.merge(clubs, left_on='to_club_id', right_on='club_id', how='inner')
    t = t.merge(comps, left_on='domestic_competition_id', right_on='competition_id', how='inner')
    t = t[t['country_name'] == RUSSIA_LEAGUE_COUNTRY].merge(players, on='player_id', how='left')
    t = t[t['country_of_citizenship'].notna() & (t['country_of_citizenship'] != 'Russia')]
    t['vote'] = t['country_of_citizenship'].map(votes).fillna('unmatched') if votes is not None else 'n/a'
    tab = t.pivot_table(index='year', columns='vote', values='player_id', aggfunc='count', fill_value=0)
    share = (tab.div(tab.sum(axis=1), axis=0) * 100).round(1)
    fig, ax = plt.subplots(figsize=(8, 4))
    for c in share.columns:
        ax.plot(share.index, share[c], marker='o', label=c)
    ax.axvline(2022, color='grey', ls='--')
    ax.set_title("Foreign players joining Russian clubs: % by home country's UN vote (ES-11/1)")
    ax.set_ylabel('% of foreign signings')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / 'russia_signings_by_vote.png', dpi=200)
    plt.close(fig)
    top = t[t['year'] >= 2022]['country_of_citizenship'].value_counts().head(15)
    return ['## Event B2: where Russian clubs sign foreign players from', 'Counts:', '```', tab.to_string(), '```',
            'Shares (%):', '```', share.to_string(), '```', 'Top origins after 2022:', '```', top.to_string(), '```', '']


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    r = matches()
    votes = load_votes()
    lines = ['# Political shock events', '']
    if votes is None:
        lines.append(f'NOTE: {VOTES_CSV.name} not found - Russia tables are not split by UN vote.\n')
    lines += event_qatar(r) + event_russia_matches(r, votes) + event_russia_transfers(votes)
    text = '\n'.join(lines) + '\n'
    (REPORTS / '11_events.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()