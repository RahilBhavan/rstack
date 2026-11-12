#!/usr/bin/env python3
"""Build the reviewed public library from this repository only, never host caches."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'skills/rstack/scripts'))
from rstacklib.catalog import scan
from rstacklib.planning import pack_for
from vendor_sources import verified_vendor_files


def public_files():
    verified_vendor_files(ROOT)
    # Imported learning resources must still match their reviewed source records.
    for manifest in ('exam-source-manifest.json', 'tutor-source-manifest.json'):
        data = json.loads((ROOT / 'docs' / manifest).read_text())
        for entry in data['files']:
            path = ROOT / 'skills' / entry['file']
            if not path.resolve().is_relative_to(ROOT / 'skills') or path.is_symlink():
                raise ValueError('Unsafe learning source')
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Changed learning source: ' + entry['file'])
    roots = [{'path': str(ROOT / 'skills'), 'kind': 'local', 'label': 'rstack'}]
    for author, dirs in [('mattpocock', ['engineering', 'misc', 'productivity']),
                         ('poteto', ['']), ('theo', [''])]:
        roots.extend({'path': str(ROOT / 'vendor' / author / 'skills' / d),
                      'kind': 'vendored', 'label': author} for d in dirs)
    catalog = scan(roots, pack_for)
    if catalog['issues']:
        raise ValueError('Public discovery has errors')
    entries = [e for e in catalog['entries'] if e['name'] != 'rstack']
    # Fixed reviewed scope: expanding it requires a deliberate license/content review.
    if len(entries) != 103:
        raise ValueError('Reviewed scope changed; expected 103 leaf skills')
    files = {'rstack/SKILL.md': (ROOT / 'public/SKILL.md').read_bytes(),
             'rstack/scripts/find.py': (ROOT / 'public/find.py').read_bytes()}
    files['rstack/references/orientation.md'] = (ROOT / 'skills/rstack/references/orientation.md').read_bytes()
    records = []
    for e in entries:
        source = Path(e['path']).relative_to(ROOT).as_posix()
        records.append({'id': e['id'], 'name': e['name'], 'description': e['description'],
                        'path': 'references/source/' + source.replace('SKILL.md', 'instructions.md'),
                        'source_path': source, 'entry_sha256': e['entry_sha256']})
    # Keep the full reviewed source trees, including binary assets, notices, parent
    # references and reference-only drafts. Only entry filenames change; bytes don't.
    for directory in ('skills', 'vendor', 'docs'):
        for path in sorted((ROOT / directory).rglob('*')):
            rel = path.relative_to(ROOT)
            if '__pycache__' in rel.parts or (directory == 'skills' and rel.parts[1] == 'rstack'):
                continue
            if path.is_symlink():
                raise ValueError('Symlink not permitted in public sources: ' + str(rel))
            if path.is_file():
                dest = rel.as_posix()
                if path.name.lower() == 'skill.md':
                    dest = str(Path(dest).with_name('instructions.md'))
                files['rstack/references/source/' + dest] = path.read_bytes()
    for path in (ROOT / 'vendor').glob('*/LICENSE*'):
        files['rstack/licenses/' + path.parent.name + '-' + path.name] = path.read_bytes()
    for name in ('LICENSE', 'ATTRIBUTION.md'):
        files['rstack/' + name] = (ROOT / name).read_bytes()
        files['rstack/references/source/' + name] = (ROOT / name).read_bytes()
    lines = ['# Public skill index\n', '103 leaf workflows plus the rstack router. '
             'Read only selected entries. Drafts under in-progress are source references, not enabled entries.\n']
    for e in records:
        desc = ' '.join(e['description'].split())
        lines.append(f"- [{e['id']}]({e['path'].removeprefix('references/')}): {desc}\n")
    files['rstack/references/index.md'] = '\n'.join(lines).encode()
    files['rstack/references/catalog.json'] = json.dumps(records, indent=2).encode()
    files['rstack/references/compatibility.md'] = (ROOT / 'public/compatibility.md').read_bytes()
    for name, data in files.items():
        if name.endswith(('.md', '.json', '.py', '.yaml', '.yml', '.txt', '.sh')):
            text = data.decode('utf-8')
            if any(s in text for s in ('/home/rahil/', '/Users/rahil/', 'rahil@umich.edu')):
                raise ValueError('Personal path or account in public file: ' + name)
    files['rstack/references/manifest.json'] = json.dumps({
        'format': 1, 'distribution': 'public-reviewed', 'leaf_count': len(records),
        'files': {n.removeprefix('rstack/'): hashlib.sha256(d).hexdigest()
                  for n, d in sorted(files.items())}}, indent=2).encode()
    return files


def build(output):
    files = public_files()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Fixed timestamps, ordering and modes make the archive reproducible.
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    print(json.dumps({'archive': str(output), 'skills': 104, 'files': len(files)}))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    try:
        build(parser.parse_args().output)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')
