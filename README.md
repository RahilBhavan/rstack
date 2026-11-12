# rstack

Rahil's skills, composed into work you can verify.

Give `$rstack` the task. It finds the relevant skills, reads the project's rules,
chooses a workflow and checks the actual result. The collection includes Rahil's
own workflows, adapted upstream skills and vendor-managed packages. Their original
instructions and ownership remain in place.

```text
Use $rstack to fix this import bug and exercise duplicate/retry behavior.

Use $rstack to turn this idea into a buildable specification.

Use $rstack to explain this finding with a sourced visual.

Use $rstack to work out why this skill keeps failing.
```

## Download and install v0.3.0

**[Download the public skill ZIP](https://github.com/RahilBhavan/rstack/releases/download/v0.3.0/rstack-public.zip)**
— one self-contained router for 103 reviewed leaf workflows, with all source
resources and license notices. [Installation guide](docs/public-install.md) covers
Claude skill upload, ChatGPT skill/plugin availability, Codex, Claude Code and other
filesystem agents. A standalone installer and plugin ZIP are included in the release.
No checkout or pip packages are needed to install. Platform-specific workflows still
require their own tools/accounts; public directory listing and account-level upload
acceptance are separate from downloadable package verification.

## Included upstream collections

This release contains the actual source files, references and license notices:

| Collection | Source packages | Default discovery |
| --- | --- | --- |
| Matt Pocock |39|31 active;8 in-progress reference-only|
| Poteto / Lauren Tan pstack |58|58|
| Theo Browne tstack |9|9|
| Rstack and the existing learning kit |6|6|

Total:112 source skill packages,104 in default discovery. The eight Matt Pocock
in-progress packages remain available as source but are excluded from normal
routing. The pinned software-factory draft has malformed upstream YAML; it is
preserved and documented rather than silently rewritten or reported as working.

The six learning entry points are linked into client skill roots. The additional
collections live in vendor/ and are discovered by rstack; copying them does not
register every native slash command, activate hooks or install a Cursor plugin.
Use author-qualified IDs to avoid collisions, for example:

```sh
.venv/bin/python rstack.py show vendor/mattpocock/tdd
.venv/bin/python rstack.py show vendor/poteto/tdd
.venv/bin/python rstack.py show vendor/theo/council
```

Read [the complete catalog](docs/upstream-catalog.md) and
[compatibility notes](docs/upstream-compatibility.md). Upstream source commits and
per-file integrity manifests are in docs/upstream-sources.json. No runtime,
permission, model subscription or account connection is granted by these files.

## What is here

- One entry point with 26 task-specific workflow plans.
- Discovery across shared, Codex, Claude, nested synced, project and plugin roots.
- A searchable catalog with canonical paths, manifest hashes and source pointers.
- Explicit variants and hash-pinned preferences when skill names overlap.
- Source-drift diagnostics and optional checks of literal Markdown references.
- Previewable installation/removal that preserves existing skills.
- Isolated behavior tests, clean-copy checks and a forward-test record.

The initial local inventory contains 172 packages in 16 packs. That is a dated file
inventory, including vendor templates and runtime-specific skills. It does not mean
172 workflows have been exercised or every corresponding tool is connected.
See the [catalog snapshot](docs/catalog.md) and [verification](docs/verification.md).

## Have your AI install it from GitHub

Public repository: **https://github.com/RahilBhavan/rstack**. No GitHub account is
needed to clone this public source. Paste this into your T3/Codex/Claude Code agent:

```text
Read https://github.com/RahilBhavan/rstack at release v0.2.0, including README.md,
INSTALL_WITH_AI.md, ATTRIBUTION.md and docs/learning-bundle.md. Install the six
allowlisted learning packages on my Mac from a reviewed checkout at
~/Projects/rstack. Preserve existing files, skill folders, remotes and local edits.
Preview installation first; never overwrite a conflict. Use Python3.10+ and a
local virtual environment. Verify all12 links across ~/.agents/skills and
~/.claude/skills, repeat the preview, run inventory and doctor in isolated local
state, and show the exact installed commit and first skill invocation.
Keep Full access selected. Do not request account tokens, install unrelated
packages or run the exam factory merely to verify installation. Public cloning
needs no GitHub sign-in. Report blocked steps separately and explain when a fresh
provider session is needed for skill discovery. Also resolve vendor/mattpocock/tdd,
vendor/poteto/principle-prove-it-works and vendor/theo/full-stop from the bundled
upstream sources. Do not activate upstream plugins or hooks just to install.
```

See [INSTALL_WITH_AI.md](INSTALL_WITH_AI.md) for exact commands, update/removal
rules and what counts as a verified installation. An AI needs tools and network
access; merely reading this page does not install anything.

## Install

Use Python 3.10+ with [PyYAML 6](requirements.txt) installed in the environment that
runs the CLI. Use an existing environment or a virtual environment if needed.
From this checkout:

```bash
python3 rstack.py install --target ~/.agents/skills
python3 rstack.py install --target ~/.agents/skills --apply
python3 rstack.py inventory --project /path/to/your/project
python3 rstack.py doctor
```

The first install command previews changes. Add other `--target` roots for an
existing client setup, such as `~/.codex/skills` or `~/.claude/skills`. Installation
links the **directory**, including its references and CLI. Keep the checkout in
place. A fresh session may be needed for skill menu discovery. The filesystem/CLI
installation is tested locally; no claim of testing every client version is made.

Invoke `$rstack` or ask the agent to use rstack. If a client does not discover it,
give the agent the actual path to [SKILL.md](skills/rstack/SKILL.md). It can read and
use the same entry point directly.

Rstack uses the skills already present on the host and the pinned upstream collections above. Its six directly linked entry packages include
the explicitly requested exam-prep and practice-exam-factory learning packages from
Rahil's MacBook, plus the upstream socratic-tutor and learnharness skills and the study-loop that joins them. It does not bundle the rest of the installed collection or connect
accounts. See docs/learning-bundle.md for the six-package previewable installer;
install other original packages under their own terms and inventory that machine.

## Browse and plan

```bash
python3 rstack.py workflows
python3 rstack.py find 'interview preparation'
python3 rstack.py list --pack research-figures
python3 rstack.py show outcome-prompt
python3 rstack.py plan build
python3 rstack.py doctor --deep --json
```

`find` is a lexical candidate search. The agent uses the actual request to select
skills. `plan` returns conditional guidance, paths, checks and boundaries. Neither
command executes a workflow. A skill outside the named plans remains searchable
and usable; new skills are discovered on the next manual inventory refresh.

For collisions, inspect both variants and use an exact ID. Optionally pin the
choice with a reason:

```bash
python3 rstack.py prefer tdd EXACT-ID --reason 'Inspected and appropriate for this setup'
```

Add `--apply` to save. Changed/missing sources invalidate the preference instead of
silently advancing it. See [catalog operation](skills/rstack/references/catalog-operation.md)
for fixed multi-project roots, isolated state and removal.

## How the pieces fit

The [entry point](skills/rstack/SKILL.md) owns selection and composition.
[Workflow definitions](skills/rstack/references/workflows/) describe concrete inputs,
conditional skills, verification and stopping conditions.
[Routing rules](skills/rstack/references/routing.md) resolve overlapping design,
review, delivery, specification and authoring skills.

Each task keeps its project's identity and permissions. Rahil's public visuals
use Rahil Design. Orbit and client work keep their own systems. Drafting does not
publish, a generic build does not authorize merging, and account access does not
authorize an outbound action. Existing exact authorization remains valid.

Instructions guide the agent; they do not enforce a sandbox. The CLI makes no model
calls, sends no telemetry, starts no server and installs no recurring automation.
T3 remains the execution owner for its delegated work.

## Maintain

```bash
python3 -m unittest discover -s tests -v
python3 rstack.py inventory --project /path/to/project
python3 rstack.py doctor --deep --json
```

Keep machine inventories and preferences out of Git. Read the
[specification](docs/specs/rstack-v1.md) before changing behavior. For a routing
failure, preserve the original request, selected sources and actual output, then
correct the earliest responsible step. The [evaluation guidance](skills/rstack/references/quality.md)
describes how to compare useful outcomes without inventing a benchmark rank.

## Attribution and scope

Inspired by [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack)
and [Theo's tstack](https://github.com/t3dotgg/tstack). Rstack composes the local
library rather than claiming authorship of everything installed. See
[ATTRIBUTION.md](ATTRIBUTION.md) for source and redistribution boundaries.

Skill packaging and directory-link guidance were checked against the official
[Build skills](https://learn.chatgpt.com/docs/build-skills) and
[Skills in plugins](https://developers.openai.com/plugins/concepts/skills) documentation.
Local utility checks establish the behavior described in the verification record;
real task quality and usefulness need continued observation.

## Learning bundle

The MECG guide includes a downloadable archive of this checkout with the router,
two exam skills, two tutoring skills and the study loop. Follow [the installation and skill guide](docs/learning-bundle.md).
Public upstream: https://github.com/RahilBhavan/rstack. The v0.2.0 release is the versioned source for AI-assisted installation. The existing rstack.py install command still links
only the router. install_learning.py explicitly manages the six allowlisted
packages, previews by default and refuses foreign paths.
