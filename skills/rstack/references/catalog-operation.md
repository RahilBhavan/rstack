# Catalog operation

Run commands with the actual absolute path to this skill's `scripts/rstack.py`.
The repository root also provides `python3 rstack.py` as a convenience entry point.
The commands below assume the repository root.

```bash
python3 rstack.py inventory --project /path/to/project
python3 rstack.py find 'source grounded presentation'
python3 rstack.py list --pack engineering
python3 rstack.py show outcome-prompt
python3 rstack.py plan build
python3 rstack.py doctor --deep --json
```

Inventory reads shared/Codex/Claude skill roots, their nested collections, the
current project's skill roots, rstack itself and known plugin cache providers.
It follows directory links, detects cycles and deduplicates canonical manifests.
It does not read credentials, runtime databases, conversations or account contents.
It reads manifest content and hashes adjacent SOURCE/LICENSE files when present.
Recursive scanning skips data/build/cache dependency directories named in catalog.py.
Unsupported roots are added explicitly rather than claiming an entire disk census.

Local state defaults to `~/.local/state/rstack/`. Use `--state-dir PATH` before the
subcommand, or `RSTACK_STATE_DIR`, to isolate an experiment. No refresh occurs in
the background. Inventory stores exact machine paths and is private local state.

For a fixed collection across several projects, save a `roots.json` inside that
state directory. A supplied config **replaces** defaults, including the --project
choice. Include every wanted root. Relative paths resolve against the config file.

```json
{
  "roots": [
    {"path": "~/.agents/skills", "kind": "local", "label": "shared"},
    {"path": "~/.codex/skills", "kind": "local", "label": "codex"},
    {"path": "~/.claude/skills", "kind": "local", "label": "claude"},
    {"path": "/path/to/project/.agents/skills", "kind": "local", "label": "project"},
    {"path": "/path/to/rstack/skills", "kind": "local", "label": "rstack"}
  ]
}
```

Valid kinds are local, system, synced, plugin and vendored. Pinned upstream libraries
under this checkout's vendor directory are default roots. Their IDs include the
author, such as vendor/mattpocock/tdd or vendor/poteto/tdd. These are files the
router can read; they are not automatically registered native slash commands.
Bare duplicate names still require explicit selection. Include plugin-provider roots
at their existing `provider/plugin/version/...` hierarchy, as defaults do. A root
whose manifest is malformed is reported; optional absent roots are notices.
Inventory exits 1 for nonoptional discovery issues while retaining the observation.
CLI/config errors exit 2. Doctor exits 1 for source drift or discovery errors.
Literal reference warnings are advisory; examples/optional files may be intentional.

Each record stores the source path, description, pack, source kind, aliases,
SKILL.md hash and source-evidence pointers. Attribution is not inferred from where
the file lives. Identical same-name copies remain explicit variants because their
supporting resources may differ. Different roots linking the same canonical manifest
collapse. Variant IDs use a canonical-path suffix and can change after a source move.
Session-style plugin names such as `google-drive:google-sheets` also resolve when
exactly one matching plugin entry exists. Multiple cached versions require an exact
catalog ID; the alias never silently chooses the newest version.

Doctor checks known manifests against recorded hashes. It cannot discover new files
without inventory or validate scripts/assets from an entry hash. Check the sources
again when a workflow needs those resources. Missing relative references can expose
machine/runtime assumptions; inspect before use.

## Explicit variant preferences

After inspecting variants, record a local default with its rationale:

```bash
python3 rstack.py prefer tdd 'EXACT-ID-FROM-LIST' --reason 'Why this variant fits this setup'
```

Add `--apply` to save the preview to private `preferences.json` in the state directory.
The choice pins the exact ID and SKILL.md hash. A changed/missing source refuses the
preference until inspection and explicit repinning. A refresh does not silently
advance it. An exact ID supplied to show bypasses the default for deliberate use
of another variant. Preferences are local policy, not verified licensing or tool access.

## Installation and removal

Install a directory link for the single rstack skill; keep its self-contained CLI
and references beside SKILL.md. The router references leaves in their original
locations. It does not move, overwrite or bulk reinstall the collection.

```bash
python3 rstack.py install --target ~/.agents/skills
python3 rstack.py install --target ~/.agents/skills --apply
python3 rstack.py uninstall --target ~/.agents/skills
python3 rstack.py uninstall --target ~/.agents/skills --apply
```

Additional `--target` flags support the existing Codex/Claude discovery roots.
Commands preview by default. All targets are checked for conflicts before changes;
an existing foreign rstack path is refused. Repeating installation is harmless.
Uninstall only removes directory links pointing to this router. No --force exists.
Keep the checkout at a stable path while links point to it. Existing sessions may
need a fresh skill discovery/session before the new name appears in their menus.

A clone contains the router, plans and utilities. It does not contain Rahil's leaf
collection. On another machine, install the desired original packages separately
under their actual licenses, then inventory that host. Missing dependencies remain
visible in plans. This is a compositional setup, not a self-contained vendor bundle.
