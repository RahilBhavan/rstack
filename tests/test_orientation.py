import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class OrientationTests(unittest.TestCase):
    def test_cli_without_inventory_or_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            installed = root / 'skills/rstack'
            shutil.copytree(ROOT / 'skills/rstack', installed,
                            ignore=shutil.ignore_patterns('__pycache__'))
            state = root / 'absent-state'
            for command in ('orientation', 'orient', 'onboard'):
                result = subprocess.run([sys.executable, str(installed / 'scripts/rstack.py'),
                                         '--state-dir', str(state), command], cwd=root,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.startswith('# Welcome to rstack'))
                self.assertFalse(state.exists())
            self.assertEqual(list(root.iterdir()), [root / 'skills'])

    def test_uploaded_copy_has_the_same_guide_and_a_next_step(self):
        builder, installer = load('build_public'), load('install_public')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'public.zip'
            builder.build(archive)
            result = installer.install(archive, root / 'client', True)
            guide = root / 'client/rstack/references/orientation.md'
            self.assertEqual(guide.read_bytes(),
                             (ROOT / 'skills/rstack/references/orientation.md').read_bytes())
            self.assertIn('orient me', result['next'])
            self.assertIn('orient me', installer.install(archive, root / 'client', True)['next'])
            self.assertEqual(json.loads((guide.parent / 'manifest.json').read_text())['leaf_count'], 103)
