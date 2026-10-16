"""Check leakage-sensitive selection, target handling and inference boundaries."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from baseline_core import prepare_training_rows, validate_prediction_row
from train_baseline import evaluate


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.exclusions = prepare_training_rows(ROOT/'output/木质素碳点训练数据库/csv/抗菌训练长表.csv')
        cls.domain = {'numeric_ranges': {'cd_loading_pct': [5,20], 'contact_min': [15,45]},
                      'categories': {'light': ['dark','visible'],
                                     'organism': ['Escherichia coli','Staphylococcus aureus']}}
        cls.example = dict(pet_present=0, material_context='PVA_film', cd_loading_pct=10,
                           contact_min=15, light='dark', organism='Escherichia coli')

    def test_endpoint_conversion_and_no_derived_duplicates(self):
        self.assertEqual(len(self.rows), 16)
        first = next(r for r in self.rows if r['measurement_id']=='M0197')
        self.assertAlmostEqual(first['target_killing_pct'], 52.55)
        self.assertTrue(all(r['study_id']=='A08' and r['pet_present']==0 for r in self.rows))
        keys = [(r['formulation_id'],r['organism'],r['light'],r['contact_min']) for r in self.rows]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertTrue(any(r['reason']=='duplicate_derived_endpoint' for r in self.exclusions))

    def test_formulation_is_held_out_entirely(self):
        _, folds, oof = evaluate(self.rows)
        for group in {r['formulation_id'] for r in oof}:
            self.assertEqual(len({r['validation_fold'] for r in oof if r['formulation_id']==group}),1)
        self.assertEqual(sum(r['test_n'] for r in folds if r['model']=='xgboost_cuda'),len(self.rows))
        self.assertTrue(all(r['actual_device'].startswith('cuda') for r in folds if r['model']=='xgboost_cuda'))
        self.assertTrue(all(0<=r['xgb_oof_killing_pct']<=100 for r in oof))

    def test_zero_survival_excluded_but_reported_ceiling_flagged(self):
        self.assertNotIn('M0208',{r['measurement_id'] for r in self.rows})
        self.assertEqual(sum(r['reported_100_pct'] for r in self.rows),2)

    def test_valid_non_pet_input(self):
        self.assertEqual(validate_prediction_row(self.example,self.domain)['cd_loading_pct'],10)

    def test_pet_and_other_materials_rejected(self):
        for change in [dict(pet_present=1),dict(material_context='free_CD')]:
            with self.assertRaises(ValueError):
                validate_prediction_row({**self.example,**change},self.domain)

    def test_unknown_categories_and_extrapolation_rejected(self):
        for change in [dict(light='UV'),dict(organism='Klebsiella pneumoniae'),
                       dict(cd_loading_pct=21),dict(contact_min=120),dict(cd_loading_pct=float('nan'))]:
            with self.assertRaises(ValueError):
                validate_prediction_row({**self.example,**change},self.domain)


if __name__=='__main__':
    unittest.main()
