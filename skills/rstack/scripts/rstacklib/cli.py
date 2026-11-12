"""CLI boundary: arguments, local observations and explicit link changes."""
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from . import VERSION
from .catalog import SKILL_DIR, find, read_roots, resolve, scan, write_json
from .diagnostics import diagnose
from .installation import change_links
from .planning import definitions, pack_for, plan


def parser():
    p = argparse.ArgumentParser(description="Discover, compose and check your local skill collection.")
    p.add_argument("--version", action="version", version=VERSION)
    p.add_argument("--state-dir", type=Path,
                   default=Path(os.environ.get("RSTACK_STATE_DIR", Path.home() / ".local/state/rstack")))
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("orientation", aliases=["orient", "onboard"],
                   help="Print the new-user orientation workflow for your agent.")
    inv = sub.add_parser("inventory", help="Refresh a local inventory; never execute skill code.")
    inv.add_argument("--config", type=Path, help="JSON roots configuration; replaces default roots.")
    inv.add_argument("--project", type=Path, default=Path.cwd())
    inv.add_argument("--json", action="store_true")
    ls = sub.add_parser("list", help="List all entries or one pack.")
    ls.add_argument("--pack")
    ls.add_argument("--json", action="store_true")
    search = sub.add_parser("find", help="Lexical candidate search, not an execution decision.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="Resolve a name or explicit ID; optionally read its instructions.")
    show.add_argument("skill")
    show.add_argument("--read", action="store_true")
    show.add_argument("--json", action="store_true")
    sub.add_parser("workflows", help="List task-specific workflow plans.")
    pl = sub.add_parser("plan", help="Resolve a named plan; does not execute its workflow.")
    pl.add_argument("workflow")
    pl.add_argument("--json", action="store_true")
    dr = sub.add_parser("doctor", help="Check source drift, collisions and optional literal references.")
    dr.add_argument("--deep", action="store_true")
    dr.add_argument("--json", action="store_true")
    pref = sub.add_parser("prefer", help="Preview a hash-pinned local variant choice; --apply saves it.")
    pref.add_argument("name")
    pref.add_argument("skill_id")
    pref.add_argument("--reason", required=True)
    pref.add_argument("--apply", action="store_true")
    for name in ("install", "uninstall"):
        cmd = sub.add_parser(name, help="Preview router link changes; use --apply to write.")
        cmd.add_argument("--target", type=Path, action="append", required=True,
                         help="A skill root, such as ~/.agents/skills. May repeat.")
        cmd.add_argument("--apply", action="store_true")
    return p


def load_catalog(state):
    path = state / "catalog.json"
    if not path.is_file():
        raise ValueError("no catalog; run inventory first")
    data = json.loads(path.read_text())
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or not isinstance(data.get("entries"), list)):
        raise ValueError("unsupported catalog; refresh with inventory")
    preferences_path = state / "preferences.json"
    if preferences_path.is_file():
        preferences = json.loads(preferences_path.read_text())
        if not isinstance(preferences, dict):
            raise ValueError("preferences must be an object")
        for name, choice in preferences.items():
            if not isinstance(choice, dict) or any(not isinstance(choice.get(k), str)
                                                 for k in ("id", "entry_sha256", "reason")):
                raise ValueError(f"invalid preference: {name}")
        data["preferences"] = preferences
    return data


def emit(data):
    print(json.dumps(data, indent=2))


