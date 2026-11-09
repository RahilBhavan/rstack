"""Behavior checks through the CLI with isolated, synthetic source packages."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / 'rstack.py'
SCRATCH = Path.home() / 'scratch/rstack'


class CatalogCliTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='catalog-', dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'skills'
        self.root.mkdir()
        self.state = self.base / 'state'
        self.config = self.base / 'roots.json'
        self.configure([self.root])

    def configure(self, roots, kind='local'):
        self.config.write_text(json.dumps({'roots': [dict(path=str(p), kind=kind) for p in roots]}))

    def skill(self, folder, name='example', description='A useful example skill.', body=''):
        path = self.root / folder / 'SKILL.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\nname: '+json.dumps(name)+'\ndescription: '+json.dumps(description)+'\n---\n'+body)
        return path

    def run_cli(self, *args, expected=0, cli=CLI):
        result = subprocess.run([sys.executable, str(cli), '--state-dir', str(self.state), *args],
                                text=True, capture_output=True, cwd=self.base)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def inventory(self, expected=0):
        self.run_cli('inventory', '--config', str(self.config), expected=expected)
        return json.loads((self.state/'catalog.json').read_text())

    def test_aliases_collapse_but_nested_skills_survive(self):
        manifest = self.skill('one', 'parent')
        self.skill('one/mac', 'child')
        (self.root/'alias').symlink_to(manifest.parent, target_is_directory=True)
        catalog = self.inventory()
        self.assertEqual({e['name'] for e in catalog['entries']}, {'parent', 'child'})
        parent = next(e for e in catalog['entries'] if e['name']=='parent')
        self.assertEqual(len(parent['aliases']), 2)

    def test_cycle_terminates_without_duplicate_records(self):
        self.skill('one')
        (self.root/'one/back').symlink_to(self.root, target_is_directory=True)
        self.assertEqual(len(self.inventory()['entries']), 1)

    def test_broken_link_is_visible_and_inventory_fails(self):
        (self.root/'broken').symlink_to(self.base/'absent')
        catalog=self.inventory(expected=1)
        self.assertIn('broken', catalog['issues'][0]['path'])

    def test_missing_optional_root_is_notice(self):
        self.configure([self.root, self.base/'not-installed'])
        catalog=self.inventory()
        self.assertTrue(catalog['issues'][0]['optional'])
        self.run_cli('doctor')

    def test_invalid_manifest_does_not_hide_nested_skill(self):
        path=self.skill('bad')
        path.write_text('---\nname: bad\ndescription: wrong: scalar\n---\n')
        self.skill('bad/nested', 'valid-child')
        catalog=self.inventory(expected=1)
        self.assertEqual([e['name'] for e in catalog['entries']], ['valid-child'])
        self.assertEqual(len(catalog['issues']), 1)
        self.run_cli('doctor', expected=1)

    def test_same_name_variants_are_not_silently_chosen(self):
        first=self.skill('one','tdd',body='First instructions.')
        self.skill('two','tdd',body='Different instructions.')
        catalog=self.inventory()
        self.assertEqual(len(catalog['entries']),2)
        result=self.run_cli('show','tdd', expected=2)
        self.assertIn('ambiguous', result.stderr)
        chosen=catalog['entries'][0]
        result=self.run_cli('show', chosen['id'], '--read')
        self.assertEqual(result.stdout, Path(chosen['path']).read_text()+'\n')
        first.write_text(first.read_text()+'changed')
        self.run_cli('doctor', expected=1)

    def test_identical_entry_bytes_do_not_erase_distinct_packages(self):
        self.skill('one','tdd')
        self.skill('two','tdd')
        catalog=self.inventory()
        self.assertEqual(len(catalog['entries']),2)
        report=json.loads(self.run_cli('doctor','--json').stdout)
        self.assertTrue(report['name_variants'][0]['entry_content_equal'])

    def test_vendor_namespaces_do_not_shadow_local_name(self):
        self.skill('local','pdf')
        synced=self.skill('synced/collection/pdf','pdf')
        self.inventory()
        result=json.loads(self.run_cli('show','pdf','--json').stdout)
        self.assertEqual(result['kind'],'local')
        result=json.loads(self.run_cli('show','synced/pdf','--json').stdout)
        self.assertEqual(result['path'],str(synced))

    def test_plugin_cache_namespace_retains_version(self):
        self.skill('provider/1.2.3/skills/sheets','Spreadsheets')
        self.configure([self.root],kind='plugin')
        entry=self.inventory()['entries'][0]
        self.assertEqual(entry['id'],'plugin/provider/Spreadsheets@1.2.3')
        self.assertEqual(entry['pack'],'documents')
        result=json.loads(self.run_cli('show','spreadsheets','--json').stdout)
        self.assertEqual(result['id'],entry['id'])

    def test_session_plugin_alias_resolves_only_a_unique_cached_version(self):
        self.skill('google-drive/1.0/skills/sheets','google-sheets')
        self.configure([self.root],kind='plugin')
        self.inventory()
        result=json.loads(self.run_cli('show','google-drive:google-sheets','--json').stdout)
        self.assertEqual(result['id'],'plugin/google-drive/google-sheets@1.0')
        self.skill('google-drive/2.0/skills/sheets','google-sheets')
        self.inventory()
        self.run_cli('show','google-drive:google-sheets',expected=2)
        self.run_cli('show','plugin/google-drive/google-sheets@1.0')

    def test_multiline_yaml_description_and_provenance_are_read(self):
        path=self.skill('one')
        path.write_text('---\nname: example\ndescription: >\n  Research sources\n  and compare evidence.\n---\n')
        (path.parent/'SOURCE.md').write_text('Original source: https://example.org')
        entry=self.inventory()['entries'][0]
        self.assertIn('Research sources and compare evidence.',entry['description'])
        self.assertEqual(entry['provenance']['pointers'][0]['type'],'SOURCE.md')
        self.assertEqual(entry['provenance']['status'],'unreviewed')

    def test_entry_change_and_deletion_are_detected_after_process_restart(self):
        path=self.skill('one')
        self.inventory()
        path.write_text(path.read_text()+'new content')
        report=json.loads(self.run_cli('doctor','--json',expected=1).stdout)
        self.assertEqual(report['source_issues'][0]['status'],'changed')
        path.unlink()
        report=json.loads(self.run_cli('doctor','--json',expected=1).stdout)
        self.assertEqual(report['source_issues'][0]['status'],'missing')

    def test_refresh_removes_deleted_entry_and_observes_new_skill(self):
        path=self.skill('one')
        self.inventory()
        path.unlink()
        self.skill('two','new-skill')
        self.assertEqual([e['name'] for e in self.inventory()['entries']],['new-skill'])

    def test_find_and_pack_filter_reach_unclassified_skill(self):
        self.skill('one','custom-domain','Understand unusual quarks with original evidence.')
        self.skill('two','tdd','Write tests first.')
        self.inventory()
        result=json.loads(self.run_cli('find','quarks','--json').stdout)
        self.assertEqual([e['name'] for e in result],['custom-domain'])
        result=json.loads(self.run_cli('list','--pack','extensions','--json').stdout)
        self.assertEqual([e['name'] for e in result],['custom-domain'])
        self.run_cli('find','quarks','--limit','0',expected=2)

    def test_missing_optional_plan_skills_are_reported_without_execution(self):
        path=self.skill('one','outcome-prompt')
        (path.parent/'should-not-run.py').write_text('raise RuntimeError("executed")')
        self.inventory()
        result=json.loads(self.run_cli('plan','build','--json').stdout)
        self.assertEqual(result['skills'][0]['path'],str(path))
        self.assertTrue(any('resolution_error' in e for e in result['skills']))
        self.assertTrue(all('not exercised' in e.get('capability_status','not exercised') for e in result['skills']))
        self.run_cli('plan','not-a-workflow',expected=2)

    def test_literal_link_diagnostic_does_not_claim_full_dependency_validation(self):
        self.skill('one',body='[missing](references/absent.md) [web](https://example.org)')
        self.inventory()
        result=json.loads(self.run_cli('doctor','--deep','--json').stdout)
        self.assertEqual(len(result['reference_warnings'][0]['missing_literal_references']),1)
        self.assertTrue(result['healthy_inventory'])

    def test_invalid_config_does_not_replace_last_observation(self):
        self.skill('one')
        self.inventory()
        before=(self.state/'catalog.json').read_bytes()
        self.config.write_text('{"roots": [{"path": 1}]}')
        self.run_cli('inventory','--config',str(self.config),expected=2)
        self.assertEqual((self.state/'catalog.json').read_bytes(),before)

    def test_relative_config_paths_and_persistent_config(self):
        self.skill('one')
        self.state.mkdir()
        (self.state/'roots.json').write_text(json.dumps({'roots':[{'path':'../skills'}]}))
        self.run_cli('inventory')
        entries=json.loads(self.run_cli('list','--json').stdout)
        self.assertEqual(len(entries),1)

    def test_explicit_preference_is_previewable_pinned_and_survives_restart(self):
        self.skill('one','tdd',body='A')
        self.skill('two','tdd',body='B')
        entries=self.inventory()['entries']
        chosen=entries[0]
        args=['prefer','tdd',chosen['id'],'--reason','Inspected compatible variant.']
        self.run_cli(*args)
        self.assertFalse((self.state/'preferences.json').exists())
        self.run_cli(*args,'--apply')
        entry=json.loads(self.run_cli('show','tdd','--json').stdout)
        self.assertEqual(entry['id'],chosen['id'])
        self.assertIn('Inspected',entry['selection_reason'])
        source=Path(chosen['path'])
        source.write_text(source.read_text()+'changed')
        self.run_cli('show','tdd',expected=2)
        self.inventory()
        self.run_cli('show','tdd',expected=2)
        self.run_cli(*args,'--apply')
        self.run_cli('show','tdd')

    def test_disappeared_preferred_variant_does_not_fall_back_to_remaining_copy(self):
        first=self.skill('one','tdd',body='A')
        self.skill('two','tdd',body='B')
        entries=self.inventory()['entries']
        chosen=next(e for e in entries if e['path']==str(first))
        self.run_cli('prefer','tdd',chosen['id'],'--reason','Chosen deliberately.','--apply')
        first.unlink()
        self.inventory()
        self.run_cli('show','tdd',expected=2)
        result=json.loads(self.run_cli('doctor','--json',expected=1).stdout)
        self.assertEqual(len(result['preference_issues']),1)

    def test_preference_refuses_mismatched_id_or_changed_source(self):
        source=self.skill('one','tdd')
        self.skill('two','another')
        entries=self.inventory()['entries']
        other=next(e for e in entries if e['name']=='another')
        self.run_cli('prefer','tdd',other['id'],'--reason','wrong','--apply',expected=2)
        source.write_text(source.read_text()+'changed')
        self.run_cli('prefer','tdd','tdd','--reason','stale','--apply',expected=2)
        self.assertFalse((self.state/'preferences.json').exists())

    def test_clean_skill_copy_runs_without_repository_or_private_inventory(self):
        copied=self.base/'clean-copy'
        shutil.copytree(REPO/'skills/rstack',copied,ignore=shutil.ignore_patterns('__pycache__'))
        cli=copied/'scripts/rstack.py'
        self.run_cli('workflows',cli=cli)
        self.run_cli('show','anything',expected=2,cli=cli)
        self.skill('one','outcome-prompt')
        self.run_cli('inventory','--config',str(self.config),cli=cli)
        self.run_cli('plan','build',cli=cli)
        self.run_cli('doctor',cli=cli)


if __name__=='__main__':
    unittest.main()
