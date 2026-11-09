# Install from GitHub with your AI

Source: https://github.com/RahilBhavan/rstack. Versioned release: v0.2.0.

Ask a tool-enabled coding agent to read this file, README.md, ATTRIBUTION.md,
docs/learning-bundle.md and the installer source before executing. A chat assistant
without file/Terminal tools can explain the procedure but cannot perform it.
Public cloning needs no GitHub login. Keep school materials and credentials out
of the checkout. Skills are instructions, not account access or a sandbox.

## Installation procedure

1. Inspect macOS and the installed client. Reuse working Python3.10+ and Git.
   If missing, guide the user through official Python/Apple installers. Do not
   replace Apple's Python or install a package manager solely for this task.
2. Use `~/Projects/rstack` as a stable source directory. If absent, clone:

```sh
git clone --branch v0.2.0 --depth 1 https://github.com/RahilBhavan/rstack.git "$HOME/Projects/rstack"
```

Create the Projects parent if needed. If the target exists, inspect its origin,
revision and working tree. Reuse only the intended matching checkout; stop on
foreign contents or conflicts. Never delete or overwrite it to finish. If it is a clean matching older release,
fetch the specifically requested new tag, review the differences and switch to
that tag deliberately; preserve local edits and stop on a foreign checkout.

3. Record `git rev-parse HEAD` and inspect the tagged source. A tag is a readable
   release label; retain the full commit for reproducibility. Then in that folder:

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills"
```

4. The preview must contain12 create/unchanged actions: six packages in two roots.
   The allowlist is rstack, exam-prep, practice-exam-factory, socratic-tutor,
   learnharness and study-loop. Apply only after inspecting that exact preview:

```sh
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills" --apply
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills"
```

All12 actions must now be unchanged. A foreign existing path is a blocker; do not
remove it. Installation only links folders. It does not install every optional
leaf dependency, connect an account, execute a workflow or copy private data.

5. Keep inventory outside Git and point it at the actual project being used:

```sh
.venv/bin/python rstack.py --state-dir "$HOME/.local/state/rstack" inventory --project "$HOME/Projects/rstack"
.venv/bin/python rstack.py --state-dir "$HOME/.local/state/rstack" show exam-prep
.venv/bin/python rstack.py --state-dir "$HOME/.local/state/rstack" show practice-exam-factory
.venv/bin/python rstack.py --state-dir "$HOME/.local/state/rstack" show study-loop
.venv/bin/python rstack.py --state-dir "$HOME/.local/state/rstack" doctor
```

Inspect diagnostics rather than assuming every discovered cached plugin is usable.
A fresh client/provider session may be needed. Ask the agent to invoke `$rstack`,
or `/rstack` where that client supports it. If discovery fails, provide the actual
checkout's skills/rstack/SKILL.md path. Do not claim menu discovery merely because
symlinks exist. Keep T3 Full access selected as the course requests.

## Discover the included upstream skills

The installer links six entry packages; the checkout also holds106 upstream
source skill packages. Rstack automatically scans31 active Matt Pocock skills,
58 Poteto skills and9 Theo skills. Including the six entry packages, a clean
release-only inventory has104 entries. A user's machine may have more entries
and deliberate same-name variants. Preserve those and choose a qualified ID.

```sh
.venv/bin/python rstack.py show vendor/mattpocock/tdd
.venv/bin/python rstack.py show vendor/poteto/principle-prove-it-works
.venv/bin/python rstack.py show vendor/theo/full-stop
```

Ask the agent to read the returned SKILL.md and only relevant supporting files.
The eight Matt in-progress drafts remain reference-only; their presence is not a
compatibility claim. No upstream plugin, agent registration, hook, network service
or recurring automation is activated by this installer. Runtime/project rules and
exact-action permissions still govern an invoked skill. See the catalog.

## Verification receipt

Record source URL, requested tag, full commit, Python and client versions,
checkout path,12 link targets, repeat-preview outcome, inventory/doctor findings
and the first actual client invocation. Omit secrets and personal inventory.
Distinguish automated filesystem proof from client/Mac behavior not exercised.

## Update and remove

The tagged shallow checkout is intentionally pinned, normally detached. Do not
blindly run git pull or imply automatic upgrades. Inspect clean status, fetch a
specific later tag, review its differences and license notices, then deliberately
switch to that version. Stop on local edits and preserve them. Reinstall changed
requirements, repeat preview/apply, refresh inventory and open a fresh session.

Preview removal by adding --remove to the installer command; apply removal only
when requested. It unlinks only links owned by that checkout and leaves sources,
private notes and other skills intact. Deleting/moving the checkout breaks links.

## Distribution terms

Preserve LICENSE, ATTRIBUTION.md and each package's SOURCE/LICENSE files.
LearnHarness is unmodified AGPL-3.0-only material; Socratic Tutor retains MIT.
The root MIT license covers original rstack files, not every imported package.
No provider subscription, cloud account, school permission or private data is
included. Do not create or push a reader-owned GitHub repository unless asked.
