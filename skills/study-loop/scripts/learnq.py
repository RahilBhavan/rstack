"""Local spaced-review queue for rstack's study loop.

Standard library only. No network, no model calls, no background jobs. The queue is
private local state, outside the repository and outside LearnHarness's data folder.
Every refused action raises before anything is written.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

INTERVALS = (1, 3, 7, 21, 60)  # days until the next review after 1, 2, 3, 4, 5+ passes in a row
GRADERS = ('tutor', 'checker', 'code', 'human')
INDEPENDENT = ('checker', 'code', 'human')
CONFIDENT = 70  # a failed answer at or above this confidence is a confident error
TRIAL_DAYS = 7
OVERCONFIDENCE_GAP = 0.15
LOW_GAIN = 0.3


def default_state():
    env = os.environ.get('RSTACK_LEARN_STATE')
    return Path(env) if env else Path.home() / '.local/state/rstack/learn-queue.json'


def load(path):
    path = Path(path)
    if not path.exists():
        return {'version': 1, 'items': {}, 'trials': {}}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ValueError(f'queue file {path} is not valid JSON ({exc}); nothing was changed') from None
    if isinstance(data, dict) and data.get('version') not in (None, 1):
        raise ValueError(f'unsupported queue version {data["version"]!r} in {path}; nothing was changed')
    if not _well_formed(data):
        raise ValueError(f'queue file {path} is malformed; fix or move it, nothing was changed')
    return data


def _is_date(value):
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def _int(value, low, high=None):
    return type(value) is int and value >= low and (high is None or value <= high)


def _check_ok(c):
    return (isinstance(c, dict) and _is_date(c.get('date')) and type(c.get('passed')) is bool
            and c.get('grader') in GRADERS and _int(c.get('confidence'), 0, 100))


def _trial_ok(x):
    return (isinstance(x, dict) and _is_date(x.get('start')) and _int(x.get('out_of'), 1)
            and _int(x.get('pre'), 0, x['out_of']))


def _well_formed(data):
    if not (isinstance(data, dict) and data.get('version') == 1
            and isinstance(data.get('items'), dict) and isinstance(data.get('trials'), dict)):
        return False
    for items in data['items'].values():
        if not isinstance(items, dict):
            return False
        for item in items.values():
            if not (isinstance(item, dict) and _int(item.get('level'), 0, 5) and _int(item.get('streak'), 0)
                    and _is_date(item.get('due')) and isinstance(item.get('checks'), list)
                    and all(_check_ok(c) for c in item['checks'])):
                return False
    return all(isinstance(trials, list) and all(_trial_ok(x) for x in trials)
               for trials in data['trials'].values())


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.learnq-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, indent=2)
            out.write('\n')
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _level(value):
    if not isinstance(value, int) or not 0 <= value <= 5:
        raise ValueError('level must be an integer from 0 to 5')
    return value


def _item(data, topic, subskill):
    try:
        return data['items'][topic][subskill]
    except KeyError:
        raise KeyError(f'unknown subskill: {topic} / {subskill}; add it first') from None


def add(data, topic, subskills, level, today):
    """Add diagnosed subskills. A diagnostic sets levels 0-3; existing ones stay as they are."""
    if _level(level) > 3:
        raise ValueError('add sets levels 0-3; levels 4-5 need record with an independent grader')
    if not topic.strip() or not subskills or not all(name.strip() for name in subskills):
        raise ValueError('topic and subskill names must not be empty')
    items = data['items'].setdefault(topic, {})
    result = {'added': [], 'existing': []}
    for name in subskills:
        if name in items:
            result['existing'].append(name)
        else:
            items[name] = {'level': level, 'streak': 0, 'due': today.isoformat(), 'checks': []}
            result['added'].append(name)
    return result


def record(data, topic, subskill, passed, grader, confidence, today, level=None):
    """Log one check and reschedule.

    Levels 4-5 need a grader other than the tutor. Raising a level needs two passes in
    a row, this one included, mirroring socratic-tutor's two-check rule.
    """
    item = _item(data, topic, subskill)
    if grader not in GRADERS:
        raise ValueError(f'grader must be one of {", ".join(GRADERS)}')
    if confidence is None or not 0 <= confidence <= 100:
        raise ValueError('confidence is required on every check, as 0-100')
    if level is not None:
        _level(level)
        if not passed:
            raise ValueError('a failed check cannot set a level; the level drops by one')
        if level >= 4 and grader not in INDEPENDENT:
            raise ValueError('levels 4-5 need an independent grader (checker, code or human), not the tutor')
        if level < item['level']:
            raise ValueError('a pass cannot lower a level; record a fail instead')
        if level > item['level'] + 1:
            raise ValueError('a level rises one step at a time')
        if level > item['level'] and item['streak'] + 1 < 2:
            raise ValueError('raising a level needs two passes in a row; record this pass without --level')
    if passed:
        item['streak'] += 1
        if level is not None:
            item['level'] = level
        gap = INTERVALS[min(item['streak'], len(INTERVALS)) - 1]
    else:
        item['streak'] = 0
        item['level'] = max(item['level'] - 1, 0)
        gap = INTERVALS[0]
    item['due'] = (today + timedelta(days=gap)).isoformat()
    item['checks'].append({'date': today.isoformat(), 'passed': passed,
                           'grader': grader, 'confidence': confidence})
    return item


def _confident_wrong(item):
    last = item['checks'][-1] if item['checks'] else None
    return bool(last and not last['passed'] and (last['confidence'] or 0) >= CONFIDENT)


def due(data, today):
    """Due items: confident errors first, then oldest and weakest, mixing topics."""
    rows = []
    for topic, items in data['items'].items():
        for name, item in items.items():
            if date.fromisoformat(item['due']) <= today:
                rows.append({'topic': topic, 'subskill': name, 'level': item['level'],
                             'due': item['due'], 'confident_wrong': _confident_wrong(item)})
    rows.sort(key=lambda r: (r['due'], r['level']))
    mixed = []
    for group in ([r for r in rows if r['confident_wrong']], [r for r in rows if not r['confident_wrong']]):
        while group:
            last = mixed[-1]['topic'] if mixed else None
            pick = next((r for r in group if r['topic'] != last), group[0])
            group.remove(pick)
            mixed.append(pick)
    return mixed


def _score(score, out_of):
    if out_of <= 0 or not 0 <= score <= out_of:
        raise ValueError('score must be between 0 and out_of, and out_of above 0')


def _trial_grader(grader):
    if grader not in INDEPENDENT:
        raise ValueError('trial tests need an independent grader (checker, code or human)')


def _open_trial(data, topic):
    trials = data['trials'].get(topic) or []
    if trials and 'post' not in trials[-1] and 'cancelled' not in trials[-1]:
        return trials[-1]
    return None


def trial_start(data, topic, score, out_of, grader, today):
    if topic not in data['items']:
        raise KeyError(f'unknown topic: {topic}; add its subskills first')
    _trial_grader(grader)
    _score(score, out_of)
    open_trial = _open_trial(data, topic)
    if open_trial:
        raise ValueError(f'a trial for {topic} is already open since {open_trial["start"]}; end or cancel it')
    trials = data['trials'].setdefault(topic, [])
    trials.append({'start': today.isoformat(), 'pre': score, 'out_of': out_of, 'pre_grader': grader})
    return trials[-1]


def trial_cancel(data, topic, today):
    trial = _open_trial(data, topic)
    if not trial:
        raise ValueError(f'no open trial for {topic}')
    trial['cancelled'] = today.isoformat()
    return trial


def trial_end(data, topic, score, out_of, grader, today):
    trial = _open_trial(data, topic)
    if not trial:
        raise ValueError(f'no open trial for {topic}')
    _trial_grader(grader)
    if out_of != trial['out_of']:
        raise ValueError('the post-test must have the same number of questions as the pre-test')
    _score(score, out_of)
    waited = (today - date.fromisoformat(trial['start'])).days
    if waited < TRIAL_DAYS:
        raise ValueError(f'the post-test needs {TRIAL_DAYS} days after the pre-test; {waited} have passed')
    room = out_of - trial['pre']
    trial.update(end=today.isoformat(), post=score, post_grader=grader, gain=(score - trial['pre']) / room if room else None)
    return trial


def report(data):
    """Per-topic evidence plus signals that the loop itself needs a change."""
    topics, signals = {}, []
    for topic, items in data['items'].items():
        checks = [c for item in items.values() for c in item['checks']]
        passes = [c for c in checks if c['passed']]
        rated = [c for c in checks if c['confidence'] is not None]
        independent = sum(c['grader'] in INDEPENDENT for c in passes)
        summary = {
            'subskills': len(items),
            'mean_level': round(sum(i['level'] for i in items.values()) / len(items), 2) if items else 0,
            'checks': len(checks),
            'pass_rate': round(len(passes) / len(checks), 2) if checks else None,
            'independent_passes': independent,
        }
        if len(rated) >= 3:
            confidence = sum(c['confidence'] for c in rated) / len(rated) / 100
            accuracy = sum(c['passed'] for c in rated) / len(rated)
            summary['calibration_gap'] = round(confidence - accuracy, 2)
            if confidence - accuracy > OVERCONFIDENCE_GAP:
                signals.append({'kind': 'overconfident', 'topic': topic, 'gap': summary['calibration_gap']})
        if len(passes) >= 2 and independent == 0:
            signals.append({'kind': 'self-graded', 'topic': topic, 'passes': len(passes)})
        for name, item in items.items():
            lapses, seen_pass = 0, False
            for c in item['checks']:
                lapses += seen_pass and not c['passed']
                seen_pass = seen_pass or c['passed']
            if lapses >= 2:
                signals.append({'kind': 'lapsing', 'topic': topic, 'subskill': name, 'lapses': lapses})
        topics[topic] = summary
    for topic, trials in data['trials'].items():
        for t in trials:
            if t.get('gain') is not None and t['gain'] < LOW_GAIN:
                signals.append({'kind': 'low-gain', 'topic': topic, 'gain': round(t['gain'], 2), 'end': t['end']})
    return {'topics': topics, 'trials': data['trials'], 'signals': signals}


def show(data, topic):
    items = data['items'].get(topic)
    if not items:
        raise KeyError(f'unknown topic: {topic}')
    def bar(fraction):
        filled = round(fraction * 10)
        return '█' * filled + '░' * (10 - filled)
    mean = sum(i['level'] for i in items.values()) / len(items) / 5
    width = max(len(n) for n in items) + 2
    lines = [f'Topic: {topic}    overall: {bar(mean)} {round(mean * 100)}%', '-' * (width + 34)]
    for name, item in items.items():
        flag = '  ! confident error' if _confident_wrong(item) else ''
        lines.append(f'{name:<{width}}[{bar(item["level"] / 5)}]  {item["level"]}/5  due {item["due"]}{flag}')
    return '\n'.join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--state', type=Path, default=None, help='queue file (default ~/.local/state/rstack/learn-queue.json)')
    p.add_argument('--today', type=date.fromisoformat, default=None, help='YYYY-MM-DD, for tests and backfills')
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add', help='add subskills after a diagnostic')
    a.add_argument('topic'); a.add_argument('subskills', nargs='+'); a.add_argument('--level', type=int, default=0)
    r = sub.add_parser('record', help='log one check and reschedule')
    r.add_argument('topic'); r.add_argument('subskill')
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument('--pass', dest='passed', action='store_true'); g.add_argument('--fail', dest='passed', action='store_false')
    r.add_argument('--grader', required=True, choices=GRADERS); r.add_argument('--confidence', type=int, required=True)
    r.add_argument('--level', type=int)
    sub.add_parser('due', help='list due reviews in study order')
    s = sub.add_parser('show', help='render one topic as a skill map'); s.add_argument('topic')
    for name in ('trial-start', 'trial-end'):
        t = sub.add_parser(name, help=f'{name.replace("-", " ")}: same-size pre/post test, {TRIAL_DAYS} days apart')
        t.add_argument('topic'); t.add_argument('score', type=int); t.add_argument('out_of', type=int)
        t.add_argument('--grader', required=True, choices=INDEPENDENT)
    c = sub.add_parser('trial-cancel', help='abandon an open trial without a result'); c.add_argument('topic')
    sub.add_parser('report', help='evidence and signals for improving the loop')
    args = p.parse_args(argv)
    state = args.state or default_state()
    today = args.today or date.today()
    try:
        data = load(state)
        if args.cmd == 'due':
            print(json.dumps(due(data, today), indent=2)); return
        if args.cmd == 'show':
            print(show(data, args.topic)); return
        if args.cmd == 'report':
            print(json.dumps(report(data), indent=2)); return
        if args.cmd == 'add':
            result = add(data, args.topic, args.subskills, args.level, today)
        elif args.cmd == 'record':
            result = record(data, args.topic, args.subskill, args.passed, args.grader, args.confidence, today, args.level)
        elif args.cmd == 'trial-start':
            result = trial_start(data, args.topic, args.score, args.out_of, args.grader, today)
        elif args.cmd == 'trial-cancel':
            result = trial_cancel(data, args.topic, today)
        else:
            result = trial_end(data, args.topic, args.score, args.out_of, args.grader, today)
        save(state, data)
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        message = exc.args[0] if isinstance(exc, KeyError) and exc.args else exc
        p.exit(2, f'{message}\n')


if __name__ == '__main__':
    main()
