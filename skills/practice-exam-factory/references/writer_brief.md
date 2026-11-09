# Writer brief (one writer per unit)

Fill the <...> fields and send this to a fresh general-purpose agent. Run all writers at once.

---
Task: write exam-style questions for <COURSE> <EXAM>, unit <UNIT> only (<UNIT TOPICS>). Do the work yourself. Start no subagents.

All work is in "<WORK>". Read "<WORK>/harness.py" first (a copy of the skill's harness). Its docstring is the contract for the files you write. Family files and the selftest import it as `harness` from WORK.

Sources:
- The slides: "<SLIDES>". Read them fully. They define what the instructor teaches.
- The style and difficulty target: "<STYLE ANCHOR>". Copy its feel: wording, length, the number of steps, how options look (two-part answers, "None of the above", statement options), and how clean the numbers are.
- Optional: <NOTES OR TOPIC LIST>.

Deliverables:
1. fam_<UNIT>.py: FAMILIES, at least <K, usually 15> generator functions. Each one is a distinct exam problem type that yields at least 22 distinct variants (f.n = 22).
   - Cover every computable topic in the slides.
   - Use stories with names and real objects, clean numbers, and 2 or 3 steps.
   - Distractors must come from real student mistakes (wrong sign, a forgotten step, the wrong formula, swapped definitions). Never use random offsets.
   - Raise Reject for ugly draws: messy decimals, degenerate cases where two readings give the same answer, equal parameters that hide a mix-up, distractors within rounding distance of the key.
   - Import helpers with `from harness import Reject, num, money, frac_tex`.
2. selftest_<UNIT>.py: for every family, re-solve the key over at least 30 seeds by an independent method. Use brute force, a numeric search, sympy, or the definition instead of the shortcut formula.
   - Also fail if any distractor is also correct, or within rounding distance of the key.
   - Exit nonzero on any failure.
   - Prove it catches errors: break one formula, see it fail, restore it.
3. concept_<UNIT>.json: at least 45 hand-written MC at exam level. Use "which is true" questions, graphs described in words, direction-of-change questions and 2-step ideas. Spread the answer letters evenly.
   - Format: [{"topic","stem","opts":[<OPTIONS> strings],"ans","explain"}].
4. tf_<UNIT>.json: about <N_TF> true/false items in the style of the anchor's true/false: about 70% concept or trap, 30% short calculation, half true.
   - Format: [{"topic","stem","ans":"T"|"F","explain"}].
   - Avoid repeating stems in <EXISTING FILES, if any>.

Rules:
- Math uses KaTeX \( ... \) only. Dollar signs stay outside math.
- Every explain is a worked solution of 2-5 sentences with the key numbers.
- Every item has exactly one defensible answer under the exam's standing assumptions: <ASSUMPTIONS>. Put any extra assumption in the stem.

Bar:
- `python3 <SKILL>/scripts/harness.py --work <WORK> <UNIT>` prints "PROBLEMS: none" with at least <TARGET> items.
- The selftest passes, run with `uv run --with scipy --with sympy --with numpy python selftest_<UNIT>.py`.
- Read the printed samples and fix anything awkward.

Reply with only: the item count by family, the selftest result, the concept and tf counts, and one sentence on anything you could not do.
---

## Sizing
- MC needed per unit = n_exams x (MC per exam) / units. Aim for at least 1.3x that, because review drops some families. Each family gives 22 variants. Concept items add about 45.
- T/F needed per unit = n_exams x (T/F per exam) / units. Writers can add more T/F in the fix round if the pool is short. build_exams.py reports the shortfall exactly.
