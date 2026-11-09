"""Report stale inventory and inspect literal Markdown reference paths."""
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

from .planning import check_source
from .catalog import resolve


def local_references(entry):
    source = Path(entry["path"])
    if not source.is_file():
        return []
    missing = []
    for raw in re.findall(r"\]\(([^\n)]+)\)", source.read_text()):
        ref = raw.strip().strip("<>")
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", ref) or ref.startswith("#"):
            continue
        ref = unquote(ref.split("#", 1)[0])
        if not ref or any(x in ref for x in ("<", ">", "*", " ")):
            continue
        path = Path(ref).expanduser()
        if not path.is_absolute():
            path = source.parent / path
        if not path.exists():
            missing.append({"reference": raw, "resolved_path": str(path)})
    return missing


def diagnose(catalog, deep=False):
    source_issues, references = [], []
    variants = defaultdict(list)
    counts = defaultdict(int)
    for entry in catalog["entries"]:
        status = check_source(entry)
        if status != "entry-current":
            source_issues.append({"id": entry["id"], "status": status, "path": entry["path"]})
        variants[(entry["kind"], entry["name"])].append(entry)
        counts[entry["kind"]] += 1
        if deep:
            missing = local_references(entry)
            if missing:
                references.append({"id": entry["id"], "missing_literal_references": missing})
    collisions = []
    for (_, name), entries in sorted(variants.items()):
        if len(entries) > 1:
            collisions.append({"name": name, "ids": [e["id"] for e in entries],
                               "entry_content_equal": len({e["entry_sha256"] for e in entries}) == 1})
    errors = [i for i in catalog["issues"] if not i.get("optional")]
    preference_issues = []
    for name in catalog.get("preferences", {}):
        try:
            resolve(catalog, name)
        except ValueError as exc:
            preference_issues.append({"name": name, "issue": str(exc)})
    return {"observed_at": catalog["observed_at"], "entries": len(catalog["entries"]),
            "source_kinds": dict(counts), "source_issues": source_issues,
            "discovery_issues": catalog["issues"], "name_variants": collisions,
            "reference_warnings": references,
            "preference_issues": preference_issues,
            "healthy_inventory": not source_issues and not errors and not preference_issues,
            "limits": ["Only SKILL.md hashes are checked, not supporting assets/scripts.",
                       "Literal link warnings need source inspection; optional/example links may be intentional.",
                       "Provenance and licensing are unreviewed unless separately documented.",
                       "File presence does not prove live tools, account access or workflow quality."]}
