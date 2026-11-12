#!/usr/bin/env python3
"""Search the bundled catalog with standard-library Python; never execute skills."""
import json
from pathlib import Path
import re
import sys


def words(text):
    # Match ordinary plural task words to singular descriptions (days / multi-day).
    return {w[:-1] if len(w) > 3 and w.endswith('s') else w
            for w in re.findall(r'[a-z0-9]+', text.lower())}


def search(query, root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    terms = words(query)
    rows = json.loads((root / 'references/catalog.json').read_text())
    ranked = []
    for e in rows:
        name = words(e['id'])
        description = words(e['description'])
        score = 3 * len(terms & name) + len(terms & description)
        if score or not terms:
            ranked.append((score, e['id'], e))
    return [r[2] for r in sorted(ranked, key=lambda r: (-r[0], r[1]))[:12]]


if __name__ == '__main__':
    print(json.dumps(search(' '.join(sys.argv[1:])), indent=2))
