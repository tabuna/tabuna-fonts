import tempfile
import unittest
from pathlib import Path
from web_cache import refresh, digest


class CacheChainTest(unittest.TestCase):
    def test_changed_font_invalidates_css_and_html_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'dist').mkdir(); (root/'sources').mkdir()
            font=root/'dist/TabunaSansVariable.woff2';font.write_bytes(b'first')
            css=root/'dist/tabuna.css';css.write_text('src:url("TabunaSansVariable.woff2?v=old")')
            for name in ['demo.css','demo.js','sources/charset.js']:(root/name).write_text('example')
            page=root/'index.html';page.write_text('<link href="dist/tabuna.css?v=old"><link href="dist/TabunaSansVariable.woff2?v=old">')
            refresh(root);first=page.read_text()
            font.write_bytes(b'second');refresh(root)
            self.assertNotEqual(first,page.read_text())
            self.assertIn('dist/tabuna.css?v='+digest(css),page.read_text())
            self.assertIn('TabunaSansVariable.woff2?v='+digest(font),css.read_text())
            second=page.read_text();refresh(root);self.assertEqual(second,page.read_text())


if __name__=='__main__':unittest.main()
