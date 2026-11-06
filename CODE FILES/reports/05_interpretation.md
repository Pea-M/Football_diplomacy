# Phase 5 interpretation

This phase uses the held-out 2017-2019 evaluation set with the best HistGradientBoosting models for each target and the no-lag and lagged feature sets. The wording is about associations, not causal effects.

## Best model by target

| target | selected feature set | Poisson deviance | MAE | Spearman |
| --- | --- | ---: | ---: | ---: |
| T1 | G+P | 4593978567799139422060629451809270107703062036480.000 | 2296989283899569711030314725904635053851531018240.000 | 0.004 |
| T2 | G+P+L | 0.077 | 0.024 | 0.019 |

## Permutation importance

The bar charts are saved under [CODE FILES/reports/figures/phase5](./figures/phase5). They show the average drop in prediction error for each feature over 10 repeats. Features with a larger mean drop are more associated with the held-out prediction error.

## SHAP summary

The SHAP summary plots use TreeExplainer on the best HistGradientBoosting models and are saved as PNG files in the same folder. Larger absolute SHAP values indicate a stronger association with the fitted count level.

## Partial dependence

The partial dependence plots show how each selected feature is associated with the fitted count after averaging over the other features. The selected features are diplo_disagreement, log distw, col45 and comcol.

## Sign sanity check

| feature | expected sign | glm IRR | PDP direction | comment |
| --- | --- | ---: | --- | --- |
| log_distw | negative | 0.655 | flat | surprise |
| log_gdp_o | positive | 1.016 | flat | surprise |
| log_gdp_d | positive | 1.365 | flat | surprise |
| contig | positive | 1.133 | flat | surprise |
| diplo_disagreement | negative | 0.819 | flat | surprise |
| col45 | positive | 1.481 | flat | surprise |
| comcol | positive | 0.287 | flat | surprise |

The GLM incidence-rate ratios point in the expected direction for distance, GDP, contiguity and colonial links, but the PDP slopes on the 2017-2019 test set were mostly flat. That flatness is a surprise and suggests the out-of-sample association was weaker than the in-sample GLM sign pattern alone would suggest.

## Conflict sub-window importance

| feature_set | feature | mean importance | std importance |
| --- | --- | ---: | ---: |
| G+P | conflict_onset | 0.0000 | 0.0000 |
| G+P | conflict_ongoing | 0.0000 | 0.0000 |
| G+P | max_hostility | 0.0000 | 0.0000 |
| G+P+C | conflict_onset | 0.0000 | 0.0000 |
| G+P+C | conflict_ongoing | 0.0000 | 0.0000 |
| G+P+C | max_hostility | 0.0000 | 0.0000 |

The MID flags are interpreted as being associated with the fitted count within the narrower conflict sub-window. Their importance is compared between G+P and G+P+C to check whether added conflict features are informative beyond the baseline geopolitics set.

## Final note

All results here are associations in the held-out test years; they are not causal estimates.
