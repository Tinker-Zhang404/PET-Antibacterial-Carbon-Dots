"""Train and audit a fixed CUDA XGBoost baseline. No PET claims or tuning."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import DMatrix, XGBRegressor, build_info

from baseline_core import (CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES,
                           SCOPE, feature_matrix, prepare_training_rows, write_csv)

ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = 'literature_pva_xgb_cuda_v1'
SEED = 20261016
XGB_PARAMS = dict(n_estimators=120, max_depth=2, learning_rate=0.05,
                  min_child_weight=2, subsample=1.0, colsample_bytree=1.0,
                  reg_lambda=10.0, reg_alpha=0.0, objective='reg:squarederror',
                  tree_method='hist', device='cuda:0', random_state=SEED,
                  n_jobs=1, verbosity=1)


def make_pipeline():
    encoder = ColumnTransformer([
        ('numeric', 'passthrough', list(range(len(NUMERIC_FEATURES)))),
        ('categorical', OneHotEncoder(handle_unknown='error', sparse_output=False),
         list(range(len(NUMERIC_FEATURES), len(FEATURES))))])
    return Pipeline([('features', encoder), ('regressor', XGBRegressor(**XGB_PARAMS))])


def assert_cuda(pipeline):
    config = json.loads(pipeline.named_steps['regressor'].get_booster().save_config())
    device = config['learner']['generic_param']['device']
    if not device.startswith('cuda'):
        raise RuntimeError(f'GPU was requested but XGBoost trained on {device}; CPU fallback is not accepted')
    if 'grow_gpu_hist' not in json.dumps(config):
        raise RuntimeError('CUDA histogram tree updater was not found in the fitted model config')
    return device


def predict_pipeline(pipeline, x):
    # Explicit DMatrix prediction avoids a CPU-input/inplace-predict device mismatch.
    encoded = pipeline.named_steps['features'].transform(x)
    return pipeline.named_steps['regressor'].get_booster().predict(DMatrix(np.asarray(encoded, dtype=np.float32)))


def scores(y, pred):
    return {'MAE_percentage_points': float(mean_absolute_error(y, pred)),
            'RMSE_percentage_points': float(np.sqrt(mean_squared_error(y, pred))),
            'R2': float(r2_score(y, pred))}


def evaluate(rows):
    x = np.asarray(feature_matrix(rows), dtype=object)
    y = np.array([r['target_killing_pct'] for r in rows], dtype=float)
    groups = np.array([r['formulation_id'] for r in rows])
    predictions = {name: np.full(len(rows), np.nan) for name in ['xgboost_cuda', 'dummy_mean']}
    fold_rows, fold_assignments = [], np.zeros(len(rows), dtype=int)
    for fold, (train, test) in enumerate(LeaveOneGroupOut().split(x, y, groups), 1):
        if set(groups[train]) & set(groups[test]):
            raise AssertionError('Formulation leakage across train and validation')
        fold_assignments[test] = fold
        models = {'xgboost_cuda': make_pipeline(), 'dummy_mean': DummyRegressor(strategy='mean')}
        for name, model in models.items():
            model.fit(x[train], y[train])
            actual_device = assert_cuda(model) if name == 'xgboost_cuda' else 'cpu_trivial_mean'
            pred = predict_pipeline(model, x[test]) if name == 'xgboost_cuda' else model.predict(x[test])
            predictions[name][test] = pred
            fold_rows.append({'fold': fold, 'held_out_formulation': str(groups[test][0]),
                              'held_out_loading_pct': rows[int(test[0])]['cd_loading_pct'],
                              'train_n': len(train), 'test_n': len(test), 'model': name, 'actual_device': actual_device,
                              **scores(y[test], pred)})
    if any(not np.isfinite(p).all() for p in predictions.values()):
        raise AssertionError('Missing or invalid out-of-fold predictions')
    summary = {}
    for name, pred in predictions.items():
        per_fold = [r for r in fold_rows if r['model'] == name]
        summary[name] = {**scores(y, pred),
                         'macro_fold_MAE_percentage_points': float(np.mean([r['MAE_percentage_points'] for r in per_fold]))}
    oof = [{**r, 'validation_fold': int(fold_assignments[i]),
            'xgb_oof_killing_pct': float(predictions['xgboost_cuda'][i]),
            'dummy_oof_killing_pct': float(predictions['dummy_mean'][i])}
           for i, r in enumerate(rows)]
    return summary, fold_rows, oof


def plot_validation(rows, folds, metrics, output):
    cache = ROOT/'tmp/matplotlib'
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3), layout='constrained')
    palette = {5.0: '#3278A8', 10.0: '#D98B32', 20.0: '#388773'}
    for loading, color in palette.items():
        group = [r for r in rows if r['cd_loading_pct'] == loading]
        axes[0].scatter([r['target_killing_pct'] for r in group], [r['xgb_oof_killing_pct'] for r in group],
                        c=color, s=45, label=f'{loading:g}% loading')
    axes[0].plot([0, 100], [0, 100], color='#888888', linestyle='--', linewidth=1)
    axes[0].set(xlim=(0, 105), ylim=(0, 105), xlabel='Reported killing (%)',
                ylabel='Out-of-fold prediction (%)', title='Leave one formulation out')
    axes[0].legend(frameon=False, fontsize=9)
    axes[0].text(.03, .96, f"XGBoost MAE = {metrics['xgboost_cuda']['MAE_percentage_points']:.2f} pp\n"
                 f"Pooled R2 = {metrics['xgboost_cuda']['R2']:.3f}",
                 transform=axes[0].transAxes, va='top', fontsize=9)
    x = np.arange(3)
    for offset, name, color, label in [(-.18, 'xgboost_cuda', '#3278A8', 'CUDA XGBoost'),
                                       (.18, 'dummy_mean', '#A8ADB3', 'Training-fold mean')]:
        records = [r for r in folds if r['model'] == name]
        axes[1].bar(x+offset, [r['MAE_percentage_points'] for r in records], width=.34,
                    color=color, label=label)
    axes[1].set_xticks(x, ['5%', '10%', '20%'])
    axes[1].set(xlabel='Held-out film loading', ylabel='Mean absolute error (pp)', title='Same folds, fixed settings')
    axes[1].legend(frameon=False, fontsize=9)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Non-PET PVA/lignin-CD film pilot: one paper, three formulations', fontsize=12)
    fig.savefig(output/'validation.png', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'output/木质素碳点训练数据库/csv/抗菌训练长表.csv')
    args = parser.parse_args()
    source = args.source.resolve()
    rows, exclusions = prepare_training_rows(source)
    output = ROOT/'output/training'/MODEL_NAME
    model_dir = ROOT/'models'/MODEL_NAME
    output.mkdir(parents=True, exist_ok=True); model_dir.mkdir(parents=True, exist_ok=True)
    metrics, folds, oof = evaluate(rows)
    # Sensitivity to the reported upper boundary, without estimating its detection limit.
    without_ceiling = [r for r in rows if not r['reported_100_pct']]
    sensitivity, _, _ = evaluate(without_ceiling)
    pipeline = make_pipeline()
    pipeline.fit(np.asarray(feature_matrix(rows), dtype=object), [r['target_killing_pct'] for r in rows])
    actual_device = assert_cuda(pipeline)
    pipeline.named_steps['regressor'].get_booster().save_model(model_dir/'booster.json')
    joblib.dump(pipeline, model_dir/'model.joblib', compress=3)
    domain = {'numeric_ranges': {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in NUMERIC_FEATURES},
              'categories': {k: sorted({r[k] for r in rows}) for k in CATEGORICAL_FEATURES}}
    versions = {pkg: importlib.metadata.version(pkg) for pkg in ['numpy','scikit-learn','scipy','joblib','matplotlib','xgboost']}
    gpu = subprocess.check_output(['nvidia-smi','--query-gpu=index,name,driver_version,memory.total','--format=csv,noheader'], text=True).strip()
    result = {'scope': SCOPE, 'model_name': MODEL_NAME, 'run_date': '2026-10-16',
              'validation': 'leave_one_formulation_out_within_A08', 'hyperparameter_search': False,
              'actual_training_device': actual_device, 'gpu_inventory': gpu,
              'xgboost_cuda_build': {k:v for k,v in build_info().items() if 'CUDA' in k},
              'observations': len(rows), 'independent_formulations': len({r['formulation_id'] for r in rows}),
              'independent_CD_samples': len({r['sample_id'] for r in rows}), 'independent_papers': 1,
              'pooled_oof': metrics, 'sensitivity_without_reported_100_pct': {'n': len(without_ceiling), 'pooled_oof': sensitivity},
              'PET_validated': False, 'cross_paper_validated': False,
              'input_data_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    metadata = {**result, 'features': FEATURES, 'target': 'target_killing_pct', 'target_unit': 'percent_0_to_100',
                'algorithm': 'XGBRegressor', 'hyperparameters': XGB_PARAMS, 'prediction_domain': domain,
                'python': platform.python_version(), 'library_versions': versions,
                'source_study': {'study_id': 'A08', 'doi': '10.1002/pen.70108',
                                 'source_file_id': 'F14', 'source_pages': 'p8-9 §3.5; p4 methods'},
                'model_sha256': hashlib.sha256((model_dir/'model.joblib').read_bytes()).hexdigest(),
                'limitations': ['One non-PET CD synthesis, three PVA film loading levels, one paper.',
                                'No support for co-precursor, dopant or synthesis-condition selection.',
                                'Reported wt% denominator and assay sampling times have source ambiguities.',
                                'Zero-survival source-flagged row excluded; reported 100% endpoints retained with sensitivity analysis.',
                                'No calibrated prediction interval or independent external test set.',
                                'Literature-reported aggregate outcomes; replicate-level data unavailable.']}
    with source.open(encoding='utf-8-sig', newline='') as stream:
        import csv
        raw_by_id = {r['measurement_id']:r for r in csv.DictReader(stream)}
    fixed_fields = ['sample_id','synthesis_temperature_C','synthesis_time_h','precursor',
                    'precursor_mass_g','water_mL','additive','additive_precursor_mass_ratio',
                    'material_mass_g','assay_volume_mL','initial_CFU_mL','medium','control','incubation_h']
    metadata['fixed_source_conditions'] = {}
    for field in fixed_fields:
        values = {raw_by_id[r['measurement_id']][field] for r in rows}
        if len(values) != 1:
            raise ValueError(f'Unexpected variation in a supposedly fixed assay field: {field}')
        metadata['fixed_source_conditions'][field] = next(iter(values)) or None
    (model_dir/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (output/'metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    write_csv(output/'training_data.csv', rows)
    write_csv(output/'excluded_rows.csv', exclusions)
    write_csv(output/'oof_predictions.csv', oof)
    write_csv(output/'fold_metrics.csv', folds)
    plot_validation(oof, folds, metrics, output)
    rf, dummy = metrics['xgboost_cuda'], metrics['dummy_mean']
    comparison = '低于' if rf['MAE_percentage_points'] < dummy['MAE_percentage_points'] else '未低于'
    report = f'''# 第一版传统模型训练报告

日期：2026-10-16。模型：固定参数 CUDA XGBoost。用途：非 PET 的 PVA/木质素碳点膜抗菌率流程基线。

实际训练设备：`{actual_device}`。显卡信息：`{gpu}`。每个交叉验证折及全量拟合后均核查 Booster 配置，若回退 CPU 则训练失败。

## 结果

| 分组交叉验证指标 | CUDA XGBoost | 训练折均值基线 |
| --- | ---: | ---: |
| MAE（百分点） | {rf['MAE_percentage_points']:.3f} | {dummy['MAE_percentage_points']:.3f} |
| RMSE（百分点） | {rf['RMSE_percentage_points']:.3f} | {dummy['RMSE_percentage_points']:.3f} |
| 合并折外预测 R² | {rf['R2']:.3f} | {dummy['R2']:.3f} |

XGBoost 的折外 MAE {comparison}均值基线。该结果只衡量本次小规模、同论文内的配方添加水平迁移，不能作为 PET 配方预测或跨论文泛化的证据。没有进行超参数搜索或从多组设置中挑选最好结果。

![折外验证图](validation.png)

## 数据与标签

- 从 A08（DOI：10.1002/pen.70108）选择 {len(rows)} 条原文明确数值结果，共 3 个膜添加水平、1 个碳点合成样品、1 篇论文。
- 输入仅有：LCQD 添加百分数、抗菌接触时间、暗/可见光、菌种。文献 ID、配方 ID、原文页码及制备后表征均不作特征。
- 输出：相对论文指定对照的抗菌率（0–100）。原文存活率用 100−存活率作明确转换；同一观察已有的派生记录排除，避免重复计数。
- 不混合 MIC、抑菌圈、其他论文的测试协议、游离 CD、H2O2 辅助体系或金属复合结果。
- 按原库规则排除原文零存活且未给检出限的 1 条记录；仍保留原文报告 100% 抗菌率的 2 条边界记录，并进行敏感性分析。

## 验证方法

每次完整留出一个膜配方（5%、10% 或 20%），用其他两个配方训练。相同配方在不同菌种、光照和时间的记录不会跨训练和验证集。编码器也只在训练折拟合。没有独立外部测试集。

留出 5% 和 20% 时涉及训练加载水平之外的外推；留出 10% 是区间内插值。三折样本量很小，不能把合并 R² 解释成可靠的普适精度，也不报告无依据的显著性或置信区间。

剔除两个原文 100% 端点后，{len(without_ceiling)} 条记录的 XGBoost 折外 MAE 为 {sensitivity['xgboost_cuda']['MAE_percentage_points']:.3f} 个百分点、R² 为 {sensitivity['xgboost_cuda']['R2']:.3f}。此结果用于检查边界值敏感性，不用于重新选择模型。

## 适用范围与不足

训练的是 PVA 膜中已有木质素碳点的添加和抗菌测试条件，不是 PET 合成配方。该论文 CD 的制备条件固定，因而本模型不能学习共前驱体、掺杂剂或合成温度/时间的作用。

原文添加 wt% 分母未明确，方法每 10 min 取样而正文结果使用 15/45 min，已在来源疑点中保留。训练按原文明确的添加水平和结果时间建模，不能把这些条件解释成已复现实验协议。

## 文件

- `training_data.csv`：实际进入模型的观察和原始测量 ID。
- `excluded_rows.csv`：原始 96 条记录中各被排除行及原因。
- `oof_predictions.csv`、`fold_metrics.csv`：逐行折外预测和分折误差。
- `metrics.json`：可机器读取的结果和输入文件哈希。
- `models/{MODEL_NAME}/model.joblib`、`booster.json`、`metadata.json`：全量 {len(rows)} 条记录拟合的管线、原生 XGBoost 模型与版本/用途信息。

全量拟合模型用于复现和受限试用；它不再有额外独立测试分数。预测入口会拒绝 PET、其他材料层级、未知菌种/光照及训练范围之外的输入。
'''
    (output/'report.md').write_text(report, encoding='utf-8')
    lock = sorted(f"{dist.metadata['Name']}=={dist.version}" for dist in importlib.metadata.distributions()
                  if dist.metadata['Name'].lower() not in {'pip','setuptools','wheel'})
    (ROOT/'requirements-ml.lock.txt').write_text('\n'.join(lock)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
