# Model results (all ablations)

d2_explained = share of Poisson deviance explained vs a predict-the-training-mean model (1.0 = perfect).
delta_d2_vs_G = gain from adding the geopolitics (P) or conflict (C) block to the same model.
Persistence predicts exactly 0 wherever last year was 0, so its deviance/D2 blow up; judge it on MAE, Spearman and ROC-AUC only.

## T1 (best model: TwoPart)
### split = time
```
       model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
 HGB_Poisson    G False              0.704               NaN          0.000             0.516          0.457         0.930        0.661           0.104
 HGB_Poisson  G+P False              0.700               NaN         -0.004             0.522          0.457         0.929        0.664           0.104
  PoissonGLM    G False              0.620               NaN          0.000             0.661          0.442         0.915        0.629           0.104
  PoissonGLM  G+P False              0.630               NaN          0.010             0.644          0.444         0.917        0.628           0.104
RandomForest    G False              0.640               NaN          0.000             0.627          0.447         0.920        0.631           0.104
RandomForest  G+P False              0.641               NaN          0.001             0.625          0.448         0.921        0.632           0.104
     TwoPart    G False              0.726               NaN          0.000             0.477          0.456         0.928        0.666           0.104
     TwoPart  G+P False              0.724               NaN         -0.002             0.481          0.456         0.928        0.666           0.104
 HGB_Poisson    G  True              0.766               NaN          0.000             0.408          0.467         0.939        0.730           0.104
 HGB_Poisson  G+P  True              0.764               NaN         -0.002             0.411          0.466         0.938        0.727           0.104
 Persistence    G  True             -0.345               NaN          0.000             2.342          0.624         0.786        0.545           0.104
 Persistence  G+P  True             -0.345               NaN          0.000             2.342          0.624         0.786        0.545           0.104
  PoissonGLM    G  True              0.687               NaN          0.000             0.545          0.457         0.930        0.709           0.104
  PoissonGLM  G+P  True              0.689               NaN          0.002             0.541          0.458         0.930        0.706           0.104
RandomForest    G  True              0.747               NaN          0.000             0.441          0.465         0.937        0.733           0.104
RandomForest  G+P  True              0.746               NaN         -0.000             0.442          0.465         0.937        0.734           0.104
     TwoPart    G  True              0.766               NaN          0.000             0.407          0.466         0.937        0.729           0.104
     TwoPart  G+P  True              0.764               NaN         -0.002             0.411          0.465         0.937        0.728           0.104
```

### split = gkf
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False              0.623             0.029          0.000             0.351          0.363         0.931        0.572           0.063
HGB_Poisson  G+P False              0.626             0.029          0.003             0.349          0.363         0.931        0.578           0.063
 PoissonGLM    G False              0.591             0.037          0.000             0.380          0.349         0.915        0.532           0.063
 PoissonGLM  G+P False              0.600             0.038          0.009             0.372          0.352         0.918        0.536           0.063
    TwoPart    G False              0.638             0.025          0.000             0.339          0.364         0.932        0.585           0.063
    TwoPart  G+P False              0.642             0.025          0.004             0.335          0.365         0.933        0.592           0.063
HGB_Poisson    G  True              0.705             0.030          0.000             0.274          0.372         0.941        0.657           0.063
HGB_Poisson  G+P  True              0.706             0.029          0.001             0.273          0.372         0.941        0.658           0.063
Persistence    G  True             -0.660             0.240          0.000             1.535          0.574         0.760        0.458           0.063
Persistence  G+P  True             -0.660             0.240          0.000             1.535          0.574         0.760        0.458           0.063
 PoissonGLM    G  True              0.652             0.042          0.000             0.322          0.361         0.929        0.618           0.063
 PoissonGLM  G+P  True              0.656             0.040          0.003             0.319          0.362         0.929        0.619           0.063
    TwoPart    G  True              0.708             0.030          0.000             0.272          0.372         0.942        0.663           0.063
    TwoPart  G+P  True              0.709             0.029          0.001             0.271          0.373         0.943        0.664           0.063
