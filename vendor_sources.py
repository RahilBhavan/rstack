"""Verify the pinned, separately licensed upstream snapshots without executing them."""
import hashlib
import json
from pathlib import Path


def contained(root, value):
    path = Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('upstream path must be repository relative')
    target = root / path
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('upstream path escapes repository')
    return target


def verified_vendor_files(root):
    root = Path(root)
    index = json.loads((root / 'docs/upstream-sources.json').read_text())
    expected = {}
    for family in index['families']:
        base = contained(root, family['root'])
        if not family['root'].startswith('vendor/'):
            raise ValueError('upstream root must be under vendor')
        entries = []
        for manifest in family['manifests']:
            entries.extend(json.loads(contained(root, manifest).read_text()))
        if len(entries) != family['file_count']:
            raise ValueError('upstream file count differs from manifest')
        for entry in entries:
            path = contained(root, entry['path'])
            if not path.is_relative_to(base) or entry['path'] in expected:
                raise ValueError('duplicate or foreign upstream file')
            if path.is_symlink() or not path.is_file():
                raise ValueError('missing or linked upstream file: ' + entry['path'])
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('changed upstream file: ' + entry['path'])
            expected[entry['path']] = entry['sha256']
        disk = {p.relative_to(root).as_posix() for p in base.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts}
        listed = {entry['path'] for entry in entries}
        if disk != listed:
            raise ValueError('unlisted upstream files: ' + family['name'])
        count = len(list(contained(root, family['skill_root']).rglob('SKILL.md')))
        if count != family['skill_count']:
            raise ValueError('upstream skill count differs: ' + family['name'])
    return expected
