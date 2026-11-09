"""Study-loop queue: spacing, grader gate, confident errors, interleaving, trials, signals."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/study-loop/scripts/learnq.py'
spec = importlib.util.spec_from_file_location('learnq', SCRIPT)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

D0 = date(2026, 11, 9)


def day(n):
    return D0 + timedelta(days=n)


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.data = q.load('/nonexistent/learn-queue.json')
        q.add(self.data, 'circuits', ['thevenin', 'norton'], 1, D0)

    def due_names(self, today):
        return [(i['topic'], i['subskill']) for i in q.due(self.data, today)]

    def test_new_items_are_due_today(self):
        self.assertEqual(set(self.due_names(D0)), {('circuits', 'thevenin'), ('circuits', 'norton')})

    def test_passes_expand_interval(self):
        today, gaps = D0, []
        for _ in range(5):
            q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, today)
            nxt = date.fromisoformat(self.data['items']['circuits']['thevenin']['due'])
            gaps.append((nxt - today).days)
            today = nxt
        self.assertEqual(gaps, [1, 3, 7, 21, 60])

    def test_fail_resets_interval_and_lowers_level(self):
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, D0)
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, day(1), level=2)
        q.record(self.data, 'circuits', 'thevenin', False, 'tutor', 50, day(4))
        item = self.data['items']['circuits']['thevenin']
        self.assertEqual(item['level'], 1)
        self.assertEqual(item['due'], day(5).isoformat())

    def test_high_levels_need_independent_grader(self):
        q.add(self.data, 'circuits', ['mesh'], 3, D0)
        with self.assertRaisesRegex(ValueError, 'independent'):
            q.record(self.data, 'circuits', 'mesh', True, 'tutor', 90, D0, level=4)
        self.assertEqual(self.data['items']['circuits']['mesh']['checks'], [])
        q.record(self.data, 'circuits', 'mesh', True, 'tutor', 90, D0)
        q.record(self.data, 'circuits', 'mesh', True, 'checker', 90, day(1), level=4)
        self.assertEqual(self.data['items']['circuits']['mesh']['level'], 4)

    def test_failed_check_cannot_set_level(self):
        with self.assertRaisesRegex(ValueError, 'failed'):
            q.record(self.data, 'circuits', 'thevenin', False, 'human', 50, D0, level=3)

    def test_confident_wrong_comes_first(self):
        q.record(self.data, 'circuits', 'norton', False, 'tutor', 90, D0)
        q.record(self.data, 'circuits', 'thevenin', False, 'tutor', 20, D0)
        first = q.due(self.data, day(1))[0]
        self.assertEqual(first['subskill'], 'norton')
        self.assertTrue(first['confident_wrong'])

    def test_due_interleaves_topics(self):
        q.add(self.data, 'econ', ['elasticity', 'surplus'], 1, D0)
        topics = [i['topic'] for i in q.due(self.data, D0)]
        self.assertTrue(all(a != b for a, b in zip(topics, topics[1:])), topics)

    def test_trial_needs_seven_days_and_reports_gain(self):
        q.trial_start(self.data, 'circuits', 4, 10, 'checker', D0)
        with self.assertRaisesRegex(ValueError, '7 days'):
            q.trial_end(self.data, 'circuits', 9, 10, 'checker', day(6))
        result = q.trial_end(self.data, 'circuits', 7, 10, 'code', day(7))
        self.assertAlmostEqual(result['gain'], 0.5)

    def test_trial_needs_independent_grader_and_known_topic(self):
        with self.assertRaisesRegex(ValueError, 'independent'):
            q.trial_start(self.data, 'circuits', 4, 10, 'tutor', D0)
        with self.assertRaises(KeyError):
            q.trial_start(self.data, 'ghost', 4, 10, 'checker', D0)
        q.trial_start(self.data, 'circuits', 4, 10, 'checker', D0)
        with self.assertRaisesRegex(ValueError, 'independent'):
            q.trial_end(self.data, 'circuits', 9, 10, 'tutor', day(7))

    def test_open_trial_can_be_cancelled(self):
        q.trial_start(self.data, 'circuits', 4, 10, 'checker', D0)
        with self.assertRaisesRegex(ValueError, 'already open'):
            q.trial_start(self.data, 'circuits', 4, 10, 'checker', day(1))
        q.trial_cancel(self.data, 'circuits', day(1))
        q.trial_start(self.data, 'circuits', 5, 10, 'checker', day(1))
        self.assertEqual(self.data['trials']['circuits'][0]['cancelled'], day(1).isoformat())
        self.assertNotIn('low-gain', {s['kind'] for s in q.report(self.data)['signals']})

    def test_level_raise_needs_two_passes_in_a_row(self):
        with self.assertRaisesRegex(ValueError, 'two passes in a row'):
            q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, D0, level=2)
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, D0)
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, day(1), level=2)
        self.assertEqual(self.data['items']['circuits']['thevenin']['level'], 2)

    def test_pass_cannot_lower_level_or_jump_two(self):
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, D0)
        with self.assertRaisesRegex(ValueError, 'cannot lower'):
            q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, day(1), level=0)
        with self.assertRaisesRegex(ValueError, 'one step'):
            q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 50, day(1), level=3)
        self.assertEqual(len(self.data['items']['circuits']['thevenin']['checks']), 1)

    def test_add_caps_level_rejects_blank_and_reports_existing(self):
        with self.assertRaisesRegex(ValueError, '0-3'):
            q.add(self.data, 'circuits', ['mesh'], 5, D0)
        with self.assertRaisesRegex(ValueError, 'empty'):
            q.add(self.data, 'circuits', [''], 1, D0)
        with self.assertRaisesRegex(ValueError, 'empty'):
            q.add(self.data, ' ', ['mesh'], 1, D0)
        result = q.add(self.data, 'circuits', ['thevenin', 'mesh'], 2, D0)
        self.assertEqual(result, {'added': ['mesh'], 'existing': ['thevenin']})
        self.assertEqual(self.data['items']['circuits']['thevenin']['level'], 1)

    def test_confidence_is_required(self):
        with self.assertRaisesRegex(ValueError, 'confidence'):
            q.record(self.data, 'circuits', 'thevenin', True, 'tutor', None, D0)

    def test_all_confident_errors_come_first(self):
        q.add(self.data, 'econ', ['elasticity'], 1, D0)
        q.record(self.data, 'circuits', 'thevenin', False, 'tutor', 90, D0)
        q.record(self.data, 'circuits', 'norton', False, 'tutor', 90, D0)
        q.record(self.data, 'econ', 'elasticity', False, 'tutor', 10, D0)
        flags = [i['confident_wrong'] for i in q.due(self.data, day(1))]
        self.assertEqual(flags, [True, True, False])

    def test_corrupt_state_is_refused(self):
        bad = ['[]', 'null', '5', '{"version": 1}', '{"version": 1, "items": [], "trials": {}}',
               '{"version": 1, "items": {"A": 5}, "trials": {}}', '{"version": 1, "items": {}, "trials": []}',
               '{"version": 1, "items": {"A": {"x": {}}}, "trials": {}}', '{"version": 2, "items": {}, "trials": {}}',
               '{not json',
               '{"version": 1, "items": {"A": {"x": {"level": 1, "streak": 0, "due": "2026-11-09", "checks": [{"date": "2026-11-09", "passed": false, "confidence": "x", "grader": "code"}]}}}, "trials": {}}',
               '{"version": 1, "items": {"A": {"x": {"level": 1, "streak": 0, "due": "2026-11-09", "checks": [{"date": "2026-11-09"}]}}}, "trials": {}}',
               '{"version": 1, "items": {"A": {"x": {"level": true, "streak": 0, "due": "2026-11-09", "checks": []}}}, "trials": {}}',
               '{"version": 1, "items": {"A": {"x": {"level": 99, "streak": 0, "due": "2026-11-09", "checks": []}}}, "trials": {}}',
               '{"version": 1, "items": {"A": {"x": {"level": 1, "streak": -1, "due": "2026-11-09", "checks": []}}}, "trials": {}}',
               '{"version": 1, "items": {}, "trials": {"A": [{"start": "2026-11-09"}]}}']
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'q.json'
            for text in bad:
                path.write_text(text)
                with self.assertRaises(ValueError, msg=text):
                    q.load(path)

    def test_report_flags_overconfidence_and_lapses(self):
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 95, D0)
        q.record(self.data, 'circuits', 'thevenin', False, 'tutor', 95, day(1))
        q.record(self.data, 'circuits', 'thevenin', True, 'tutor', 95, day(2))
        q.record(self.data, 'circuits', 'thevenin', False, 'tutor', 95, day(3))
        rep = q.report(self.data)
        kinds = {s['kind'] for s in rep['signals']}
        self.assertIn('overconfident', kinds)
        self.assertIn('lapsing', kinds)
        self.assertIn('self-graded', kinds)

    def test_unknown_grader_and_topic_refused(self):
        with self.assertRaises(ValueError):
            q.record(self.data, 'circuits', 'thevenin', True, 'me', 50, D0)
        with self.assertRaises(KeyError):
            q.record(self.data, 'nope', 'x', True, 'tutor', 50, D0)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / 'state/learn-queue.json'

    def run_cli(self, *args, code=0):
        r = subprocess.run([sys.executable, '-I', str(SCRIPT), '--state', str(self.state),
                            '--today', '2026-11-09', *args], capture_output=True, text=True)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r

    def test_corrupt_state_exits_cleanly(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text('[]')
        r = self.run_cli('due', code=2)
        self.assertNotIn('Traceback', r.stderr)
        self.assertIn('queue', r.stderr)

    def test_due_on_missing_state_writes_nothing(self):
        self.assertEqual(json.loads(self.run_cli('due').stdout), [])
        self.assertFalse(self.state.exists())

    def test_round_trip_and_refusal_leaves_state_unchanged(self):
        self.run_cli('add', 'circuits', 'thevenin', '--level', '3')
        before = self.state.read_text()
        self.run_cli('record', 'circuits', 'thevenin', '--pass', '--grader', 'tutor',
                     '--confidence', '50', '--level', '5', code=2)
        self.run_cli('record', 'circuits', 'thevenin', '--pass', '--grader', 'tutor', code=2)
        self.assertEqual(self.state.read_text(), before)
        self.run_cli('record', 'circuits', 'thevenin', '--pass', '--grader', 'tutor', '--confidence', '70')
        self.run_cli('record', 'circuits', 'thevenin', '--pass', '--grader', 'checker',
                     '--confidence', '80', '--level', '4')
        shown = self.run_cli('show', 'circuits').stdout
        self.assertIn('thevenin', shown)
        self.assertIn('4/5', shown)



class WiringTests(unittest.TestCase):
    def test_installed_routed_and_documented(self):
        lspec = importlib.util.spec_from_file_location('learning', REPO / 'install_learning.py')
        learning = importlib.util.module_from_spec(lspec)
        lspec.loader.exec_module(learning)
        self.assertIn('study-loop', learning.NAMES)
        ops = json.loads((REPO / 'skills/rstack/references/workflows/operations.json').read_text())
        self.assertEqual(ops['learn']['skills'][0]['name'], 'study-loop')
        packs = json.loads((REPO / 'skills/rstack/references/packs.json').read_text())
        self.assertIn('study-loop', packs['career-learning'])
        skill = (REPO / 'skills/study-loop/SKILL.md').read_text()
        self.assertTrue(skill.startswith('---\nname: study-loop\n'))
        for command in ('due', 'add', 'record', 'show', 'trial-start', 'trial-end', 'trial-cancel', 'report'):
            self.assertIn(f'learnq.py {command}', skill)


if __name__ == '__main__':
    unittest.main()