```

### split = covid
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False              0.737               NaN          0.000             0.541          0.502         0.930        0.709           0.128
HGB_Poisson  G+P False              0.727               NaN         -0.011             0.563          0.501         0.930        0.706           0.128
 PoissonGLM    G False              0.634               NaN          0.000             0.754          0.485         0.916        0.669           0.128
 PoissonGLM  G+P False              0.645               NaN          0.011             0.732          0.487         0.917        0.671           0.128
    TwoPart    G False              0.740               NaN          0.000             0.535          0.501         0.929        0.707           0.128
    TwoPart  G+P False              0.747               NaN          0.007             0.521          0.503         0.931        0.712           0.128
HGB_Poisson    G  True              0.786               NaN          0.000             0.440          0.511         0.938        0.758           0.128
HGB_Poisson  G+P  True              0.786               NaN         -0.000             0.440          0.512         0.938        0.758           0.128
Persistence    G  True             -0.187               NaN          0.000             2.445          0.643         0.802        0.584           0.128
Persistence  G+P  True             -0.187               NaN          0.000             2.445          0.643         0.802        0.584           0.128
 PoissonGLM    G  True              0.717               NaN          0.000             0.583          0.504         0.932        0.742           0.128
 PoissonGLM  G+P  True              0.719               NaN          0.002             0.579          0.503         0.931        0.742           0.128
    TwoPart    G  True              0.788               NaN          0.000             0.437          0.513         0.939        0.759           0.128
    TwoPart  G+P  True              0.787               NaN         -0.001             0.438          0.513         0.940        0.760           0.128
```

### Overfitting check (time split: train D2 vs test D2; gap > 0.10 = worry)
```
       model fset   lag  train_d2_mean  d2_explained_mean    gap
 HGB_Poisson    G False          0.781              0.704  0.077
  PoissonGLM    G False          0.557              0.620 -0.064
RandomForest    G False          0.635              0.640 -0.005
     TwoPart    G False          0.763              0.726  0.037
 HGB_Poisson    G  True          0.760              0.766 -0.005
  PoissonGLM    G  True          0.608              0.687 -0.079
RandomForest    G  True          0.701              0.747 -0.046
     TwoPart    G  True          0.764              0.766 -0.002
 HGB_Poisson  G+P False          0.799              0.700  0.099
  PoissonGLM  G+P False          0.567              0.630 -0.063
RandomForest  G+P False          0.640              0.641 -0.001
     TwoPart  G+P False          0.756              0.724  0.032
 HGB_Poisson  G+P  True          0.762              0.764 -0.002
  PoissonGLM  G+P  True          0.614              0.689 -0.076
RandomForest  G+P  True          0.703              0.746 -0.043
     TwoPart  G+P  True          0.741              0.764 -0.023
```

