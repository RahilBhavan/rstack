#!/usr/bin/env python3
"""Validate package metadata, workflow contracts and repository-local doc links."""
import json
import hashlib
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
errors = []
skill = ROOT / "skills/rstack"
parts = re.split(r"^---\s*$", (skill / "SKILL.md").read_text(), maxsplit=2, flags=re.M)
metadata = yaml.safe_load(parts[1])
if metadata.get("name") != "rstack" or not isinstance(metadata.get("description"), str):
    errors.append("rstack metadata needs its name and description")
ui = yaml.safe_load((skill / "agents/openai.yaml").read_text())
if "$rstack" not in ui["interface"]["default_prompt"]:
    errors.append("default prompt must mention $rstack")

names = set()
for path in (skill / "references/workflows").glob("*.json"):
    group = json.loads(path.read_text())
    if names & group.keys():
        errors.append(f"duplicate workflow in {path.name}")
    names.update(group)
    for name, recipe in group.items():
        for field in ("outcome", "inputs", "steps", "skills", "check", "stop"):
            if not recipe.get(field):
                errors.append(f"{name}: missing {field}")
        for entry in recipe["skills"]:
            if not entry.get("name") or not entry.get("when"):
                errors.append(f"{name}: skill needs its selection condition")

# Preserve upstream files byte-for-byte, including their license and source.
# The size rule still applies to authored files; only hash-verified manifest
# entries may retain an upstream size above the local authoring limit.
manifest = json.loads((ROOT / "docs/tutor-source-manifest.json").read_text())
vendored_hashes = {"skills/" + item["file"]: item["sha256"] for item in manifest["files"]}

files = [p for p in ROOT.rglob("*") if p.is_file() and
         not any(x in p.relative_to(ROOT).parts for x in
                 (".git", ".local", ".venv", "__pycache__"))]
for path in files:
    if path.stat().st_size > 20000:
        expected = vendored_hashes.get(path.relative_to(ROOT).as_posix())
        if expected is None or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"split file by responsibility: {path.relative_to(ROOT)}")
    if path.suffix != ".md":
        continue
    for target in re.findall(r"\]\(([^\n)]+)\)", path.read_text()):
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        target = target.split("#", 1)[0].strip("<>")
        if target and not (path.parent / target).exists():
            errors.append(f"broken local doc link: {path.relative_to(ROOT)} -> {target}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print(f"Package checks passed: {len(names)} workflow contracts; metadata, local links and file sizes.")