def print_entries(entries):
    for entry in entries:
        print(f"{entry['id']}  [{entry['pack']}; {entry['kind']}]")
        print(f"  {entry['description']}")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in ("orientation", "orient", "onboard"):
            print((SKILL_DIR / "references/orientation.md").read_text())
            return 0
        if args.command == "workflows":
            for name, definition in sorted(definitions("workflows.json").items()):
                print(f"{name}: {definition['outcome']}")
            return 0
        if args.command in ("install", "uninstall"):
            emit(change_links(args.target, args.apply, args.command == "uninstall"))
            return 0
        if args.command == "inventory":
            config = args.config
            if config is None and (args.state_dir / "roots.json").is_file():
                config = args.state_dir / "roots.json"
            catalog = scan(read_roots(config, args.project), pack_for)
            write_json(args.state_dir / "catalog.json", catalog)
            if args.json:
                emit(catalog)
            else:
                print(f"Observed {len(catalog['entries'])} skill packages; "
                      f"{len(catalog['issues'])} discovery notices.")
                print(f"Catalog: {args.state_dir / 'catalog.json'}")
                for issue in catalog["issues"]:
                    print(f"  {issue['path']}: {issue['issue']}")
            return int(any(not i.get("optional") for i in catalog["issues"]))
        catalog = load_catalog(args.state_dir)
        if args.command == "prefer":
            from .planning import check_source
            entry = next((e for e in catalog["entries"] if e["id"] == args.skill_id), None)
            if entry is None or entry["name"].casefold() != args.name.casefold():
                raise ValueError("choose an exact catalog ID matching the requested name")
            if not args.reason.strip() or check_source(entry) != "entry-current":
                raise ValueError("a preference needs a reason and a current inspected source")
            preferences = catalog.get("preferences", {})
            key = args.name.casefold()
            preferences[key] = {"id": entry["id"], "entry_sha256": entry["entry_sha256"],
                                      "reason": args.reason}
            if args.apply:
                write_json(args.state_dir / "preferences.json", preferences)
            emit({"applied": args.apply, "preference": preferences[key]})
        elif args.command == "list":
            entries = [e for e in catalog["entries"] if not args.pack or e["pack"] == args.pack]
            emit(entries) if args.json else print_entries(entries)
        elif args.command == "find":
            if args.limit < 1:
                raise ValueError("limit must be positive")
            entries = find(catalog, args.query, args.limit)
            emit(entries) if args.json else print_entries(entries)
        elif args.command == "show":
            entry = resolve(catalog, args.skill)
            if args.read:
                print(Path(entry["path"]).read_text())
            elif args.json:
                emit(entry)
            else:
                print_entries([entry])
                print(f"  Read: {entry['path']}\n  SHA-256: {entry['entry_sha256']}")
                if "selection_reason" in entry:
                    print("  Local preference: " + entry["selection_reason"])
                print("  Source evidence and licenses require inspection. Live tools are not checked.")
        elif args.command == "plan":
            result = plan(catalog, args.workflow)
            if args.json:
                emit(result)
            else:
                print(result["outcome"])
                for key in ("inputs", "steps"):
                    print(f"\n{key.capitalize()}:")
                    for line in result[key]:
                        print(f"- {line}")
                print("\nConditional skill selection:")
                for item in result["skills"]:
                    print(f"- {item['name']}: {item['when']}")
                    print("  " + item.get("path", item.get("resolution_error", "")))
                    if "source_status" in item and item["source_status"] != "entry-current":
                        print("  Source is " + item["source_status"] + "; refresh/reconcile before use.")
                for key in ("check", "stop", "boundary", "note"):
                    print(f"\n{key.capitalize()}: {result[key]}")
        elif args.command == "doctor":
            result = diagnose(catalog, args.deep)
            if args.json:
                emit(result)
            else:
                print(f"{result['entries']} packages; source kinds: {result['source_kinds']}")
                print(f"Source drift/missing: {len(result['source_issues'])}; "
                      f"stale preferences: {len(result['preference_issues'])}; "
                      f"name variant groups: {len(result['name_variants'])}; "
                      f"reference warning packages: {len(result['reference_warnings'])}")
                for item in result["source_issues"]:
                    print(f"  {item['id']}: {item['status']}")
                for item in result["name_variants"]:
                    print("  Choose variant: " + ", ".join(item["ids"]))
                for limit in result["limits"]:
                    print("  Limit: " + limit)
            return int(not result["healthy_inventory"])
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, yaml.YAMLError) as exc:
        print(f"rstack: {exc}", file=sys.stderr)
        return 2
