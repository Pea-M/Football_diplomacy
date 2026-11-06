# Within-pair (fixed-effects Poisson) results

Fixed effects: T1 = pair + origin-year + destination-year; T2 = pair + year. SEs clustered by pair.
Read: effect_% = change in expected links for the same pair when the variable moves; placebo row "disagreement_future" should be ~0 / not significant.

## T1: talent_flow_count
- pairs with at least one link: 1,263; rows: 23,220

### within-pair  (n=18,577)
```
           feature     scale  effect_%  Estimate  Std. Error  Pr(>|t|)
diplo_disagreement  per 1 SD    9.8897    0.1276      0.1818    0.4828
               rta yes vs no  -16.3732   -0.1788      0.2035    0.3796
                eu yes vs no   -6.9033   -0.0715      0.7810    0.9270
```

### placebo (future)  (n=18,577)
```
            feature     scale  effect_%  Estimate  Std. Error  Pr(>|t|)
 diplo_disagreement  per 1 SD   10.0609    0.1297      0.1813    0.4744
                rta yes vs no  -16.4814   -0.1801      0.2035    0.3762
                 eu yes vs no   -6.8973   -0.0715      0.7819    0.9272
disagreement_future  per 1 SD   -2.3326   -0.0319      0.1836    0.8619
```

## T2: friendly_count
- pairs with at least one link: 3,426; rows: 89,076

### within-pair  (n=75,314)
```
           feature     scale  effect_%  Estimate  Std. Error  Pr(>|t|)
diplo_disagreement  per 1 SD   -7.2633   -0.1046      0.0513    0.0413
               rta yes vs no   -8.0807   -0.0843      0.0591    0.1543
                eu yes vs no  -30.3569   -0.3618      0.0974    0.0002
```

### placebo (future)  (n=74,690)
```
            feature     scale  effect_%  Estimate  Std. Error  Pr(>|t|)
 diplo_disagreement  per 1 SD   -5.0670   -0.0721      0.0616    0.2420
                rta yes vs no   -8.8465   -0.0926      0.0592    0.1177
                 eu yes vs no  -29.5694   -0.3505      0.0973    0.0003
disagreement_future  per 1 SD   -2.9391   -0.0414      0.0637    0.5164
```

