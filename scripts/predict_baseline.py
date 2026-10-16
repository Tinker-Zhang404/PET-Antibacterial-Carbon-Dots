"""Restricted inference for the non-PET PVA-film pilot, not PET recipe design."""
import argparse
import csv
import json
from pathlib import Path

import joblib
import numpy as np

from baseline_core import SCOPE, feature_matrix, validate_prediction_row, write_csv
from train_baseline import predict_pipeline

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model-dir', type=Path, default=ROOT/'models/literature_pva_xgb_cuda_v1')
    args = parser.parse_args()
    metadata = json.loads((args.model_dir/'metadata.json').read_text(encoding='utf-8'))
    if metadata['scope'] != SCOPE or metadata['PET_validated']:
        raise ValueError('Unexpected model scope metadata')
    with args.input.open(encoding='utf-8-sig', newline='') as stream:
        raw = list(csv.DictReader(stream))
    if not raw:
        raise ValueError('No input records')
    rows = [validate_prediction_row(r, metadata['prediction_domain']) for r in raw]
    pipeline = joblib.load(args.model_dir/'model.joblib')
    predicted = predict_pipeline(pipeline, np.asarray(feature_matrix(rows), dtype=object))
    output = [{**row, 'predicted_killing_pct': float(pred), 'model_scope': SCOPE,
               'PET_validated': False, 'calibrated_interval_available': False}
              for row, pred in zip(rows, predicted)]
    write_csv(args.output, output)
    print(f'Wrote {len(output)} scoped predictions to {args.output}')


if __name__ == '__main__':
    main()
