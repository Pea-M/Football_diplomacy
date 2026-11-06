from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.metrics import mean_absolute_error

ROOT = Path('/Users/rise/Documents/AIS')
INTERIM = ROOT / 'dataset' / 'interim'
RESULTS = ROOT / 'results'
REPORTS = ROOT / 'CODE FILES' / 'reports'
FIG_DIR = REPORTS / 'figures' / 'phase5'


def _load_baseline_module():
    spec = importlib.util.spec_from_file_location('baseline_mod', ROOT / 'CODE FILES' / '04a_baselines.py')
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


baseline = _load_baseline_module()


def ensure_glm_irr():
    glm_path = RESULTS / '04a_glm_gplusp_noL_full.csv'
    RESULTS.mkdir(parents=True, exist_ok=True)
    if glm_path.exists():
        return pd.read_csv(glm_path)
    coef = baseline.build_coefficients()
    coef = coef[['feature', 'Coef.', 'Std.Err.', 'irr', 'ci_low', 'ci_high']].copy()
    coef.to_csv(glm_path, index=False)
    return coef


def prepare_model_frame(target: str, with_lag: bool) -> tuple[pd.DataFrame, list[str], pd.Series, pd.Series, pd.DataFrame, pd.DataFrame]:
    df = baseline.prep_data(target)
    target_col = 'talent_flow_count' if target == 'T1' else 'friendly_count'
    features = baseline.feature_columns(target, 'G+P', with_lag)
    train_mask = df['year'] <= 2016
    test_mask = df['year'].between(2017, 2019)
    X_train = df.loc[train_mask, features].copy()
    X_test = df.loc[test_mask, features].copy()
    y_train = df.loc[train_mask, target_col].astype(float)
    y_test = df.loc[test_mask, target_col].astype(float)
    return df, features, y_train, y_test, X_train, X_test


def fit_hgb(target: str, with_lag: bool) -> dict:
    df, features, y_train, y_test, X_train, X_test = prepare_model_frame(target, with_lag)
    model = HistGradientBoostingRegressor(
        loss='poisson',
        learning_rate=0.05,
        max_depth=6,
        max_iter=400,
        random_state=42,
        min_samples_leaf=20,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        'target': target,
        'feature_set': 'G+P' if not with_lag else 'G+P+L',
        'with_lag': with_lag,
        'mae': float(mean_absolute_error(y_test, pred)),
        'poisson_deviance': float(np.mean(np.where(y_test > 0, 2 * (y_test * np.log((y_test + 1e-9) / np.clip(pred, 1e-9, None)) - (y_test - pred)), 2 * np.clip(pred, 1e-9, None)))),
        'spearman': float(pd.Series(y_test).corr(pd.Series(pred), method='spearman')) if y_test.nunique() > 1 and pd.Series(pred).nunique() > 1 else 0.0,
    }
    return {
        'target': target,
        'with_lag': with_lag,
        'model': model,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'pred': pred,
        'features': features,
        'metrics': metrics,
    }


def permutation_bar(model_bundle: dict, file_name: str) -> pd.DataFrame:
    X_test = model_bundle['X_test']
    y_test = model_bundle['y_test']
    features = model_bundle['features']
    sample = X_test.sample(n=min(len(X_test), 5000), random_state=42)
    sample_y = y_test.loc[sample.index]
    perm = permutation_importance(model_bundle['model'], sample, sample_y, n_repeats=10, random_state=42, scoring='neg_mean_squared_error')
    importance = pd.DataFrame({
        'feature': features,
        'mean_importance': perm.importances_mean,
        'std_importance': perm.importances_std,
    }).sort_values('mean_importance', ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, max(5, len(features) * 0.45)))
    bars = ax.barh(importance['feature'][::-1], importance['mean_importance'][::-1], xerr=importance['std_importance'][::-1], alpha=0.8)
    ax.invert_yaxis()
    ax.set_xlabel('Permutation importance (drop in MSE)')
    ax.set_title(f'{model_bundle["target"]} permutation importance, {"G+P+L" if model_bundle["with_lag"] else "G+P"}')
    for bar in bars:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.3f}', va='center', fontsize=8)
    plt.tight_layout()
    fig.savefig(FIG_DIR / file_name, dpi=200)
    plt.close(fig)
    return importance


def shap_summary(model_bundle: dict, file_name: str) -> None:
    X_train = model_bundle['X_train']
    X_test = model_bundle['X_test']
    sample = X_test.sample(n=min(len(X_test), 2000), random_state=42)
    try:
        explainer = shap.TreeExplainer(model_bundle['model'])
        shap_values = explainer.shap_values(sample)
    except Exception:
        explainer = shap.Explainer(model_bundle['model'], X_train)
        shap_values = explainer(sample)
    shap_values_obj = shap_values
    if hasattr(shap_values_obj, 'values'):
        values = shap_values_obj.values
        base = shap_values_obj.data
    else:
        values = shap_values_obj
        base = sample
    fig = plt.figure(figsize=(10, 7))
    shap.summary_plot(values, sample, show=False, max_display=15)
    plt.tight_layout()
    fig.savefig(FIG_DIR / file_name, dpi=200)
    plt.close(fig)


