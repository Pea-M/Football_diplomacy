# Reverse arrow: does football predict next-year political change?

Outcome dD = UN disagreement(t+1) - disagreement(t). Negative coef = more football, pair moves CLOSER politically next year. All within-pair (pair + year FE), pair-clustered SEs.

## A1. Friendlies, 1994-2019
```
                feature     coef      se       p      n  pairs
   log1p_friendly_count -0.00369 0.00374 0.32359 417328  17564
log1p_competitive_count  0.00156 0.00291 0.59135 417328  17564
```

## A2. Placebo: FUTURE friendlies (t+2) must NOT predict the t->t+1 change
```
                feature     coef      se       p      n  pairs
   log1p_friendly_count -0.00470 0.00396 0.23595 383299  17564
  log1p_friendly_future -0.00493 0.00407 0.22573 383299  17564
log1p_competitive_count  0.00225 0.00310 0.46641 383299  17564
```

## A3. Friendlies + player transfers, 2010-2019 (pairs with a league country only)
```
                feature     coef      se       p     n  pairs
   log1p_friendly_count -0.00312 0.00864 0.71850 49271   4930
        log1p_transfers  0.00542 0.00342 0.11284 49271   4930
log1p_competitive_count  0.01139 0.00653 0.08139 49271   4930
```

(1 SD of log1p friendlies = 0.092; SD of dD = 0.2443)

## B. ML ablation: predicting next-year political change
```
                              split                   features  R2_mean  R2_std  MAE_mean  delta_R2
time (train <=2013, test 2014-2019) politics history + gravity  0.09498 0.00000   0.14346   0.00000
time (train <=2013, test 2014-2019)                 + football  0.09535 0.00000   0.14330   0.00037
        unseen pairs (GroupKFold 5) politics history + gravity  0.14111 0.00269   0.16228   0.00000
        unseen pairs (GroupKFold 5)                 + football  0.14592 0.00306   0.16196   0.00481
```