## T2 (best model: TwoPart)
### split = time
```
       model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
 HGB_Poisson    G False              0.260               NaN          0.000             0.071          0.135         0.893        0.082            0.01
 HGB_Poisson  G+P False              0.260               NaN          0.001             0.071          0.136         0.895        0.080            0.01
  PoissonGLM    G False              0.220               NaN          0.000             0.075          0.131         0.883        0.065            0.01
  PoissonGLM  G+P False              0.220               NaN          0.000             0.075          0.131         0.882        0.066            0.01
RandomForest    G False              0.241               NaN          0.000             0.073          0.136         0.890        0.081            0.01
RandomForest  G+P False              0.243               NaN          0.002             0.073          0.136         0.890        0.082            0.01
     TwoPart    G False              0.262               NaN          0.000             0.071          0.135         0.894        0.083            0.01
     TwoPart  G+P False              0.265               NaN          0.003             0.070          0.136         0.895        0.086            0.01
 HGB_Poisson    G  True              0.261               NaN          0.000             0.071          0.135         0.894        0.082            0.01
 HGB_Poisson  G+P  True              0.260               NaN         -0.000             0.071          0.135         0.895        0.080            0.01
 Persistence    G  True             -2.716               NaN          0.000             0.356          0.058         0.529        0.014            0.01
 Persistence  G+P  True             -2.716               NaN          0.000             0.356          0.058         0.529        0.014            0.01
  PoissonGLM    G  True              0.220               NaN          0.000             0.075          0.131         0.883        0.065            0.01
  PoissonGLM  G+P  True              0.220               NaN          0.001             0.075          0.131         0.883        0.066            0.01
RandomForest    G  True              0.242               NaN          0.000             0.073          0.136         0.891        0.083            0.01
RandomForest  G+P  True              0.245               NaN          0.003             0.072          0.136         0.893        0.083            0.01
     TwoPart    G  True              0.262               NaN          0.000             0.071          0.135         0.894        0.083            0.01
     TwoPart  G+P  True              0.264               NaN          0.002             0.071          0.136         0.896        0.085            0.01
```

### split = gkf
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False              0.317             0.014          0.000             0.068          0.141         0.917        0.106            0.01
HGB_Poisson  G+P False              0.322             0.015          0.005             0.067          0.142         0.919        0.108            0.01
 PoissonGLM    G False              0.277             0.013          0.000             0.072          0.136         0.903        0.094            0.01
 PoissonGLM  G+P False              0.279             0.012          0.002             0.071          0.137         0.905        0.095            0.01
    TwoPart    G False              0.320             0.013          0.000             0.067          0.141         0.917        0.108            0.01
    TwoPart  G+P False              0.325             0.013          0.005             0.067          0.142         0.920        0.110            0.01
HGB_Poisson    G  True              0.319             0.014          0.000             0.067          0.141         0.917        0.107            0.01
HGB_Poisson  G+P  True              0.323             0.015          0.005             0.067          0.142         0.920        0.109            0.01
Persistence    G  True             -2.538             0.120          0.000             0.351          0.092         0.545        0.020            0.01
Persistence  G+P  True             -2.538             0.120          0.000             0.351          0.092         0.545        0.020            0.01
 PoissonGLM    G  True              0.278             0.013          0.000             0.071          0.137         0.904        0.096            0.01
 PoissonGLM  G+P  True              0.281             0.012          0.003             0.071          0.137         0.906        0.096            0.01
    TwoPart    G  True              0.322             0.013          0.000             0.067          0.141         0.918        0.109            0.01
    TwoPart  G+P  True              0.325             0.014          0.003             0.067          0.142         0.920        0.110            0.01
```

### split = covid
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False              0.205               NaN          0.000             0.047          0.095         0.893        0.048           0.005
HGB_Poisson  G+P False              0.202               NaN         -0.003             0.047          0.095         0.893        0.052           0.005
 PoissonGLM    G False              0.194               NaN          0.000             0.048          0.091         0.878        0.045           0.005
 PoissonGLM  G+P False              0.192               NaN         -0.001             0.048          0.092         0.881        0.046           0.005
    TwoPart    G False              0.205               NaN          0.000             0.047          0.095         0.892        0.051           0.005
    TwoPart  G+P False              0.199               NaN         -0.006             0.048          0.095         0.892        0.053           0.005
HGB_Poisson    G  True              0.207               NaN          0.000             0.047          0.095         0.892        0.050           0.005
HGB_Poisson  G+P  True              0.202               NaN         -0.005             0.048          0.095         0.894        0.049           0.005
Persistence    G  True             -2.126               NaN          0.000             0.186          0.038         0.520        0.007           0.005
Persistence  G+P  True             -2.126               NaN          0.000             0.186          0.038         0.520        0.007           0.005
 PoissonGLM    G  True              0.198               NaN          0.000             0.048          0.092         0.880        0.044           0.005
 PoissonGLM  G+P  True              0.197               NaN         -0.001             0.048          0.092         0.882        0.045           0.005
    TwoPart    G  True              0.206               NaN          0.000             0.047          0.095         0.892        0.055           0.005
    TwoPart  G+P  True              0.202               NaN         -0.004             0.047          0.095         0.893        0.054           0.005
```

