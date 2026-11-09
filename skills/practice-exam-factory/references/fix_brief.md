# Fix-round brief (send to the same writer with SendMessage, because it still has its context)

What changed does not need reporting: `review.py blind --handwritten changed` detects it from fingerprints and graded stems.

---
Round-<R> follow-up for <UNIT>: blind reviewers solved <WHAT>. Their notes are in "<WORK>/review/notes<R>_<UNIT>.txt". Each note names the family, concept item or tf index, and gives the stem and the reviewer's comment.

1. For each note where the reviewer is right, fix the cause.
   - In a family, change the generator: add a Reject, or improve the distractor logic, so no variant has the problem.
   - If you judge the reviewer wrong, leave the item and say why in one line.
2. Rewrite hand-written items marked exam_like=false so they read like the anchor. Delete one only if it cannot be saved. Keep at least <MIN> concept and <MIN> tf items.
3. Do not touch these families, which are being dropped: <DROP LIST>.
4. List every note you rejected, each with a one-line reason. The orchestrator decides those, not you.

Bar:
- harness prints PROBLEMS: none with 22 variants per family.
- The selftest passes.
- Any new check is proven to bite.

Reply with the counts, the number of notes fixed, and the list of rejected notes with their reasons.
---
