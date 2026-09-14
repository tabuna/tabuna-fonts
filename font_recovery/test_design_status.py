"""Release checks must reject stale, incomplete and unreviewed evidence."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from font_recovery.design_status import ROOT, evidence_valid, inspect, sha


class DesignStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('sources/design-decisions.json', 'reports/current-quality.json',
                     'reports/verification.json', 'dist/TabunaSansVariable.ttf', 'dist/TabunaSansVariable.woff2'):
            destination = self.root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, destination)
        self.quality_path = self.root/'reports/current-quality.json'
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


if __name__ == '__main__':
    unittest.main()
