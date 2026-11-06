# Interpretation (associations, not causal effects)

## T1 - best model TwoPart

### Permutation importance (top 10)
```
           feature  importance    std
log1p_tot_out_orig      0.9908 0.0074
 log1p_tot_in_dest      0.2715 0.0110
         log_distw      0.1092 0.0009
         log_pop_o      0.0938 0.0028
       comlang_off      0.0467 0.0008
         log_gdp_d      0.0439 0.0031
         log_pop_d      0.0337 0.0015
         log_gdp_o      0.0247 0.0015
diplo_disagreement      0.0175 0.0012
      col_dep_ever      0.0130 0.0009
```

### Poisson GLM sign check (G+P, no lag, 1994-2019, n=50,099, pair-clustered SEs)
```
           feature     scale   irr  ci_low  ci_high     p expected found matches
         log_distw  per 1 SD 0.684   0.625    0.749 0.000        -     -     yes
            contig yes vs no 1.010   0.728    1.400 0.954        +  n.s.    n.s.
       comlang_off yes vs no 2.207   1.708    2.853 0.000        +     +     yes
         log_gdp_o  per 1 SD 0.917   0.803    1.047 0.200        ?  n.s.       -
         log_gdp_d  per 1 SD 1.225   1.058    1.418 0.007        +     +     yes
         log_pop_o  per 1 SD 1.519   1.306    1.767 0.000        ?     +       -
         log_pop_d  per 1 SD 1.037   0.924    1.163 0.541        ?  n.s.       -
               rta yes vs no 0.908   0.768    1.073 0.256        +  n.s.    n.s.
                eu yes vs no 0.946   0.758    1.181 0.625        +  n.s.    n.s.
             wto_o yes vs no 1.165   0.953    1.425 0.136        ?  n.s.       -
             wto_d yes vs no 0.979   0.550    1.741 0.941        ?  n.s.       -
 log1p_tot_in_dest  per 1 SD 2.359   2.174    2.560 0.000        ?     +       -
log1p_tot_out_orig  per 1 SD 2.763   2.611    2.923 0.000        ?     +       -
diplo_disagreement  per 1 SD 0.881   0.809    0.960 0.004        -     -     yes
             col45 yes vs no 1.372   0.935    2.015 0.106        +  n.s.    n.s.
            comcol yes vs no 3.305   1.584    6.898 0.001        +     +     yes
      col_dep_ever yes vs no 2.089   1.494    2.920 0.000        +     +     yes
```

## T2 - best model TwoPart

### Permutation importance (top 10)
```
              feature  importance    std
            log_distw      0.0120 0.0007
          log_gdp_sum      0.0068 0.0004
log1p_tot_matches_min      0.0060 0.0005
   same_confederation      0.0038 0.0002
   diplo_disagreement      0.0027 0.0007
      log_gdp_absdiff      0.0014 0.0002
          comlang_off      0.0012 0.0003
          log_pop_sum      0.0011 0.0001
      log_pop_absdiff      0.0011 0.0003
log1p_tot_matches_max      0.0003 0.0001
```

### Poisson GLM sign check (G+P, no lag, 1994-2019, n=369,461, pair-clustered SEs)
```
              feature     scale   irr  ci_low  ci_high     p expected found matches
            log_distw  per 1 SD 0.649   0.618    0.681 0.000        -     -     yes
               contig yes vs no 0.878   0.756    1.020 0.090        +  n.s.    n.s.
          comlang_off yes vs no 2.077   1.869    2.307 0.000        +     +     yes
          log_gdp_sum  per 1 SD 1.590   1.489    1.697 0.000        +     +     yes
      log_gdp_absdiff  per 1 SD 0.781   0.742    0.823 0.000        ?     -       -
          log_pop_sum  per 1 SD 1.138   1.072    1.208 0.000        ?     +       -
      log_pop_absdiff  per 1 SD 0.874   0.830    0.921 0.000        ?     -       -
                  rta yes vs no 1.101   0.997    1.215 0.057        +  n.s.    n.s.
                   eu yes vs no 0.518   0.450    0.595 0.000        +     -      NO
             wto_both yes vs no 1.162   1.066    1.267 0.001        ?     +       -
   same_confederation yes vs no 2.592   2.302    2.917 0.000        +     +     yes
log1p_lag_competitive  per 1 SD 0.966   0.950    0.981 0.000        ?     -       -
log1p_tot_matches_min  per 1 SD 1.463   1.377    1.556 0.000        ?     +       -
log1p_tot_matches_max  per 1 SD 1.176   1.109    1.248 0.000        ?     +       -
   diplo_disagreement  per 1 SD 0.894   0.853    0.937 0.000        -     -     yes
                col45 yes vs no 0.859   0.592    1.246 0.423        +  n.s.    n.s.
               comcol yes vs no 1.355   1.196    1.537 0.000        +     +     yes
         col_dep_ever yes vs no 1.188   0.913    1.546 0.199        +  n.s.    n.s.
```

