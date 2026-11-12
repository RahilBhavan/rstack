import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PublicBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = module('build_public')
        cls.installer = module('install_public')
        cls.files = cls.builder.public_files()

    def archive(self, root, mutate=None):
        files = dict(self.files)
        if mutate:
            mutate(files)
        archive = root / 'bundle.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for n, d in files.items():
                z.writestr(n, d)
        return archive

    def test_clean_install_repeat_conflict_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.archive(root)
            target = root / 'client'
            self.assertEqual(self.installer.install(archive, target)['status'], 'preview')
            self.assertFalse(target.exists())
            self.installer.install(archive, target, True)
            installed = target / 'rstack'
            manifest = json.loads((installed / 'references/manifest.json').read_text())
            for name, expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256((installed / name).read_bytes()).hexdigest(), expected)
            self.assertEqual(self.installer.install(archive, target, True)['status'], 'already-installed')
            result = subprocess.run([sys.executable, '-I', str(installed / 'scripts/find.py'),
                                     'test driven development'], capture_output=True, text=True, check=True)
            rows = json.loads(result.stdout)
            self.assertTrue(any(r['name'] == 'tdd' for r in rows))
            for row in rows:
                self.assertTrue((installed / row['path']).is_file())
            result = subprocess.run([sys.executable, '-I', str(installed / 'scripts/find.py'),
                                     'SQL practice several days'], capture_output=True, text=True, check=True)
            self.assertIn('study-loop', [r['name'] for r in json.loads(result.stdout)])
            (installed / 'SKILL.md').write_text('user edit')
            with self.assertRaises(ValueError):
                self.installer.install(archive, target, True)
            self.assertEqual((installed / 'SKILL.md').read_text(), 'user edit')

    def test_tampering_traversal_and_unlisted_files(self):
        mutations = [lambda f: f.update({'rstack/SKILL.md': b'changed'}),
                     lambda f: f.update({'rstack/../../escape': b'bad'}),
                     lambda f: f.update({'rstack/unlisted': b'bad'}),
                     lambda f: f.update({'rstack/..\\escape': b'bad'})]
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive = self.archive(root, mutation)
                with self.assertRaises(ValueError):
                    self.installer.install(archive, root / 'client', True)
                self.assertFalse((root / 'client').exists())

    def test_all_sources_assets_and_licenses_are_preserved(self):
        catalog = json.loads(self.files['rstack/references/catalog.json'])
        self.assertEqual(len(catalog), 103)
        for e in catalog:
            self.assertEqual(self.files['rstack/' + e['path']], (ROOT / e['source_path']).read_bytes())
        for path in (ROOT / 'vendor').rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if path.name.lower() == 'skill.md':
                rel = str(Path(rel).with_name('instructions.md'))
            self.assertEqual(self.files['rstack/references/source/' + rel], path.read_bytes())
        self.assertIn('rstack/licenses/poteto-LICENSE', self.files)
        self.assertIn('rstack/references/source/skills/learnharness/LICENSE', self.files)
        self.assertEqual(sum(n.lower().endswith('/skill.md') for n in self.files), 1)

    def test_index_links_and_source_bytes(self):
        import re
        router = self.files['rstack/SKILL.md'].decode()
        for link in re.findall(r'\]\(([^)]+)\)', router):
            self.assertIn('rstack/' + link, self.files)
        index = self.files['rstack/references/index.md'].decode()
        for link in re.findall(r'\]\(([^)]+)\)', index):
            self.assertIn('rstack/references/' + link, self.files)

    def test_archive_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a.zip', Path(tmp) / 'b.zip'
            self.builder.build(a)
            self.builder.build(b)
            self.assertEqual(a.read_bytes(), b.read_bytes())


class PluginTests(unittest.TestCase):
    def test_plugin_layout(self):
        plugin = module('build_plugin')
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'plugin.zip'
            plugin.build(archive)
            with zipfile.ZipFile(archive) as z:
                self.assertIn('rstack-plugin/skills/rstack/SKILL.md', z.namelist())
                manifest = json.loads(z.read('rstack-plugin/plugin.json'))
                self.assertEqual(manifest['name'], 'rstack')
                self.assertEqual(manifest['version'], '0.4.0')
                self.assertIn('rstack-plugin/.claude-plugin/plugin.json', z.namelist())
