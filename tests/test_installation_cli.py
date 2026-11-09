"""Install and remove the entry point through a separate process, including conflicts."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
SCRATCH=Path.home()/'scratch/rstack'


class InstallationCliTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='installation-',dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.target=self.base/'client/skills'

    def run_cli(self,*args,expected=0):
        result=subprocess.run([sys.executable,str(REPO/'rstack.py'),*args],capture_output=True,text=True)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result

    def test_preview_repeat_install_and_uninstall(self):
        args=['install','--target',str(self.target)]
        result=json.loads(self.run_cli(*args).stdout)
        self.assertFalse(result['applied'])
        self.assertFalse(self.target.exists())
        self.run_cli(*args,'--apply')
        link=self.target/'rstack'
        self.assertTrue(link.is_symlink())
        result=json.loads(self.run_cli(*args,'--apply').stdout)
        self.assertEqual(result['actions'][0]['action'],'unchanged')
        result=self.run_cli('workflows')
        self.assertIn('build:',result.stdout)
        self.run_cli('uninstall','--target',str(self.target))
        self.assertTrue(link.is_symlink())
        self.run_cli('uninstall','--target',str(self.target),'--apply')
        self.assertFalse(link.is_symlink())
        self.assertTrue((REPO/'skills/rstack/SKILL.md').is_file())
        self.run_cli('uninstall','--target',str(self.target),'--apply')

    def test_existing_directory_and_file_are_preserved(self):
        foreign=self.target/'rstack'
        foreign.mkdir(parents=True)
        (foreign/'user-work.txt').write_text('keep me')
        self.run_cli('install','--target',str(self.target),'--apply',expected=2)
        self.run_cli('uninstall','--target',str(self.target),'--apply',expected=2)
        self.assertEqual((foreign/'user-work.txt').read_text(),'keep me')

    def test_foreign_and_broken_symlinks_are_preserved(self):
        self.target.mkdir(parents=True)
        link=self.target/'rstack'
        other=self.base/'other'
        link.symlink_to(other)
        self.run_cli('install','--target',str(self.target),'--apply',expected=2)
        self.run_cli('uninstall','--target',str(self.target),'--apply',expected=2)
        self.assertEqual(link.readlink(),other)

    def test_all_targets_are_preflighted_before_any_write(self):
        other=self.base/'other-client'
        (other/'rstack').mkdir(parents=True)
        self.run_cli('install','--target',str(self.target),'--target',str(other),'--apply',expected=2)
        self.assertFalse((self.target/'rstack').exists())

    def test_failed_second_link_rolls_back_first_link(self):
        blocked=self.base/'file'
        blocked.write_text('keep')
        self.run_cli('install','--target',str(self.target),'--target',str(blocked/'child'),'--apply',expected=2)
        self.assertFalse((self.target/'rstack').is_symlink())
        self.assertEqual(blocked.read_text(),'keep')

    def test_entry_point_runs_through_installed_directory_link(self):
        self.run_cli('install','--target',str(self.target),'--apply')
        cli=self.target/'rstack/scripts/rstack.py'
        result=subprocess.run([sys.executable,str(cli),'workflows'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('research:',result.stdout)


if __name__=='__main__':
    unittest.main()
