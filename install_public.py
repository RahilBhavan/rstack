#!/usr/bin/env python3
"""Install a public rstack ZIP without dependencies. Preview unless --apply is set."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile


def contents(archive):
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        if len(entries) > 5000 or sum(e.file_size for e in entries) > 250_000_000:
            raise ValueError('Archive exceeds public bundle limits')
        files = {}
        for e in entries:
            name = e.filename
            path = PurePosixPath(name)
            mode = e.external_attr >> 16
            if ('\\' in name or ':' in name or path.is_absolute() or '..' in path.parts
                    or not name.startswith('rstack/') or stat.S_ISLNK(mode)
                    or e.is_dir() or name in files):
                raise ValueError('Unsafe or duplicate archive member: ' + name)
            files[name] = z.read(e)
    manifest_name = 'rstack/references/manifest.json'
    manifest = json.loads(files[manifest_name])
    if manifest.get('format') != 1 or manifest.get('distribution') != 'public-reviewed':
        raise ValueError('Not a reviewed public rstack bundle')
    expected = manifest['files']
    if set(files) != {'rstack/' + name for name in expected} | {manifest_name}:
        raise ValueError('Archive file list differs from manifest')
    for name, digest in expected.items():
        if hashlib.sha256(files['rstack/' + name]).hexdigest() != digest:
            raise ValueError('Archive hash mismatch: ' + name)
    if 'rstack/SKILL.md' not in files or sum(n.lower().endswith('/skill.md') for n in files) != 1:
        raise ValueError('Expected exactly one router SKILL.md')
    return {n.removeprefix('rstack/'): d for n, d in files.items()}


def install(archive, target, apply=False):
    files = contents(archive)
    destination = Path(target).expanduser().absolute() / 'rstack'
    if destination.is_symlink():
        raise ValueError('Refusing existing symlink: ' + str(destination))
    if destination.exists():
        if not destination.is_dir():
            raise ValueError('Refusing existing file: ' + str(destination))
        actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*')
                  if p.is_file() or p.is_symlink()}
        if actual == set(files) and all(not (destination / n).is_symlink()
                                       and (destination / n).read_bytes() == d
                                       for n, d in files.items()):
            return {'status': 'already-installed', 'destination': str(destination), 'written': False,
                    'next': 'Ask your agent: Use rstack to orient me.'}
        raise ValueError('Existing installation differs; preserve it and use a fresh target: ' + str(destination))
    if apply:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.mkdir()  # Exclusive reservation; never overwrite another install.
        try:
            for name, data in files.items():
                p = destination / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return {'status': 'installed' if apply else 'preview', 'destination': str(destination),
            'files': len(files), 'written': apply,
            'next': 'Ask your agent: Use rstack to orient me.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--client', choices=['codex', 'claude', 'shared'])
    target.add_argument('--target', type=Path, help='Any Agent Skills-compatible root')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    directory = args.target
    if args.client:
        directory = Path.home() / {'codex': '.codex', 'claude': '.claude', 'shared': '.agents'}[args.client] / 'skills'
    try:
        print(json.dumps(install(args.archive, directory, args.apply), indent=2))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
