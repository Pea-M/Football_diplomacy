# Model results (all ablations)

d2_explained = share of Poisson deviance explained vs a predict-the-training-mean model (1.0 = perfect).
delta_d2_vs_G = gain from adding the geopolitics (P) or conflict (C) block to the same model.
Persistence predicts exactly 0 wherever last year was 0, so its deviance/D2 blow up; judge it on MAE, Spearman and ROC-AUC only.

## T1 (best model: TwoPart)
### split = time
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False      -3.338997e+05               NaN          0.000        134680.143          0.330         0.989        0.455           0.012
HGB_Poisson  G+P False      -3.338997e+05               NaN          0.000        134680.143          0.308         0.989        0.455           0.012
 PoissonGLM    G False       7.670000e-01               NaN          0.000             0.094          0.186         0.988        0.617           0.012
 PoissonGLM  G+P False       7.730000e-01               NaN          0.006             0.091          0.186         0.989        0.617           0.012
    TwoPart    G False       8.020000e-01               NaN          0.000             0.080          0.186         0.987        0.594           0.012
    TwoPart  G+P False       8.020000e-01               NaN          0.000             0.080          0.186         0.987        0.592           0.012
HGB_Poisson    G  True      -2.473514e+08               NaN          0.000      99770147.040          0.310         0.992        0.656           0.012
HGB_Poisson  G+P  True      -2.473514e+08               NaN          0.000      99770147.040          0.310         0.992        0.657           0.012
Persistence    G  True       3.170000e-01               NaN          0.000             0.275          0.639         0.796        0.508           0.012
Persistence  G+P  True       3.170000e-01               NaN          0.000             0.275          0.639         0.796        0.508           0.012
 PoissonGLM    G  True       7.900000e-01               NaN          0.000             0.085          0.187         0.990        0.673           0.012
 PoissonGLM  G+P  True       7.940000e-01               NaN          0.004             0.083          0.187         0.990        0.672           0.012
    TwoPart    G  True       8.760000e-01               NaN          0.000             0.050          0.188         0.993        0.725           0.012
    TwoPart  G+P  True       8.750000e-01               NaN         -0.001             0.050          0.188         0.993        0.724           0.012
```

### Overfitting check (time split: train D2 vs test D2; gap > 0.10 = worry)
```
      model fset   lag  train_d2_mean  d2_explained_mean          gap
HGB_Poisson    G False  -1.603382e+05      -3.338997e+05   173561.551
 PoissonGLM    G False   7.170000e-01       7.670000e-01       -0.050
    TwoPart    G False   8.580000e-01       8.020000e-01        0.056
HGB_Poisson    G  True  -2.195103e+08      -2.473514e+08 27841149.116
 PoissonGLM    G  True   7.320000e-01       7.900000e-01       -0.057
    TwoPart    G  True   8.520000e-01       8.760000e-01       -0.024
HGB_Poisson  G+P False  -1.603382e+05      -3.338997e+05   173561.553
 PoissonGLM  G+P False   7.260000e-01       7.730000e-01       -0.048
    TwoPart  G+P False   8.590000e-01       8.020000e-01        0.056
HGB_Poisson  G+P  True  -2.195103e+08      -2.473514e+08 27841149.118
 PoissonGLM  G+P  True   7.390000e-01       7.940000e-01       -0.055
    TwoPart  G+P  True   8.460000e-01       8.750000e-01       -0.029
```

## T2 (best model: HGB_Poisson)
### split = time
```
      model fset   lag  d2_explained_mean  d2_explained_std  delta_d2_vs_G  poisson_dev_mean  spearman_mean  roc_auc_mean  pr_auc_mean  base_rate_mean
HGB_Poisson    G False              0.260               NaN          0.000             0.069          0.132         0.894        0.080           0.009
HGB_Poisson  G+P False              0.264               NaN          0.004             0.068          0.133         0.897        0.080           0.009
 PoissonGLM    G False              0.225               NaN          0.000             0.072          0.129         0.886        0.065           0.009
 PoissonGLM  G+P False              0.225               NaN          0.000             0.072          0.129         0.886        0.066           0.009
    TwoPart    G False              0.264               NaN          0.000             0.068          0.133         0.896        0.083           0.009
    TwoPart  G+P False              0.263               NaN         -0.001             0.068          0.133         0.896        0.082           0.009
HGB_Poisson    G  True              0.263               NaN          0.000             0.068          0.133         0.896        0.079           0.009
HGB_Poisson  G+P  True              0.264               NaN          0.001             0.068          0.133         0.897        0.079           0.009
Persistence    G  True             -2.678               NaN          0.000             0.341          0.059         0.530        0.014           0.009
Persistence  G+P  True             -2.678               NaN          0.000             0.341          0.059         0.530        0.014           0.009
 PoissonGLM    G  True              0.225               NaN          0.000             0.072          0.130         0.886        0.065           0.009
 PoissonGLM  G+P  True              0.225               NaN          0.000             0.072          0.130         0.886        0.066           0.009
    TwoPart    G  True              0.266               NaN          0.000             0.068          0.133         0.897        0.083           0.009
    TwoPart  G+P  True              0.268               NaN          0.002             0.068          0.134         0.898        0.083           0.009
```

### Overfitting check (time split: train D2 vs test D2; gap > 0.10 = worry)
```
      model fset   lag  train_d2_mean  d2_explained_mean   gap
HGB_Poisson    G False          0.423              0.260 0.163
 PoissonGLM    G False          0.293              0.225 0.069
    TwoPart    G False          0.408              0.264 0.143
HGB_Poisson    G  True          0.424              0.263 0.161
 PoissonGLM    G  True          0.295              0.225 0.070
    TwoPart    G  True          0.406              0.266 0.141
HGB_Poisson  G+P False          0.429              0.264 0.165
 PoissonGLM  G+P False          0.296              0.225 0.071
    TwoPart  G+P False          0.423              0.263 0.159
HGB_Poisson  G+P  True          0.410              0.264 0.146
 PoissonGLM  G+P  True          0.298              0.225 0.073
    TwoPart  G+P  True          0.431              0.268 0.163
```

