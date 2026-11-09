---
name: exam-prep
description: Turn course or self-study materials (lecture slides, notes, syllabus sessions, textbook chapters, review sheets, past or practice exams, marking schemes) into study material that raises exam scores - question-first study guides and detailed notes, practice exams that mirror the real exam's format, answer keys in marking-scheme wording, answers to chapter or textbook exercises, and checks of the user's answers. Use whenever a student uploads lecture or exam files, or asks for notes, a study guide, cheat sheet, practice questions, practice exam, predicted questions, or exam/quiz prep for a course (Econ, Stats, EECS, Math, Psych, etc.). This skill owns HTML study material, including interactive study pages, diagrams, and graphs requested "using artifacts" or "design skills", so prefer it over frontend-design and docs for coursework. Not for newsletter digests or prompt rewriting.
---

# Exam prep

Builds study material for a specific exam from the user's own course files. The goal is
points on the exam, so every output is shaped by the real exam's format and by what
learning research says actually works.

## 1. Intake (once per exam, before building)

Read every uploaded file first. Then establish these facts, from the files where possible:

- Course, exam name, date, and which lectures/chapters are in scope
- Exam format: question types allowed (MC, matching, fill-in, T/F, free response),
  calculator or not, time, points. A past exam or the professor's announcement is the
  authority; the review sheet is the topic list.
- Marking-scheme wording, if a key or rubric was uploaded
- What the user wants now: study guide, practice exam, answer check, or predicted questions

Exam format matters most for practice exams and predicted questions. If it's missing
there, ask in one short batch (at most 3 questions). For notes and study guides, or when
the files already answer it, state your assumptions in one line and proceed. Building a
large deliverable on a wrong format assumption is the most expensive mistake here; a
333-page question bank was once built before learning the exam was T/F + MC only.

Large build = more than 3 lectures in one guide, or more than one practice exam. For those,
show a 5-10 line plan (sections, question counts, format) and wait for "go". If the user
says "plan first", always plan. Otherwise just build.

## 2. Pick the mode

| User asks for | Build | Read first |
|---|---|---|
| notes, study guide, cheat sheet, "understand the concepts" | Retrieval-first study guide | `references/learning-science.md` |
| practice exam, more questions, "like the past exam" | Practice exam + separate key | `references/practice-exam.md` |
| "check my answers", "verify this key" | Answer check | section 4 below |
| "what will be on the exam" | Predicted-topics list with evidence | section 5 below |

All modes use `references/output-format.md` for the file itself.

## 3. Non-negotiables for every mode

- **Match the real exam.** If the exam is MC/matching/fill-in only, generate zero free
  response, including disguised "explain why" items. If no calculator, no arithmetic-heavy items.
- **Use the course's own language.** Notation, variable names, and phrasing follow the
  slides and marking scheme (e.g. "true but unknown" if that's the scheme's phrase), because
  graders award points for the expected wording.
- **Questions before explanations.** Even in a study guide, each section opens with
  2-4 questions to attempt before the explanation. See learning-science.md for why.
- **Mark the traps.** For each topic, name the common wrong answer and why it's tempting.
- **Correctness over volume.** Fewer verified questions beat many unchecked ones. Re-derive
  every answer key entry before shipping.

## 4. Answer check

Work each problem independently first, then compare with the user's or the key's answer.
For each disagreement, show the step where they diverge and cite the slide or rule. If
subagents are available and there are more than ~30 items, split the key across 2-3 agents
that each verify independently, then reconcile disagreements yourself. An independent
audit like this has caught several wrong keys before.

## 5. Predicted questions

Rank topics by evidence: emphasis in the review sheet, time spent in lectures, what past
exams tested, and anything the professor said. Show the evidence for each prediction so
the user can judge it, then give 1-2 sample questions per topic in the exam's format.

## 6. Academic integrity

If the user shares a live graded quiz, exam, or take-home that's due, say once, briefly,
that you can't answer graded work directly, then offer the useful alternative right away:
explain the concept and build similar practice problems with full solutions. Don't lecture,
and don't refuse study help on ungraded or past material.
