"""Release checks must reject stale, incomplete and unreviewed evidence."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from font_recovery.design_status import ROOT, deviations_valid, evidence_valid, inspect, sha


class DesignStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('sources/design-decisions.json', 'reports/current-quality.json',
                     'reports/verification.json', 'reports/timer-verification.json', 'dist/TabunaSansVariable.ttf', 'dist/TabunaSansVariable.woff2'):
            destination = self.root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, destination)
        self.quality_path = self.root/'reports/current-quality.json'
        decisions_path = self.root/'sources/design-decisions.json'
        decisions = json.loads(decisions_path.read_text())
        for decision in decisions['decisions']:
            decision.update(status='pending', change=None, evidence=[], verdict=None)
        decisions.pop('authorial_deviations', None)
        decisions_path.write_text(json.dumps(decisions))
        self.quality = json.loads(self.quality_path.read_text())
        for row in self.quality['all_cases']:
            if row['mask_iou'] is not None:
                row['mask_iou'] = 1.0
        self.write_quality()

    def write_quality(self):
        self.quality_path.write_text(json.dumps(self.quality))

    def test_complete_baseline_does_not_approve_authorial_release(self):
        result = inspect(self.root)
        self.assertTrue(result['baseline_ready'])
        self.assertFalse(result['author_release_ready'])
        self.assertEqual(len(result['pending_decisions']), 6)

    def test_tabular_failures_block_authorial_gate(self):
        self.assertTrue(inspect(self.root)['audit_failures'])
        path = self.root/'reports/digit-verification.json'
        proof = json.loads((ROOT/'reports/digit-verification.json').read_text())
        path.write_text(json.dumps(proof))
        self.assertEqual(inspect(self.root)['audit_failures'], [])
        proof['failures'] = [{'text': '44', 'area': 5}]
        path.write_text(json.dumps(proof))
        self.assertTrue(inspect(self.root)['audit_failures'])
        self.assertFalse(inspect(self.root)['author_release_ready'])

    def test_stale_timer_proof_blocks_authorial_gate(self):
        path = self.root/'reports/timer-verification.json'
        proof = json.loads(path.read_text())
        proof['font_sha256'] = 'previous-font'
        path.write_text(json.dumps(proof))
        self.assertTrue(any('timer' in reason for reason in inspect(self.root)['audit_failures']))
        self.assertFalse(inspect(self.root)['author_release_ready'])

    def test_duplicate_case_cannot_replace_missing_case(self):
        self.quality['all_cases'][-1] = self.quality['all_cases'][0]
        self.write_quality()
        self.assertFalse(inspect(self.root)['baseline_ready'])

    def test_stale_report_and_missing_ink_cannot_pass(self):
        self.quality['font_sha256'] = 'stale'
        self.quality['all_cases'][-1]['mask_iou'] = None
        self.write_quality()
        result = inspect(self.root)
        self.assertFalse(result['baseline_ready'])
        self.assertEqual(len(result['technical_failures']), 2)

    def test_evidence_binds_font_and_file_contents(self):
        path = self.root/'evidence.json'
        path.write_text('{}')
        evidence = dict(path='evidence.json', font_sha256='font-a', sha256=sha(path))
        self.assertTrue(evidence_valid(self.root, evidence, 'font-a'))
        self.assertFalse(evidence_valid(self.root, evidence, 'font-b'))
        path.write_text('{"changed":true}')
        self.assertFalse(evidence_valid(self.root, evidence, 'font-a'))

    def test_authorial_scope_requires_review_and_rejects_unrelated_changes(self):
        digest = self.quality['font_sha256']
        baseline = self.root/'baseline.json'
        baseline.write_text(json.dumps(self.quality))
        changed = next(r for r in self.quality['all_cases'] if r['character'] == 'o')
        changed['mask_iou'] = .8
        report = dict(font_sha256=digest, reviewed=True,
                      baseline_quality=dict(path='baseline.json', sha256=sha(baseline),
                                            font_sha256=digest),
                      glyph_decisions={changed['codepoint']: ['D01']})
        path = self.root/'deviations.json'
        decisions = dict(baseline_checkpoint=dict(font_sha256=digest),
                         decisions=[dict(id='D01', status='accepted')])
        def save():
            path.write_text(json.dumps(report))
            decisions['authorial_deviations'] = dict(
                path='deviations.json', sha256=sha(path), font_sha256=digest)
        save()
        self.assertTrue(deviations_valid(self.root, decisions, self.quality, digest))
        report['reviewed'] = False
        save()
        self.assertFalse(deviations_valid(self.root, decisions, self.quality, digest))
        report['reviewed'] = True
        save()
        unrelated = next(r for r in self.quality['all_cases'] if r['character'] == '!')
        unrelated['fp'] += 1
        self.assertFalse(deviations_valid(self.root, decisions, self.quality, digest))


if __name__ == '__main__':
    unittest.main()
