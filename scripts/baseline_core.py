"""Data rules for the first, explicitly non-PET literature baseline."""
from __future__ import annotations

import csv
import math
from pathlib import Path

NUMERIC_FEATURES = ['cd_loading_pct', 'contact_min']
CATEGORICAL_FEATURES = ['light', 'organism']
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
ALLOWED_LIGHT = {'dark', 'visible'}
ALLOWED_ORGANISMS = {'Escherichia coli', 'Staphylococcus aureus'}
SCOPE = 'non_PET_PVA_lignin_CD_film_only'


def finite_number(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be numeric') from exc
    if not math.isfinite(result):
        raise ValueError(f'{name} must be finite')
    return result


def prepare_training_rows(source: Path):
    """Select one coherent assay family, keeping a record of every exclusion."""
    with source.open(encoding='utf-8-sig', newline='') as stream:
        raw = list(csv.DictReader(stream))
    selected, exclusions, seen = [], [], set()
    for row in raw:
        reason = None
        if row['study_id'] != 'A08':
            reason = 'different_study_or_protocol'
        elif row['material_context'] != 'PVA_film':
            reason = 'different_material_context'
        elif row['data_status'] == 'derived':
            reason = 'duplicate_derived_endpoint'
        elif row['regression_eligible'] != '1':
            reason = 'source_flag_not_eligible_including_zero_survival'
        elif row['data_status'] != 'reported':
            reason = 'not_direct_reported_value'
        elif row['endpoint'] not in {'bacterial_survival_pct', 'bacterial_killing_pct'}:
            reason = 'incompatible_endpoint'
        if reason:
            exclusions.append({'measurement_id': row['measurement_id'],
                               'study_id': row['study_id'], 'reason': reason,
                               'source_endpoint': row['endpoint'],
                               'source_value': row['value']})
            continue
        for field in FEATURES:
            if not row[field]:
                raise ValueError(f'{row["measurement_id"]}: missing {field}')
        original = finite_number(row['value'], 'source_value')
        if not 0 <= original <= 100:
            raise ValueError('Percentage outside [0,100]')
        target = 100.0-original if row['endpoint'] == 'bacterial_survival_pct' else original
        key = (row['entity_id'], row['organism'], row['light'], row['contact_min'])
        if key in seen:
            raise ValueError(f'Duplicate assay condition: {key}')
        seen.add(key)
        selected.append({
            'measurement_id': row['measurement_id'],
            'formulation_id': row['entity_id'],
            'sample_id': row['sample_id'],
            'study_id': row['study_id'],
            'pet_present': int(row['pet_present']),
            'material_context': row['material_context'],
            'cd_loading_pct': finite_number(row['cd_loading_pct'], 'cd_loading_pct'),
            'contact_min': finite_number(row['contact_min'], 'contact_min'),
            'light': row['light'], 'organism': row['organism'],
            'target_killing_pct': round(target, 8),
            'source_endpoint': row['endpoint'], 'source_value': original,
            'target_conversion': '100-survival_pct' if row['endpoint']=='bacterial_survival_pct' else 'identity',
            'reported_100_pct': int(target == 100),
            'source_file_id': row['source_file_id'],
            'source_locator': row['source_locator'],
            'source_notes': row['notes'],
        })
    if len(selected) < 6 or len({r['formulation_id'] for r in selected}) < 3:
        raise ValueError('Too few observations/formulations even for this grouped pilot')
    if {r['study_id'] for r in selected} != {'A08'} or any(r['pet_present'] for r in selected):
        raise ValueError('Unexpected training domain')
    return selected, exclusions


def feature_matrix(rows):
    return [[r[name] for name in FEATURES] for r in rows]


def validate_prediction_row(row, domain):
    """Reject PET, unsupported assay categories and out-of-range inputs."""
    if finite_number(row.get('pet_present'), 'pet_present') != 0:
        raise ValueError('This model has no PET validation and rejects PET inputs')
    if row.get('material_context') != 'PVA_film':
        raise ValueError('Only the non-PET PVA/lignin-CD film assay is supported')
    result = dict(row)
    for name in NUMERIC_FEATURES:
        value = finite_number(row.get(name), name)
        lo, hi = domain['numeric_ranges'][name]
        if not lo <= value <= hi:
            raise ValueError(f'{name} outside trained range [{lo},{hi}]')
        result[name] = value
    for name in CATEGORICAL_FEATURES:
        if row.get(name) not in domain['categories'][name]:
            raise ValueError(f'Unsupported {name}: {row.get(name)}')
    return result


def write_csv(path, rows, headers=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = headers or list(rows[0])
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
