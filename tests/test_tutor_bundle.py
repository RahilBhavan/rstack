"""Vendored tutor packages: byte-for-byte integrity, install membership, learn routing."""
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('learning', REPO / 'install_learning.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VENDORED = ('socratic-tutor', 'learnharness')
LOCAL_RECORDS = {'SOURCE.md'}


class TutorBundleTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((REPO / 'docs/tutor-source-manifest.json').read_text())

    def test_installer_ships_vendored_packages(self):
        for name in VENDORED:
            self.assertIn(name, module.NAMES)
            self.assertTrue((REPO / 'skills' / name / 'SKILL.md').is_file())
            self.assertTrue((REPO / 'skills' / name / 'SOURCE.md').is_file())

    def test_files_match_manifest_hashes(self):
        for entry in self.manifest['files']:
            data = (REPO / 'skills' / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'], entry['file'])

    def test_no_unlisted_files(self):
        listed = {e['file'] for e in self.manifest['files']}
        for name in VENDORED:
            for path in (REPO / 'skills' / name).rglob('*'):
                rel = path.relative_to(REPO / 'skills').as_posix()
                if path.is_file() and path.name not in LOCAL_RECORDS and '__pycache__' not in rel:
                    self.assertIn(rel, listed)

    def test_learn_workflow_and_pack_route_to_tutors(self):
        ops = json.loads((REPO / 'skills/rstack/references/workflows/operations.json').read_text())
        names = [s['name'] for s in ops['learn']['skills']]
        packs = json.loads((REPO / 'skills/rstack/references/packs.json').read_text())
        for name in VENDORED:
            self.assertIn(name, names)
            self.assertIn(name, packs['career-learning'])


if __name__ == '__main__':
    unittest.main()
