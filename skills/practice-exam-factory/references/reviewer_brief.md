# Blind reviewer brief

Use a fresh `checker` agent for each unit, or one for 2-3 small units. Never reuse a writer. <BLIND> is the folder review.py prints (outside WORK). Never give a reviewer the WORK path. Fill the fields:

---
You are a blind reviewer for <COURSE> <EXAM> practice questions, unit <UNIT>. You see no answer key. Do the work yourself. Start no subagents.

Files:
- The questions: "<BLIND>/blind<R>_<UNIT>.txt". M items are multiple choice, T items are true/false.
- The content standard: "<SLIDES>".
- The difficulty anchor: "<STYLE ANCHOR>". Solve its questions first so your scale matches the real instructor. If it holds a key, cover the key.
- Open no other files. The questions are all you get.

For every item, with no skipping or sampling:
1. Solve it independently. Use Python for arithmetic. Answer with a letter, T or F, or AMBIGUOUS if two options are defensible or none is.
2. difficulty, from 1 to 5 against the anchor:
   - 1: one-step recall, easier than anything on it.
   - 3: a typical anchor question.
   - 5: harder than anything on it.
3. exam_like: true or false. Ask whether it would look natural on this instructor's exam in wording, length and style.
4. in_slides: true if the slides teach the needed idea, false if it needs content beyond them.
5. note, only if something is wrong. Examples: an unclear stem, a giveaway distractor, two options equal in value, a key that is only loosely right, a clone of another item.

Write "<BLIND>/grades<R>_<UNIT>.json" as [{"q","ans","difficulty","exam_like","in_slides","note"}]. Save after every 25 items.

Reply with only: the count reviewed, the mean difficulty for M and for T, the count with exam_like false, and your three most important notes.
---

## Rounds that worked
- Round 1 (sample): `review.py blind --round 1 --per-family 2 --handwritten sample`. This is a fast look at keys and style, and it finds families to fix or drop.
- Round 2 (full): `--round 2 --per-family 3 --handwritten all`. Every hand-written item gets a non-writer solve. The generated families rely on their selftests plus 3 blind samples each.
- Round 3 (changed): after the fix round, `--round 3 --per-family 2 --handwritten changed`. The script picks the changed families, the ungraded hand-written items and the skipped items itself.

## Adjudicate, do not average
`review.py compare` prints each disagreement with the stem, options and explanation. Solve it yourself. Reviewers are wrong sometimes (in one run they swapped buyer and seller shares). Writers are wrong sometimes. AMBIGUOUS always means the wording needs fixing, even when the key is right.
