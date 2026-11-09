"""Preview/apply links for the explicit rstack learning bundle; no downloads."""
import argparse
import json
from pathlib import Path

NAMES = ('rstack', 'exam-prep', 'practice-exam-factory', 'socratic-tutor', 'learnharness', 'study-loop')


def install(targets, apply=False, remove=False, source_root=None):
    root = Path(source_root or Path(__file__).resolve().parent / 'skills').resolve()
    actions = []
    seen = set()
    for raw in targets:
        target = Path(raw).expanduser().absolute()
        for name in NAMES:
            source = (root / name).resolve(strict=True)
            if not (source / 'SKILL.md').is_file():
                raise ValueError(f'package has no SKILL.md: {name}')
            dest = target / name
            if dest in seen:
                continue
            seen.add(dest)
            exists = dest.exists() or dest.is_symlink()
            owned = dest.is_symlink() and dest.resolve() == source
            if exists and not owned:
                raise ValueError(f'refusing existing foreign path: {dest}')
            action = ('remove' if owned else 'absent') if remove else ('unchanged' if owned else 'create')
            actions.append({'path': str(dest), 'source': str(source), 'action': action})
    if apply:
        created = []
        try:
            for action in actions:
                dest = Path(action['path'])
                if action['action'] == 'create':
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.symlink_to(action['source'], target_is_directory=True)
                    created.append(dest)
                elif action['action'] == 'remove':
                    dest.unlink()
        except OSError:
            for dest in reversed(created):
                if dest.is_symlink():
                    dest.unlink()
            raise
    return {'applied': apply, 'packages': list(NAMES), 'actions': actions}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', action='append', required=True)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--remove', action='store_true')
    args = p.parse_args()
    try:
        result = install(args.target, args.apply, args.remove)
    except (ValueError, OSError) as exc:
        p.exit(2, f'{exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
