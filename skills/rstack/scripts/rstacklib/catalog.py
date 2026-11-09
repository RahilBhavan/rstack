"""Observe skill packages without importing or executing their contents."""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parents[2]
KINDS = {"local", "system", "synced", "plugin"}
SKIP = {".git", "node_modules", "__pycache__", ".venv", "data", "exports", "build", "dist"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def default_roots(project):
    home = Path.home()
    pairs = [(home / ".agents/skills", "local", "shared"),
             (home / ".codex/skills", "local", "codex"),
             (home / ".claude/skills", "local", "claude"),
             (Path(project) / ".agents/skills", "local", "project"),
             (Path(project) / ".claude/skills", "local", "project-claude"),
             (SKILL_DIR.parent, "local", "rstack")]
    cache = home / ".codex/plugins/cache"
    for provider in ("openai-curated-remote", "openai-primary-runtime", "openai-bundled"):
        pairs.append((cache / provider, "plugin", provider))
    return [{"path": str(p), "kind": k, "label": label} for p, k, label in pairs]


def read_roots(path, project):
    if path is None:
        return default_roots(project)
    raw = json.loads(Path(path).read_text())
    if not isinstance(raw, dict) or not isinstance(raw.get("roots"), list):
        raise ValueError("config must contain a roots array")
    result = []
    for root in raw["roots"]:
        if (not isinstance(root, dict) or not isinstance(root.get("path"), str)
                or root.get("kind", "local") not in KINDS):
            raise ValueError("each root needs a string path and a valid source kind")
        p = Path(root["path"]).expanduser()
        if not p.is_absolute():
            p = Path(path).resolve().parent / p
        label = root.get("label", p.name)
        if not isinstance(label, str):
            raise ValueError("root label must be a string")
        result.append({"path": str(p), "kind": root.get("kind", "local"), "label": label})
    return result


def metadata(path):
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("missing YAML frontmatter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ValueError("frontmatter name must be a nonempty string")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        raise ValueError("frontmatter description must be a nonempty string")
    return data, text


def namespace(path, root, name):
    parts = path.parts
    kind = root["kind"]
    if ".system" in parts:
        return "system/" + name, "system"
    if "synced" in parts:
        return "synced/" + name, "synced"
    if kind == "plugin":
        rel = path.relative_to(Path(root["path"]).resolve())
        plugin = rel.parts[0]
        version = rel.parts[1] if len(rel.parts) > 2 else "unknown"
        return f"plugin/{plugin}/{name}@{version}", kind
    return name, kind


def source_evidence(path, text):
    pointers = []
    for name in ("SOURCE.md", "SOURCES.md", "LICENSE", "LICENSE.md", "LICENSE.txt"):
        p = path.parent / name
        if p.is_file():
            pointers.append({"type": name, "path": str(p), "sha256": digest(p)})
    urls = sorted(set(re.findall(r"https://(?:github\.com|[^\s/)]+)[^\s)>\]`\"']*", text)))
    return {"status": "unreviewed", "pointers": pointers, "urls": urls[:30],
            "note": "Source pointers are evidence to inspect, not authorship or redistribution clearance."}


def scan(roots, pack_for):
    entries, issues, visited = {}, [], set()

    def walk(directory, root, depth=0):
        if depth > 18:
            issues.append({"path": str(directory), "issue": "depth limit reached"})
            return
        try:
            real = directory.resolve(strict=True)
            if not real.is_dir():
                return
            manifest = directory / "SKILL.md"
            if manifest.is_file():
                source = manifest.resolve()
                key = str(source)
                if key in entries:
                    if str(manifest) not in entries[key]["aliases"]:
                        entries[key]["aliases"].append(str(manifest))
                else:
                    try:
                        data, text = metadata(source)
                        base, kind = namespace(source, root, data["name"])
                        entries[key] = {"id": base, "name": data["name"], "path": key,
                                        "description": data["description"].strip(), "kind": kind,
                                        "root_label": root["label"], "entry_sha256": digest(source),
                                        "aliases": [str(manifest)], "pack": pack_for(data["name"], kind),
                                        "provenance": source_evidence(source, text)}
                    except (ValueError, yaml.YAMLError) as exc:
                        issues.append({"path": str(source), "issue": str(exc)})
            if real in visited:
                return
            visited.add(real)
            for child in sorted(directory.iterdir()):
                if child.name not in SKIP and (child.is_dir() or child.is_symlink()):
                    walk(child, root, depth + 1)
        except (OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
            issues.append({"path": str(directory), "issue": str(exc)})

    for root in roots:
        path = Path(root["path"])
        if not path.exists() and not path.is_symlink():
            issues.append({"path": str(path), "issue": "root absent", "optional": True})
        else:
            walk(path, root)
    groups = {}
    for entry in entries.values():
        groups.setdefault(entry["id"], []).append(entry)
    for base, group in groups.items():
        if len(group) > 1:
            for entry in group:
                suffix = hashlib.sha256(entry["path"].encode()).hexdigest()[:10]
                entry["id"] = f"{base}~{suffix}"
    return {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
            "roots": roots, "entries": sorted(entries.values(), key=lambda e: e["id"]),
            "issues": issues}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.new")
    try:
        temp.write_text(json.dumps(data, indent=2) + "\n")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def resolve(catalog, query):
    if ":" in query:
        plugin, name = query.split(":", 1)
        matches = [e for e in catalog["entries"]
                   if e["id"].startswith(f"plugin/{plugin}/")
                   and e["name"].casefold() == name.casefold()]
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise ValueError("ambiguous runtime alias; choose an ID: " +
                             ", ".join(e["id"] for e in matches))
    options = [e for e in catalog["entries"] if e["name"].casefold() == query.casefold()]
    preference = catalog.get("preferences", {}).get(query.casefold())
    if preference:
        preferred = next((e for e in options if e["id"] == preference["id"]), None)
        if (preferred is None or preferred["entry_sha256"] != preference["entry_sha256"]
                or not Path(preferred["path"]).is_file()
                or digest(Path(preferred["path"])) != preference["entry_sha256"]):
            raise ValueError(f"pinned preference for {query} changed or disappeared; inspect and repin explicitly")
        return {**preferred, "selection_reason": preference["reason"]}
    exact = [e for e in catalog["entries"] if e["id"] == query]
    if len(exact) == 1:
        return exact[0]
    if len(options) == 1:
        return options[0]
    if options:
        raise ValueError("ambiguous skill; choose an ID: " + ", ".join(e["id"] for e in options))
    raise ValueError(f"skill not found: {query}")


def find(catalog, query, limit=10):
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for entry in catalog["entries"]:
        title = set(re.findall(r"[a-z0-9]+", entry["name"].lower()))
        body = set(re.findall(r"[a-z0-9]+", entry["description"].lower()))
        score = 4 * len(words & title) + len(words & body)
        if score:
            ranked.append((score, entry))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [{"score": score, **entry} for score, entry in ranked[:limit]]