### split = conflict
```
      model  fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson     G False              0.308               NaN          0.000             0.077          0.151         0.908        0.115           0.012
HGB_Poisson   G+P False              0.313               NaN          0.006             0.077          0.153         0.911        0.118           0.012
HGB_Poisson G+P+C False              0.307               NaN         -0.001             0.077          0.151         0.908        0.118           0.012
 PoissonGLM     G False              0.260               NaN          0.000             0.083          0.146         0.893        0.101           0.012
 PoissonGLM   G+P False              0.260               NaN         -0.000             0.083          0.146         0.894        0.101           0.012
 PoissonGLM G+P+C False              0.260               NaN          0.000             0.083          0.145         0.891        0.102           0.012
    TwoPart     G False              0.316               NaN          0.000             0.076          0.152         0.910        0.125           0.012
    TwoPart   G+P False              0.317               NaN          0.002             0.076          0.153         0.912        0.118           0.012
    TwoPart G+P+C False              0.314               NaN         -0.002             0.077          0.152         0.910        0.118           0.012
HGB_Poisson     G  True              0.310               NaN          0.000             0.077          0.152         0.909        0.117           0.012
HGB_Poisson   G+P  True              0.313               NaN          0.003             0.077          0.153         0.911        0.116           0.012
HGB_Poisson G+P+C  True              0.306               NaN         -0.004             0.078          0.151         0.907        0.117           0.012
Persistence     G  True             -2.703               NaN          0.000             0.414          0.086         0.544        0.022           0.012
Persistence   G+P  True             -2.703               NaN          0.000             0.414          0.086         0.544        0.022           0.012
Persistence G+P+C  True             -2.703               NaN          0.000             0.414          0.086         0.544        0.022           0.012
 PoissonGLM     G  True              0.260               NaN          0.000             0.083          0.146         0.894        0.101           0.012
 PoissonGLM   G+P  True              0.260               NaN          0.000             0.083          0.147         0.895        0.102           0.012
 PoissonGLM G+P+C  True              0.260               NaN          0.000             0.083          0.145         0.892        0.103           0.012
    TwoPart     G  True              0.317               NaN          0.000             0.076          0.152         0.911        0.119           0.012
    TwoPart   G+P  True              0.320               NaN          0.003             0.076          0.153         0.912        0.120           0.012
    TwoPart G+P+C  True              0.312               NaN         -0.005             0.077          0.152         0.909        0.117           0.012
```

### Overfitting check (time split: train D2 vs test D2; gap > 0.10 = worry)
```
       model fset   lag  train_d2_mean  d2_explained_mean   gap
 HGB_Poisson    G False          0.417              0.260 0.157
  PoissonGLM    G False          0.286              0.220 0.066
RandomForest    G False          0.458              0.241 0.217
     TwoPart    G False          0.403              0.262 0.141
 HGB_Poisson    G  True          0.420              0.261 0.159
  PoissonGLM    G  True          0.287              0.220 0.067
RandomForest    G  True          0.458              0.242 0.216
     TwoPart    G  True          0.397              0.262 0.135
 HGB_Poisson  G+P False          0.398              0.260 0.138
  PoissonGLM  G+P False          0.289              0.220 0.069
RandomForest  G+P False          0.463              0.243 0.220
     TwoPart  G+P False          0.416              0.265 0.151
 HGB_Poisson  G+P  True          0.403              0.260 0.143
  PoissonGLM  G+P  True          0.290              0.220 0.070
RandomForest  G+P  True          0.463              0.245 0.218
     TwoPart  G+P  True          0.415              0.264 0.151
```

