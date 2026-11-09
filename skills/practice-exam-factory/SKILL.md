---
name: practice-exam-factory
description: Mass-produce many full practice exams (5 to 150+) for a real course exam, in the exam's exact format, with every answer key verified by code and by blind reviewer agents, no question repeated across exams, difficulty graded against the instructor's own practice exam, and delivered as a timed, self-scoring exam app plus a PDF. Use whenever a student asks for "N practice exams", "100 exams", "a full exam for every day until the test", "make every question exam style", "thousands of verified questions", or wants to grind exam-format multiple-choice and true/false until expert, even if they never say "factory". Handles objective formats (MC, T/F). For notes, study guides, a single practice exam or free-response prep, use exam-prep instead.
---

# Practice-exam factory

Builds N complete practice exams that feel like the real one, where every key is right and no question repeats.
The method was proven on a 115-exam run of 3,105 questions. Read `references/lessons.md` once before starting, because it records what went wrong the first time.

The pipeline has three ideas:
1. **Generators, not lists.** Each calculation problem type is a Python function that draws parameters and computes the key, so one verified type yields 22 variants.
2. **Nobody marks their own homework.** Writers write a selftest that re-solves each key a different way. Separate blind reviewers then solve the questions without the key and grade difficulty, exam-likeness and scope.
3. **Assembly enforces exam realism.** The exam format, unit spread, no repeats, one variant per type per exam, and caps on off-slide and very hard items are all applied in code.

SKILL below means `~/.claude/skills/practice-exam-factory`. All course files go in one work folder, called WORK. Start it with:
```
python3 SKILL/scripts/harness.py --init --work WORK    # copies harness.py into WORK (family files import it) and a factory.json template
```
If the skill's harness.py changes later, run `--init` again, so the WORK copy matches. It never overwrites factory.json.

## 1. Intake

Get these from the user's files. Ask only for what the files cannot answer.
- The course, the exam, and the units in scope (lectures or chapters). Get the slides or notes for each unit.
- **The style anchor:** the instructor's practice exam or a past exam. Without one, questions drift toward textbook style. If none exists, say so, and use the syllabus format plus the closest problem sets.
- **The format:** sections (true/false, MC), the count and points of each, options per MC, the time limit, and the standing assumptions printed on the exam.
- **N, the number of exams.** Before building, estimate the cost:
  - MC needed = N × (MC per exam). T/F needed = N × (T/F per exam).
  - About 15 to 20 generator types per unit give 330 to 440 MC per unit.
  - A full run takes several hours of agent time. For a quick set of 5 to 10 exams, use fewer types and one review round.

Edit `WORK/factory.json`. Put an absolute slides path on each unit, and the anchor path in `style_anchor`. Write each `drop` entry as a `[unit, family]` pair. A bare string fails the config check on purpose.

## 2. Write (one writer agent per unit, in parallel)

Spawn one general-purpose agent per unit with `references/writer_brief.md`, filled in. Each writer delivers four files:
- `fam_<U>.py`, the generators
- `selftest_<U>.py`, the independent re-solve
- `concept_<U>.json`, the hand-written MC
- `tf_<U>.json`, the true/false items

Size the pool at about 1.3× the need, because review drops some types.

When the writers return, rerun every check yourself. A writer's report is a claim, not proof.
```
python3 SKILL/scripts/harness.py --work WORK <U>          # must print PROBLEMS: none
cd WORK && uv run --with scipy --with sympy --with numpy python selftest_<U>.py   # must exit 0
```

## 3. Review round 1: a sample

```
python3 SKILL/scripts/review.py blind --work WORK --round 1 --per-family 2 --handwritten sample
```
The question files go to a blind folder outside WORK (default `/tmp/pef_blind/<course-exam>/`). Reviewers get only that folder, the slides and the anchor, never the WORK path. Spawn fresh `checker` agents with `references/reviewer_brief.md`, one per unit or one per 2 to 3 small units. Then run:
```
python3 SKILL/scripts/review.py compare --work WORK --round 1
```
- **Disagreements:** solve each one yourself and decide who is right. Never count AMBIGUOUS as agreement. It means the wording needs fixing.
- **Flagged types:** if a type is rated exam-like in at most 1 of 3 samples, add it to `drop` in factory.json. If a type is rated harder than the anchor (difficulty 5), simplify it or let the cap limit it.
- **Notes:** `review/notes1_<U>.txt` collects every note for the fix round.
- **Skipped items:** compare lists any item a reviewer skipped. The next `--handwritten changed` round includes it automatically.

## 4. Fix round

Send each writer (SendMessage, because it keeps its context) `references/fix_brief.md`, filled in. When a pattern of problem shows up, have the writer turn it into a Reject rule plus a selftest check. Then rerun the harness and every selftest yourself.

A writer may reject a note, but the writer does not have the final word, because that would be marking its own homework. Read each rejected note with the writer's reason and decide yourself. If the reviewer was right, send it back.

## 5. Review round 2: every hand-written item

```
python3 SKILL/scripts/review.py blind --work WORK --round 2 --per-family 3 --handwritten all
```
Use fresh reviewers, then run `compare`, adjudicate the disagreements, and run a second fix round. Round 3 checks only what changed. The script finds this itself: families whose variants changed since the last fingerprint, hand-written items no round has graded, and skipped items. Writers do not get to pick what is re-reviewed.
```
python3 SKILL/scripts/review.py blind --work WORK --round 3 --per-family 2 --handwritten changed
```
Stop when compare shows no disagreement left and no AMBIGUOUS item.

## 6. Assemble and render

```
python3 SKILL/scripts/build_exams.py --work WORK --pdf
```
- **What it enforces:** the format from factory.json, an even spread over units (the remainder rotates), no repeats, one variant per type per exam, the `drop` list, and removal of hand-written items graded not exam-like.
- **Caps per exam:** `caps.beyond_mc` and `caps.beyond_tf` limit items beyond the slides, and `caps.hard_mc` limits items of difficulty 4.5 or more.
- **Grades:** difficulty and scope come from the latest blind grades.
- **Short pools:** if a pool is too small, the script states the exact shortfall and how many exams the pool supports. Then write more items or lower N. Never allow repeats silently.
- **Output:** `WORK/out/exams.html` is the exam app: timer, scoring, worked solutions, a missed-question review, a record by unit, and save and load of a progress file. `WORK/out/exams.pdf` holds each exam with its key after it.

The `--pdf` step exits nonzero if no PDF was written or any formula failed to render. Then run:
```
cd SKILL/scripts && uv run --with pymupdf python verify_outputs.py --work WORK
```
- **What it checks:** one key line per question in the PDF, one key section per exam, and no raw math source. It also answers exam 1 headless with one deliberate miss, then checks the score, the mistakes view and the rendering.
- **Bar:** report done only after it prints ALL OUTPUT CHECKS PASSED.

Copy the two outputs next to the user's other study files with clear names.

## 7. Report

Report to the user:
- the counts;
- each check run, with its result;
- each review round's agreement, for example "915 of 917, and both misses were reviewer errors I verified";
- what was dropped or capped, and why;
- the difficulty range against the anchor.

State the limits plainly:
- Reviewers are AI agents, not the instructor.
- Content beyond the slides is tagged, not removed.
- Scores live in one browser unless the user saves a progress file.

## Scope notes
- Free-response, proofs and essays do not fit this pipeline. Use exam-prep.
- MC with other option counts works: set `options`. Sections can be MC only or T/F only.
- If the user already has verified items, put them in `WORK/import_<name>.json` (fields unit, kind, topic, stem, opts, ans, explain). They join the pool without review, so say so in the report.
