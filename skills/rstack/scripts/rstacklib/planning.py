"""Compose guidance; no model calls, subprocess execution or external writes."""
import json
from pathlib import Path

from .catalog import SKILL_DIR, resolve

REFERENCES = SKILL_DIR / "references"


def definitions(name):
    if name == "workflows.json":
        result = {}
        for path in sorted((REFERENCES / "workflows").glob("*.json")):
            group = json.loads(path.read_text())
            if result.keys() & group.keys():
                raise ValueError("duplicate workflow name")
            result.update(group)
        return result
    return json.loads((REFERENCES / name).read_text())


def pack_for(name, kind):
    name = name.lower()
    for pack, names in definitions("packs.json").items():
        if name in names:
            return pack
    if name.startswith("notion-"):
        return "connected-workspaces"
    if name.startswith("artifact-template-"):
        return "templates"
    return "extensions"


def check_source(entry):
    from .catalog import digest
    path = Path(entry["path"])
    if not path.is_file():
        return "missing"
    if digest(path) != entry["entry_sha256"]:
        return "changed"
    return "entry-current"


def plan(catalog, workflow):
    workflows = definitions("workflows.json")
    if workflow not in workflows:
        raise ValueError("unknown workflow; choose: " + ", ".join(sorted(workflows)))
    spec = workflows[workflow]
    selections = []
    for item in spec["skills"]:
        try:
            entry = resolve(catalog, item["name"])
            selections.append({**item, "id": entry["id"], "path": entry["path"],
                               "kind": entry["kind"], "source_status": check_source(entry),
                               "selection_reason": entry.get("selection_reason"),
                               "capability_status": "not exercised by this plan"})
        except ValueError as exc:
            selections.append({**item, "resolution_error": str(exc)})
    return {"workflow": workflow, "outcome": spec["outcome"],
            "inputs": spec["inputs"], "steps": spec["steps"], "skills": selections,
            "check": spec["check"], "stop": spec["stop"],
            "boundary": spec.get("boundary", "Local preparation within current task authorization."),
            "catalog_observed_at": catalog["observed_at"],
            "note": "Guidance only. Read selected leaf instructions and project rules before acting. "
                    "Conditional skills load only when their condition holds. A missing optional skill "
                    "does not block unrelated work. Explicitly requested skills and required gates must resolve."}