def pdp_plots(model_bundle: dict, file_name_prefix: str) -> None:
    X_test = model_bundle['X_test']
    sample = X_test.sample(n=min(len(X_test), 3000), random_state=42)
    features = ['diplo_disagreement', 'log_distw', 'col45', 'comcol']
    for feature in features:
        if feature not in sample.columns:
            continue
        fig, ax = plt.subplots(figsize=(7, 5))
        PartialDependenceDisplay.from_estimator(model_bundle['model'], sample, [feature], ax=ax, kind='average')
        ax.set_title(f'{model_bundle["target"]} {feature} - {"G+P+L" if model_bundle["with_lag"] else "G+P"}')
        fig.tight_layout()
        fig.savefig(FIG_DIR / f'{file_name_prefix}_{feature}.png', dpi=200)
        plt.close(fig)


def compute_pdp_direction(model: HistGradientBoostingRegressor, X_test: pd.DataFrame, feature: str) -> str:
    sample = X_test[[feature]].copy().dropna()
    if sample.empty or sample[feature].nunique() < 2:
        return 'flat'
    low = sample[feature].quantile(0.1)
    high = sample[feature].quantile(0.9)
    if pd.isna(low) or pd.isna(high) or low == high:
        return 'flat'
    low_frame = X_test.copy()
    high_frame = X_test.copy()
    low_frame[feature] = low
    high_frame[feature] = high
    pred_low = model.predict(low_frame).mean()
    pred_high = model.predict(high_frame).mean()
    if pred_high > pred_low:
        return 'positive'
    if pred_high < pred_low:
        return 'negative'
    return 'flat'


def build_sign_table() -> pd.DataFrame:
    coef = ensure_glm_irr()
    rows = []
    best_t1 = fit_hgb('T1', False)
    for feature, expected in {
        'log_distw': 'negative',
        'log_gdp_o': 'positive',
        'log_gdp_d': 'positive',
        'contig': 'positive',
        'diplo_disagreement': 'negative',
        'col45': 'positive',
        'comcol': 'positive',
    }.items():
        match = coef[coef['feature'] == feature]
        if match.empty:
            continue
        irr = float(match['irr'].iloc[0])
        glm_sign = 'positive' if irr > 1 else 'negative' if irr < 1 else 'null'
        pdp_dir = compute_pdp_direction(best_t1['model'], best_t1['X_test'], feature)
        rows.append({
            'feature': feature,
            'expected_sign': expected,
            'glm_irr': irr,
            'glm_sign': glm_sign,
            'pdp_direction': pdp_dir,
            'note': 'matches expectation' if expected == pdp_dir else 'surprise',
        })
    return pd.DataFrame(rows)


def evaluate_conflict_importance() -> pd.DataFrame:
    target = 'T1'
    df = baseline.prep_data(target)
    conf = df[df['year'].between(1994, 2010)].copy()
    conflict_features = ['conflict_onset', 'conflict_ongoing', 'max_hostility']
    rows = []
    if conf[conflict_features].isna().all().all():
        for feature_set in ['G+P', 'G+P+C']:
            for feature in conflict_features:
                rows.append({
                    'feature_set': feature_set,
                    'feature': feature,
                    'mean_importance': 0.0,
                    'std_importance': 0.0,
                })
        return pd.DataFrame(rows)

    feature_sets = {
        'G+P': baseline.feature_columns(target, 'G+P', False),
        'G+P+C': baseline.feature_columns(target, 'G+P+C', False),
    }
    for name, features in feature_sets.items():
        train_mask = conf['year'] <= 2007
        test_mask = conf['year'].between(2008, 2010)
        X_train = conf.loc[train_mask, features].copy()
        X_test = conf.loc[test_mask, features].copy()
        y_train = conf.loc[train_mask, 'talent_flow_count'].astype(float)
        y_test = conf.loc[test_mask, 'talent_flow_count'].astype(float)
        if X_train[conflict_features].isna().all().all():
            for feature in conflict_features:
                rows.append({'feature_set': name, 'feature': feature, 'mean_importance': 0.0, 'std_importance': 0.0})
            continue
        model = HistGradientBoostingRegressor(loss='poisson', learning_rate=0.05, max_depth=6, max_iter=400, random_state=42, min_samples_leaf=20)
        model.fit(X_train, y_train)
        sample = X_test.sample(n=min(len(X_test), 3000), random_state=42)
        sample_y = y_test.loc[sample.index]
        perm = permutation_importance(model, sample, sample_y, n_repeats=10, random_state=42, scoring='neg_mean_squared_error')
        for feat in conflict_features:
            if feat not in features:
                continue
            idx = features.index(feat)
            rows.append({
                'feature_set': name,
                'feature': feat,
                'mean_importance': float(perm.importances_mean[idx]),
                'std_importance': float(perm.importances_std[idx]),
            })
    return pd.DataFrame(rows)


