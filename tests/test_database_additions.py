"""Provenance and label semantics for the appended literature, not model accuracy."""
import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class LiteratureAdditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'tmp/database.json').read_text(encoding='utf8'))['tables']
        cls.measurements=cls.data['性能测量']
        cls.samples=cls.data['碳点合成']

    def test_original_records_and_identifiers_preserved(self):
        expected=json.loads((ROOT/'data/original_record_checksums.json').read_text(encoding='utf8'))
        for name,record in expected.items():
            prefix=self.data[name][:record['rows']]
            encoded=json.dumps(prefix,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
            self.assertEqual(hashlib.sha256(encoded).hexdigest(),record['sha256'],name)

    def test_all_sources_match_registered_hashes(self):
        registry=json.loads((ROOT/'data/source_registry.json').read_text(encoding='utf8'))
        self.assertEqual(len({r['file_id'] for r in registry}),len(registry))
        for r in registry:
            self.assertEqual(hashlib.sha256((ROOT/r['project_path']).read_bytes()).hexdigest(),r['sha256'],r['file_id'])
        self.assertEqual(len([r for r in self.data['来源与缺文'] if r['source_file_id']]),len(registry))

    def test_correction_and_units(self):
        rows=[r for r in self.measurements if r['study_id']=='D03' and r['source_locator']=='p10 §3.3.2; p4 §2.5.3']
        self.assertEqual(len(rows),12)
        self.assertEqual({r['dose_ug_mL'] for r in rows},{5,50})
        self.assertEqual({r['contact_min'] for r in rows},{5,40})
        self.assertTrue(any('10.1016/j.jmrt.2025.03.171' in r['handling'] for r in self.data['待核查']))
        cobalt=next(r for r in self.measurements if r['study_id']=='D08' and r['endpoint']=='bacterial_survival_pct' and r['organism']=='Staphylococcus aureus')
        self.assertEqual(cobalt['H2O2_mM'],.25)
        self.assertEqual(cobalt['dose_ug_mL'],50)
        self.assertEqual(cobalt['material_context'],'free_CD_with_H2O2')

    def test_conflicts_and_no_measurement_are_not_negative_labels(self):
        self.assertTrue(all(not r['regression_eligible'] for r in self.measurements if r['data_status']=='conflict'))
        train=self.data['抗菌训练长表']
        self.assertFalse(any(r['study_id'] in {'D12','D13','C11','C12'} for r in train))
        self.assertTrue(all(r['include_primary_training']==0 for r in self.data['综述二次数据']))
        self.assertEqual(len(self.data['PET实验录入']),0)
        self.assertTrue(all(r['pet_present']==0 for r in self.samples))

    def test_endpoints_and_coactive_dose_basis(self):
        endpoints={r['endpoint'] for r in self.data['抗菌训练长表']}
        self.assertTrue({'MIC_ug_mL','MIC50_ug_mL','MBC_ug_mL','bacterial_log10_reduction'}<=endpoints)
        cdps=[r for r in self.measurements if r['study_id']=='D05' and r['endpoint'] in {'MBC_ug_mL','MIC50_ug_mL'}]
        self.assertEqual(len(cdps),2)
        self.assertTrue(all(r['dose_basis']=='PpIX equivalent in CDPs' and r['material_context']!='free_CD' for r in cdps))
        dg=[r for r in self.measurements if r['study_id']=='D07' and r['endpoint']=='MIC_ug_mL']
        self.assertEqual(sorted(r['value'] for r in dg),[1.25,5,5])

    def test_frozen_baseline_training_values_unchanged(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from baseline_core import prepare_training_rows
        rows,_=prepare_training_rows(ROOT/'output/木质素碳点训练数据库/csv/抗菌训练长表.csv')
        with (ROOT/'output/training/literature_pva_xgb_cuda_v1/training_data.csv').open(encoding='utf-8-sig',newline='') as stream:
            frozen=list(csv.DictReader(stream))
        self.assertEqual(len(rows),len(frozen))
        for now,old in zip(rows,frozen):
            self.assertEqual(now['measurement_id'],old['measurement_id'])
            self.assertEqual(now['source_notes'],old['source_notes'])
            for key in ['target_killing_pct','cd_loading_pct','contact_min']:
                self.assertEqual(now[key],float(old[key]))


if __name__=='__main__':
    unittest.main()
