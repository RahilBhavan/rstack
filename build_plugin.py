#!/usr/bin/env python3
"""Package the same public router in the portable Agent Plugins layout."""
import argparse
import json
from pathlib import Path
import zipfile
from build_public import public_files

MANIFEST = {
    '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
    'name': 'rstack', 'version': '0.4.0',
    'description': 'A portable router for 103 engineering, research, design and learning workflows.',
    'author': {'name': 'Rahil Bhavan'},
    'repository': 'https://github.com/RahilBhavan/rstack',
    'homepage': 'https://github.com/RahilBhavan/rstack/releases/tag/v0.4.0'
}


def build(output):
    files = {'rstack-plugin/skills/' + name: data for name, data in public_files().items()}
    files['rstack-plugin/plugin.json'] = json.dumps(MANIFEST, indent=2).encode()
    # Claude Code uses its own manifest location; it discovers skills/ normally.
    files['rstack-plugin/.claude-plugin/plugin.json'] = json.dumps({
        k: v for k, v in MANIFEST.items() if k != '$schema'}, indent=2).encode()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    print(json.dumps({'archive': str(output), 'skills': 104, 'files': len(files)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    build(parser.parse_args().output)
