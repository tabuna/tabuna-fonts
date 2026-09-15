"""Prevent Latin/Cyrillic counterparts from losing the shared bowl rule."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from character import ROUND_FAMILIES


class CharacterFamiliesTest(unittest.TestCase):
    def test_cross_script_counterparts_share_a_rule(self):
        rules = {}
        for family, (characters, amplitude) in ROUND_FAMILIES.items():
            for character in characters.replace(' ', ''):
                self.assertNotIn(character, rules, 'A glyph must not receive tension twice')
                rules[character] = (family, amplitude)
        for counterparts in ('aа', 'PР', 'BВв', 'oо', 'OО', 'cс', 'CС', 'eе', 'pр'):
            with self.subTest(counterparts=counterparts):
                self.assertTrue(all(c in rules for c in counterparts))
                self.assertEqual(len({rules[c] for c in counterparts}), 1)


if __name__ == '__main__':
    unittest.main()
