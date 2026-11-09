# Lessons from the first full run (ECON 401 Exam 2, 115 exams, 3,105 questions)

## What reviewers found that selftests missed
- Selftests prove a key is right. They do not prove the question is good. Blind review found these problems:
  - loose keys, where the true range was wider than the keyed option;
  - degenerate draws, where both answers were 0;
  - two equal prices, so a mix-up still gave the key;
  - distractors that differed only by rounding;
  - absurd distractors, for example a fee above income;
  - stems that admit two readings, for example a cost "can be dropped in the long run".
- After round 1, add these as Reject rules and as selftest checks. A check that has never failed proves nothing, so break the code once to see it fail.
- A key that is the only whole number among decimals, or the only decimal among whole numbers, gives itself away. harness.py rejects these automatically.

## Exam-likeness
- The first draft of generated questions was one-step and used bare equations. Briefs must point at the real exam as the style anchor and require stories, 2 or 3 steps and mistake-based distractors.
- True/false on the real exam test ideas and traps. Generated "the value is X" true/false questions are not exam-like, so keep true/false hand-written.
- Drop families that reviewers rate exam-like in at most 1 of 3 samples (`drop` in factory.json). The pool should be about 1.3x the need, so dropping is cheap.
- Cap content beyond the slides per exam instead of removing it. The textbook can still appear on the exam.

## Tooling traps
- Compare grades with exact matches. A first-letter compare counted "AMBIGUOUS" as "A" and hid a flag.
- A family file that imports `harness` while harness.py runs as `__main__` gets a second Reject class, so draws escape. harness.py now registers itself as `harness`.
- Resolve paths with `Path(__file__).resolve()`. Relative `__file__` breaks when scripts run from another folder.
- KaTeX: use `\( \)` only, never `$`. Escape a raw `<` inside math, or the browser reads it as a tag. Pages need `<meta charset="utf-8">`, or auto-render fails silently. Printing thousands of formulas needs Chrome's `--virtual-time-budget=150000`.
- Agents occasionally stop one item short of a long file. `review.py compare` lists ungraded items. Send them back.

## Cost
- A full 115-exam run took 6 writers, 3 review rounds (6, 6 and 2 reviewers) and 2 fix rounds, roughly 3-4 hours of agent time. For a quick set (5-10 exams), use one sample round and skip round 3.

## Assembly
- The "one variant per type per exam" rule must key on (unit, family), and it must skip hand-written items. The first run keyed on the family name, and all concept items share the name "concept", so each exam got at most one concept question. build_exams.py also gives the hand-written pool one rotation slot per 22 items, so concept questions appear at their share.
