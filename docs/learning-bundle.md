# Install rstack with Rahil's learning skills

This extension bundles exactly six packages: the rstack router, exam-prep, practice-exam-factory, socratic-tutor, learnharness and study-loop. The rest of Rahil's installed library remains separately maintained. The public source is https://github.com/RahilBhavan/rstack at v0.1.0. Ask your AI to read INSTALL_WITH_AI.md and install from GitHub. The older MECG ZIP is a separate, frozen three-package fallback.

## Mac installation

1. Install/authenticate one provider in T3 as the textbook explains. Select Full access.
2. Clone https://github.com/RahilBhavan/rstack at tag v0.1.0 into `~/Projects/rstack`, following INSTALL_WITH_AI.md. Keep the checkout in place: installation links to it.
3. Use a supported Python 3.10+ installation. In Terminal, run separately:

```sh
cd "$HOME/Projects/rstack"
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

4. Preview installation in Codex's shared discovery root and Claude Code's personal root. These are host-local skills, not cloud account uploads.

```sh
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills"
```

5. If the preview lists only the intended create/unchanged actions, apply it:

```sh
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills" --apply
```

The helper preflights every target. A foreign directory or link is refused without overwriting it. Repeating the same installation is harmless. Keep existing skill variants and inspect them rather than deleting to fix a conflict. The router-only `rstack.py install` command still manages only rstack.

6. Refresh the inventory. Use your actual project, or inventory the learning bundle for a first check:

```sh
.venv/bin/python rstack.py inventory --project "$HOME/Projects/rstack"
.venv/bin/python rstack.py find 'exam practice'
.venv/bin/python rstack.py show exam-prep
.venv/bin/python rstack.py show practice-exam-factory
.venv/bin/python rstack.py doctor
```

Doctor describes the recorded inventory and can flag drift/collisions; it does not authenticate a provider or run an exam build. Start a fresh provider/T3 session if the skill menu does not refresh. Codex supports `$rstack`; Claude Code exposes `/rstack` and `/exam-prep`. In either client, explicitly asking to read the installed SKILL.md path is a fallback.

## What the six packages do

### rstack

Selects relevant installed skills and composes task-specific workflows. Its CLI inventories, searches, resolves paths, returns plans and reports drift. It makes no model calls and does not execute the leaf workflow. Example: `Use rstack to prepare a source-grounded study workflow from these materials. Show which installed skill fits.` Missing leaves remain missing; install original packages separately under their terms.

### exam-prep

Turns supplied course material into question-first study guides, detailed notes, cheat sheets when appropriate, one format-matched practice exam with a key, answer checks, or evidence-labeled predicted topics. It reads the real exam's format, scope, calculator rules and marking language. Default output is an HTML study page with answers hidden; named PDF/Word/Markdown formats override that default. It asks for a short plan/go-ahead for large builds. Example: `Use exam-prep with these notes and past practice exam. Make a guide for these two lectures, in MC and T/F format, with hidden answers and common traps. Use MECG colours.`

- `references/learning-science.md`: retrieval-first topic structure, worked examples, mixed and spaced review.
- `references/practice-exam.md`: matching the real exam blueprint, plausible distractors and re-solving keys.
- `references/output-format.md`: HTML layout, hidden answers, print behavior, KaTeX and graph checks.

Learning-science and score-improvement statements in the imported skill are source claims; this import is not a new learning-effectiveness trial. Follow the course's actual rules and use authorized study materials.

### practice-exam-factory

Builds batches of objective-format exams, chiefly MC and true/false. It uses parameterized question families, independent re-solves, blind AI reviewers, ambiguity adjudication, repeat-aware assembly and difficulty/scope caps against the instructor's practice exam. It aims to deliver a timed/scoring HTML app plus a PDF with keys. It is not the default for notes, one exam, essays or proofs. Start with a small agreed batch and inspect costs/coverage before expanding.

- `scripts/harness.py`: initializes WORK, loads config and validates question-family draws/pools.
- `scripts/review.py`: creates blind review packets, compares grades/keys and tracks changed/unreviewed items.
- `scripts/build_exams.py`: assembles exams, applies format/repeat/cap constraints and renders app/PDF.
- `scripts/verify_outputs.py`: inspects PDF keys/math and drives a browser scoring/mistake test.
- `references/writer_brief.md`: source/format/generator requirements for writers.
- `references/reviewer_brief.md`: blind solving, ambiguity and difficulty/scope judgments.
- `references/fix_brief.md`: how writers repair adjudicated findings.
- `references/lessons.md`: historical failure cases and adjustments; not independently reproduced here.
- `assets/factory.example.json`: starting configuration; `assets/exams_app.html`: exam-app template.

Dependencies differ from installation: scripts begin with Python; generated selftests may need uv/scipy/sympy/numpy, PDF checks need PyMuPDF, and rendering needs Chrome/Chromium and access to the KaTeX CDN. Configure an absolute on-disk `blind_dir` outside WORK. Provider orchestration must use the current host's supported tools and limits. An installed file is not evidence the full pipeline has run.

### socratic-tutor

Jane Street's tutoring skill (MIT, [janestreet/agent_skills](https://github.com/janestreet/agent_skills)). It starts only when you ask to be taught, quizzed or drilled. It runs a 3-5 question diagnostic, keeps a 0-5 skill map per subskill and asks one question at a time. Levels rise only after two independent checks, one of them unprompted recall. `save state` prints a block you can paste into a new session. Example: `Use rstack to tutor me on Thevenin equivalents until I hit 4/5 on every subskill.`

### learnharness

The data-reader skill from [LearnHarness](https://github.com/amosblomqvist/learnharness) (AGPL-3.0-only, see its SOURCE.md). It reads the desktop app's local sessions and knowledge graph with standard-library Python and never writes to them. It needs the LearnHarness app's data folder; without it the readers stop with "Data folder not found" and create nothing.

- `scripts/sessions.py list|read`: past teaching and practice sessions, with the learner's answers, confidence and thinking.
- `scripts/graph.py propositions|find|chains`: propositions and reasoning chains, with links back to source sessions.

### How the tutor and LearnHarness combine

Rstack's `learn` workflow joins them (`rstack.py plan learn`). If LearnHarness data exists, the agent reads your past answers and thinking on the topic first. That history picks which diagnostic questions come first and which familiar ideas the tutor builds on. It never sets a skill-map level: the tutor still earns each level from fresh checks in the current session. This matters because the graph records ideas you met, not ideas you mastered. The save-state block goes to you, never into the LearnHarness data folder. When a check must match a real exam format, exam-prep takes over.

### study-loop

Rahil's own multi-day loop around socratic-tutor (MIT, part of rstack). It closes seven gaps in tutoring alone. `scripts/learnq.py` enforces the parts marked (CLI); the rest are instructions in SKILL.md.

- **Spacing (CLI).** A private review queue at `~/.local/state/rstack/learn-queue.json`. Each pass pushes the next review out to 1, 3, 7, 21, then 60 days. A fail drops the level by one and brings the item back tomorrow.
- **Beginner mode.** At level 0-1 the tutor shows a worked example, then a completion problem, before questioning.
- **Interleaving (CLI).** `due` mixes topics, so reviews alternate between subjects.
- **Independent grading (CLI).** Levels 4-5 and trial scores need a `code`, `checker` or `human` grader. `add` caps diagnosed levels at 3. A level rises one step at a time, only on the second pass in a row.
- **Confidence (CLI).** Every check needs a 0-100 confidence. `due` lists all confident errors first.
- **Memory across sessions (CLI).** The queue file keeps levels, due dates and every check, so a new session starts from `due`.
- **Measurement and self-improvement (CLI).** `trial-start` and `trial-end` record a same-size pre-test and post-test at least 7 days apart and report the normalized gain. A fresh agent writes and holds the post-test. `report` flags overconfidence, self-grading, lapsing subskills and low gains. The agent turns each flag into a tagged proposal for you to rule on, and changes nothing on its own.

The CLI checks what it records. It cannot check whether a question was really unprompted recall, or whether a `checker` label is honest. Those rest on the agent following SKILL.md.

Example: `Use rstack to start a study loop on Thevenin equivalents, with a trial.` Next day: `Use rstack: what is due?`

## Validate a first exam task

Supply ungraded/authorized course notes, a style anchor, exact scope/format, desired count and output. Verify all needed files are accessible. Ask the agent for its plan, selected skill and checks before a large run. Try a single guide/verified exam with exam-prep before commissioning a factory batch. Check answers against independent solutions and course evidence. Keep the learner's attempt separate from AI help.

## Updates and removal

Get a deliberate new release, compare its source manifest and preserve your existing copy before switching. Do not move a linked directory without updating its links. Preview removal and then add --apply to remove only links owned by this bundle:

```sh
.venv/bin/python install_learning.py --target "$HOME/.agents/skills" --target "$HOME/.claude/skills" --remove
```

Removal leaves source packages, course work and unrelated skills intact. No automatic updates, provider subscriptions or accounts are included.
