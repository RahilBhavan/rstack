"""Real pinned snapshots remain intact, discoverable and unambiguous by author."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vendor_sources import contained, verified_vendor_files

REPO = Path(__file__).resolve().parents[1]


class UpstreamBundleTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.home() / 'scratch/rstack'
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='upstream-check-', dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / 'state'
        index = json.loads((REPO / 'docs/upstream-sources.json').read_text())
        roots = [{'path': str(REPO / 'skills'), 'kind': 'local', 'label': 'rstack'}]
        roots.extend({'path': str(REPO / path), 'kind': 'vendored', 'label': family['name']}
                     for family in index['families'] for path in family['discovery_roots'])
        self.config = self.root / 'roots.json'
        self.config.write_text(json.dumps({'roots': roots}))

    def cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(REPO / 'rstack.py'),
                                 '--state-dir', str(self.state), *args],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout) if expected == 0 else result

    def inventory(self):
        return self.cli('inventory', '--config', str(self.config), '--json')

    def test_all_pinned_files_and_full_source_counts(self):
        self.assertEqual(len(verified_vendor_files(REPO)), 773)
        index = json.loads((REPO / 'docs/upstream-sources.json').read_text())
        self.assertEqual({f['name']: f['skill_count'] for f in index['families']},
                         {'mattpocock': 39, 'poteto': 58, 'theo': 9})

    def test_active_sources_are_reachable_with_author_ids(self):
        catalog = self.inventory()
        self.assertEqual(len(catalog['entries']), 104)
        self.assertFalse(catalog['issues'])
        for name in ('vendor/mattpocock/tdd', 'vendor/poteto/tdd', 'vendor/theo/council'):
            entry = self.cli('show', name, '--json')
            self.assertEqual(entry['id'], name)
            self.assertTrue(Path(entry['path']).is_file())
        self.assertTrue(self.cli('doctor', '--json')['healthy_inventory'])

    def test_find_can_select_an_upstream_family(self):
        self.inventory()
        matches = self.cli('find', 'mattpocock', '--limit', '100', '--json')
        self.assertEqual(len(matches), 31)
        self.assertTrue(all(e['id'].startswith('vendor/mattpocock/') for e in matches))

    def test_bare_collision_does_not_silently_pick_author(self):
        self.inventory()
        result = self.cli('show', 'tdd', expected=2)
        self.assertIn('ambiguous', result.stderr)
        self.assertIn('vendor/mattpocock/tdd', result.stderr)
        self.assertIn('vendor/poteto/tdd', result.stderr)

    def test_default_roots_register_active_vendor_trees(self):
        sys.path.insert(0, str(REPO / 'skills/rstack/scripts'))
        from rstacklib.catalog import default_roots
        roots = [r for r in default_roots(REPO) if r['kind'] == 'vendored']
        self.assertEqual(len(roots), 5)
        self.assertTrue(all(Path(r['path']).is_dir() for r in roots))
        self.assertTrue(all('in-progress' not in r['path'] for r in roots))

    def fixture(self):
        (self.root / 'docs').mkdir()
        (self.root / 'vendor/author/skills/item').mkdir(parents=True)
        p = self.root / 'vendor/author/skills/item/SKILL.md'
        p.write_text('fixture')
        import hashlib
        entry = {'path': str(p.relative_to(self.root)),
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        (self.root / 'docs/hash.json').write_text(json.dumps([entry]))
        family = {'name': 'author', 'root': 'vendor/author', 'file_count': 1,
                  'skill_root': 'vendor/author/skills', 'skill_count': 1,
                  'manifests': ['docs/hash.json']}
        (self.root / 'docs/upstream-sources.json').write_text(json.dumps({'families': [family]}))
        return p

    def test_changed_file_is_rejected(self):
        p = self.fixture()
        p.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'changed upstream'):
            verified_vendor_files(self.root)

    def test_unlisted_file_is_rejected(self):
        self.fixture()
        (self.root / 'vendor/author/unlisted').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'unlisted upstream'):
            verified_vendor_files(self.root)

    def test_manifest_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            contained(self.root, '../outside')


if __name__ == '__main__':
    unittest.main()
