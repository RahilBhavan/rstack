---
name: study-loop
description: Run Rahil's multi-day study loop around socratic-tutor - a spaced review queue, a beginner mode with worked examples, confidence tracking, independent grading for high levels, 7-day pre/post trials and evidence-based proposals to improve the loop. Use when the user wants to study a topic across sessions, review what is due, track mastery over time, measure whether tutoring worked, or says "study loop", "what is due", "continue studying". One-off explanations stay with explainer; exam-format material stays with exam-prep.
---

# Study loop

Teach across days, not just within one sitting. This skill leads; `socratic-tutor`
runs the teaching inside it. `learnharness` supplies read-only history when its data
exists. The queue CLI is `scripts/learnq.py`, relative to this file. Resolve its
absolute path first. It is standard-library Python 3.10+ and prints JSON.

The queue lives at `~/.local/state/rstack/learn-queue.json` (override with `--state`
or `RSTACK_LEARN_STATE`). It is private local state. Never put it in a repository or
in the LearnHarness data folder. Use `--today` only to backfill a real past check
whose date the user states, never to skip a waiting period.

## Precedence over socratic-tutor

The vendored `socratic-tutor` stays unedited. This skill overrides it in exactly two
places. Everywhere else, follow it as written.

1. **Beginner mode.** At level 0-1, teach with a worked example before questioning
   (section 4), instead of explaining only after 2-3 failed attempts.
2. **Grading.** The tutor sets levels 0-3 on its own checks. Levels 4-5, the final
   assessment and trial tests need an independent grader (section 5).

## 1. Start every session with what is due

Run `learnq.py due`. Review those items before any new material, in the listed order:
all confident errors first, then oldest and weakest, with topics mixed. Ask one fresh
question per item from a new angle, never the question from last time. Record each
answer (section 5). If nothing is due, go to new material.

## 2. New topic: trial first

Diagnostic questions teach, so give the pre-test before them. Offer a trial for each
new topic. Skip it only if the user declines.

1. Ask a fresh agent (the platform's checker agent or a fresh subagent) to write two
   parallel forms from the topic and sources: same size, same subskills, different
   questions, each with a key. It returns only the pre-test form and key to you. It
   saves the post-test form to `~/.local/state/rstack/trials/TOPIC-post.md`, creating
   the folder if needed. Never open that file yourself.
2. Give the pre-test unaided. Grade it against the key with `code` or `checker`.
3. Run `learnq.py trial-start TOPIC SCORE OUT_OF --grader checker|code|human`.
4. If an open trial blocks a new one, ask the user, then end it or run
   `learnq.py trial-cancel TOPIC`.

Section 7 finishes the trial.

## 3. New topic: history and diagnostic

1. If LearnHarness data exists, read it with the `learnharness` readers. Look for the
   learner's own answers, confidence and thinking on this topic. Note confident
   errors: wrong answers given with confidence 70 or more. Graph propositions are
   topics met, not mastery. A missing data folder is normal; continue without it.
2. Run the socratic-tutor diagnostic. Ask about known confident errors first.
3. Add the subskills at their diagnosed levels (0-3), one call per level group:
   `learnq.py add TOPIC SUBSKILL... --level N`. The result lists `existing`
   subskills, which keep their recorded level.

## 4. Teach

- **Level 0-1, beginner mode.** Show one worked example and give the reason for each
  step. Then give a completion problem with the last steps blank. Then a full problem.
  Then switch to the socratic-tutor question loop. Beginners learn more from studied
  examples than from unaided problem solving; the benefit reverses as skill grows.
- **Level 2 and up.** Use the socratic-tutor loop as written.
- **Confidence on every check.** Ask for a 0-100 confidence with each answer, as one
  extra number. A confident error gets a question that exposes the contradiction,
  and it returns first next session.
- **Real exercises.** Prefer checks with a verifiable result: code that runs, a
  circuit or calculation with a known value, a proof step with a stated rule.

## 5. Grade and record every check

`learnq.py record TOPIC SUBSKILL --pass|--fail --grader G --confidence C [--level N]`

Record every check, including review questions. `--confidence` is required.

| Grader | Use when | May set |
|---|---|---|
| `tutor` | You judged the answer yourself in this session. | Levels 0-3 |
| `code` | Running code verified the answer (a test, a simulation, SymPy). | Levels 0-5 |
| `checker` | A fresh agent graded it from only the question, the key or rubric, and the learner's verbatim answer. Never send it the conversation. | Levels 0-5 |
| `human` | An instructor, TA or real exam graded it. | Levels 0-5 |

Add `--level N` on a pass when socratic-tutor's level rule is met: two or more checks
passed, at least one of them unprompted recall. The CLI enforces the countable part:
a level rises one step, only on the second pass in a row, and a pass never lowers it.
Without `--level`, a pass reschedules the review and leaves the level unchanged.

A pass extends the next review to 1, 3, 7, 21, then 60 days. A fail drops the level by
one and brings the item back tomorrow. If no checker agent or subagent exists, use
`code` or ask the user for a `human` check. Never relabel a tutor judgment.

## 6. End the session

Run `learnq.py show TOPIC` and show the map. Emit the socratic-tutor save-state block
for the user. Say what is due next and when. Write nothing into LearnHarness data.

## 7. Finish a trial

At least 7 days after `trial-start`, the fresh agent gives the saved post-test unaided
and grades it. Run `learnq.py trial-end TOPIC SCORE OUT_OF --grader checker|code|human`.
The CLI refuses an early post-test and a different number of questions. Report the
normalized gain: the share of pre-test misses the learner now gets right.

## 8. Improve the loop

After each `trial-end`, and whenever the user asks, run `learnq.py report`. Proposals
live in `~/.local/state/rstack/learn-proposals.md`, one entry per signal kind and topic.
For each signal, look for an open entry with the same kind and topic. If one exists,
replace its evidence and date in place. Otherwise add an entry tagged
`[proposal · study-loop · YYYY-MM-DD · not yet ruled]`.

| Signal | Meaning | Proposal to consider |
|---|---|---|
| `overconfident` | Mean confidence exceeds accuracy by over 15 points. | Open sessions with confidence-calibration items. |
| `self-graded` | Two or more passes, none graded independently. | Route the next checks to `checker` or `code`. |
| `lapsing` | A subskill failed twice after passing. | Split it, add a worked example, or teach a prerequisite. |
| `low-gain` | A trial's normalized gain is below 0.3. | Try exam-prep's study guide on the next topic and compare gains. |

Rahil rules on proposals. Do not change this skill, the vendored skills or the CLI
thresholds on your own.

## Boundaries

- No schedules, reminders or background jobs. If the user asks for reminders, hand
  the `due` dates to `plan-personal-week`, which owns calendar changes and approval.
- For graded coursework, teach and guide. Do not produce the graded solution.
- Use authorized course material only.
- The queue records practice evidence. Only a trial or a real exam shows learning.
