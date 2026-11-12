# Install rstack v0.3.0

[Download the public skill ZIP](https://github.com/RahilBhavan/rstack/releases/download/v0.3.0/rstack-public.zip)
from the [versioned release](https://github.com/RahilBhavan/rstack/releases/tag/v0.3.0).
It contains one router and 103 leaf workflows: the reviewed learning kit plus
Matt Pocock, Poteto and Theo. All supporting resources and original license notices
are included. No checkout, API key, paid model subscription or maintainer account
is needed to download or install the library.

## Claude

1. Enable code execution/file creation if your account requires it.
2. Open **Customize → Skills → + → Create skill → Upload a skill**.
3. Upload `rstack-public.zip` and enable rstack.
4. Start a new chat and say: **Use rstack to help me with <your task>.**

These steps follow [Claude's custom skills guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
Organization policies may control who can upload skills.

## ChatGPT

Use the Skills creation/import flow where available in your ChatGPT desktop app
to import `rstack-public.zip`. Then select rstack with `@` or ask to use rstack.
Standalone skill availability varies by surface. Follow
[OpenAI's skills guide](https://learn.chatgpt.com/docs/build-skills).

For plugin-capable clients, the release also provides `rstack-plugin.zip`, containing
root `plugin.json`, a Claude Code compatibility manifest and `skills/rstack/`.
Extract it and load it through your client's supported local plugin installation
flow. This follows the [portable Agent Plugins layout](https://developers.openai.com/plugins/build/plugins).
It is a downloadable plugin package, **not a published listing in the ChatGPT plugin
directory**. Public directory publication requires the platform's separate submission
and review process. Do not attach a ZIP as ordinary chat context and assume it is
persistently installed. Account-level acceptance has not been tested by this release.

## Codex / Claude Code / filesystem agents

Download `rstack-public.zip` and `install_public.py` from the release into the same
folder. Python 3.10+ is sufficient; the installer uses no pip packages or network.

```sh
# Preview, then install. Choose the client you use.
python3 install_public.py rstack-public.zip --client shared
python3 install_public.py rstack-public.zip --client shared --apply
# Claude Code: replace shared with claude.
# Existing Codex-specific roots: --client codex.
# Custom agents: --target /path/to/their/skills.
```

`shared` uses `~/.agents/skills`, the documented Codex user skill root. `claude`
uses `~/.claude/skills`; `codex` uses `~/.codex/skills`. The installer validates all
archive paths and file hashes before writing, preserves foreign/edited installations
and reports an identical retry as already installed. It installs only `rstack/`.
If Python is unavailable, extract that folder manually into the client's skill root.
Start a fresh session if the client caches discovery. Other assistants can read the
extracted `SKILL.md` directly; native discovery requires Agent Skills support.

Try: **Use rstack to help me practice SQL across several days.**
Or: **Use rstack to plan a test-driven change to this Python CLI.**
Only relevant instructions are loaded. The index remains readable without Python;
the optional `scripts/find.py` search uses the standard library.

## Updates, removal and requirements

Download a new release and inspect its changes. An existing identical installation
needs no change. For an update, preserve edits and move the old `rstack/` folder
outside the scanned skills root before installing. Do not keep two copies with the
same skill name active. To remove, delete only the installed rstack folder after
checking for user edits. No hooks, daemons, credentials or account connections are
installed; original local skills remain untouched.

Installation does not provision external tools. A selected leaf may need GitHub,
a browser, a rendering tool, independent agents, a named model provider, Cursor,
T3 or the separate LearnHarness app. The router checks these before proceeding and
reports unavailable gates. It does not simulate unavailable independent reviewers.
See `references/compatibility.md` in the ZIP for details. Eight experimental upstream
drafts remain supporting source and are excluded from the 103-workflow index.

The root MIT notice covers rstack's original work. Vendored collections retain
separate MIT notices; LearnHarness retains AGPL-3.0-only and full source. Download
`rstack-source.zip` for the complete matching development source in original layout.
The public package excludes private project skills, provider caches and unreviewed
third-party packages; your original filesystem router can discover those locally.

## Verify / build from source

Compare downloaded files against `SHA256SUMS` from the same versioned release.
Internal hashes detect corruption; obtain the archive and checksums from the trusted
release, since a hash manifest alone does not authenticate an untrusted publisher.

```sh
python3 -m venv .venv
# Activate the venv using your platform's normal command, then:
python3 -m pip install -r requirements.txt
python3 build_public.py dist/rstack-public.zip
python3 build_plugin.py dist/rstack-plugin.zip
python3 -m unittest discover -s tests -v
```

Builders read only the reviewed repository trees, never installed host skill caches.
They verify pinned sources and fail if the reviewed leaf count changes. The output
has deterministic timestamps, order and file modes. Existing output files are never
overwritten; choose a fresh filename when rebuilding.