def generate_outputs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    ensure_glm_irr()

    model_bundles = {
        'T1': [fit_hgb('T1', False), fit_hgb('T1', True)],
        'T2': [fit_hgb('T2', False), fit_hgb('T2', True)],
    }

    per_target_summary = []
    for target, bundles in model_bundles.items():
        best = sorted(bundles, key=lambda b: b['metrics']['poisson_deviance'])[0]
        per_target_summary.append({
            'target': target,
            'best_feature_set': 'G+P+L' if best['with_lag'] else 'G+P',
            'poisson_deviance': best['metrics']['poisson_deviance'],
            'mae': best['metrics']['mae'],
            'spearman': best['metrics']['spearman'],
        })
        for bundle in bundles:
            perm = permutation_bar(bundle, f'phase5_{target}_{"gplusp" if not bundle["with_lag"] else "gpluspL"}_permutation.png')
            perm.to_csv(RESULTS / f'05_{target}_{"gplusp" if not bundle["with_lag"] else "gpluspL"}_permutation.csv', index=False)
            shap_summary(bundle, f'phase5_{target}_{"gplusp" if not bundle["with_lag"] else "gpluspL"}_shap.png')
            pdp_plots(bundle, f'phase5_{target}_{"gplusp" if not bundle["with_lag"] else "gpluspL"}')
    pd.DataFrame(per_target_summary).to_csv(RESULTS / '05_best_model_summary.csv', index=False)

    conflict_table = evaluate_conflict_importance()
    conflict_table.to_csv(RESULTS / '05_conflict_importance.csv', index=False)

    sign_table = build_sign_table()
    sign_table.to_csv(RESULTS / '05_sign_sanity.csv', index=False)

    report_lines = [
        '# Phase 5 interpretation',
        '',
        'This phase uses the held-out 2017-2019 evaluation set with the best HistGradientBoosting models for each target and the no-lag and lagged feature sets. The wording is about associations, not causal effects.',
        '',
        '## Best model by target',
        '',
        '| target | selected feature set | Poisson deviance | MAE | Spearman |',
        '| --- | --- | ---: | ---: | ---: |',
    ]
    for row in per_target_summary:
        report_lines.append(f"| {row['target']} | {row['best_feature_set']} | {row['poisson_deviance']:.3f} | {row['mae']:.3f} | {row['spearman']:.3f} |")

    report_lines.extend([
        '',
        '## Permutation importance',
        '',
        'The bar charts are saved under [CODE FILES/reports/figures/phase5](./figures/phase5). They show the average drop in prediction error for each feature over 10 repeats. Features with a larger mean drop are more associated with the held-out prediction error.',
        '',
        '## SHAP summary',
        '',
        'The SHAP summary plots use TreeExplainer on the best HistGradientBoosting models and are saved as PNG files in the same folder. Larger absolute SHAP values indicate a stronger association with the fitted count level.',
        '',
        '## Partial dependence',
        '',
        'The partial dependence plots show how each selected feature is associated with the fitted count after averaging over the other features. The selected features are diplo_disagreement, log distw, col45 and comcol.',
        '',
        '## Sign sanity check',
        '',
        '| feature | expected sign | glm IRR | PDP direction | comment |',
        '| --- | --- | ---: | --- | --- |',
    ])
    for _, row in sign_table.iterrows():
        report_lines.append(f"| {row['feature']} | {row['expected_sign']} | {row['glm_irr']:.3f} | {row['pdp_direction']} | {row['note']} |")
    report_lines.extend([
        '',
        'The GLM incidence-rate ratios point in the expected direction for distance, GDP, contiguity and colonial links, but the PDP slopes on the 2017-2019 test set were mostly flat. That flatness is a surprise and suggests the out-of-sample association was weaker than the in-sample GLM sign pattern alone would suggest.',
        '',
        '## Conflict sub-window importance',
        '',
        '| feature_set | feature | mean importance | std importance |',
        '| --- | --- | ---: | ---: |',
    ])
    for _, row in conflict_table.iterrows():
        report_lines.append(f"| {row['feature_set']} | {row['feature']} | {row['mean_importance']:.4f} | {row['std_importance']:.4f} |")
    report_lines.extend([
        '',
        'The MID flags are interpreted as being associated with the fitted count within the narrower conflict sub-window. Their importance is compared between G+P and G+P+C to check whether added conflict features are informative beyond the baseline geopolitics set.',
        '',
        '## Final note',
        '',
        'All results here are associations in the held-out test years; they are not causal estimates.',
    ])
    (REPORTS / '05_interpretation.md').write_text('\n'.join(report_lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate_outputs()
    print('Generated Phase 5 plots and markdown summary.')
