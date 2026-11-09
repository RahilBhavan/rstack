"""Observable install behavior for the explicit learning bundle."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('learning', Path(__file__).parents[1] / 'install_learning.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LearningInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'skills'
        for name in module.NAMES:
            p = self.source / name
            p.mkdir(parents=True)
            (p / 'SKILL.md').write_text('test package')
        self.a = self.root / 'codex'
        self.b = self.root / 'claude'

    def test_preview_repeat_and_owned_removal(self):
        r = module.install([self.a, self.b], source_root=self.source)
        self.assertEqual(len(r['actions']), 2 * len(module.NAMES))
        self.assertFalse(self.a.exists())
        module.install([self.a, self.b], True, source_root=self.source)
        self.assertTrue(all((p / n).resolve() == (self.source / n).resolve() for p in (self.a, self.b) for n in module.NAMES))
        r = module.install([self.a, self.b], True, source_root=self.source)
        self.assertTrue(all(a['action'] == 'unchanged' for a in r['actions']))
        marker = self.a / 'unrelated'
        marker.write_text('keep')
        module.install([self.a, self.b], True, True, self.source)
        self.assertEqual(marker.read_text(), 'keep')
        self.assertFalse((self.a / 'exam-prep').is_symlink())
        self.assertTrue((self.source / 'exam-prep/SKILL.md').is_file())

    def test_conflict_preflight_writes_nothing(self):
        (self.b / 'exam-prep').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'foreign'):
            module.install([self.a, self.b], True, source_root=self.source)
        self.assertFalse(self.a.exists())
        self.assertTrue((self.b / 'exam-prep').is_dir())

    def test_broken_foreign_link_is_not_replaced(self):
        self.a.mkdir()
        (self.a / 'rstack').symlink_to(self.root / 'missing')
        with self.assertRaisesRegex(ValueError, 'foreign'):
            module.install([self.a], True, source_root=self.source)
        self.assertTrue((self.a / 'rstack').is_symlink())
