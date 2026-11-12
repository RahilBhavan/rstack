# Welcome to rstack

Use this workflow when someone says “orient me”, “onboard me”, “getting started”,
or asks what to do after installing rstack. It is a conversation led by the agent,
not a survey or a script that provisions tools. Returning users can skip, resume,
or change direction. Ordinary tasks do not require orientation first.

## Start with the person

Explain in two sentences: “Rstack helps me choose a useful workflow for your task.
You describe what you want, and I read only the relevant instructions.” Avoid a
catalog dump or assuming the person shares the maintainer's projects/preferences.

Use information already in the conversation. Ask only what is missing, at most
two short questions together:

- “What would you like help with first: building or fixing something, learning a
  topic, researching a question, or exploring the library?” Allow their own answer.
- If their environment matters and is unknown: “Where are you using rstack—ChatGPT,
  Claude, a coding agent, or somewhere else?” Do not ask them to identify a model,
  buy tools or provide credentials. Experience level is optional; infer only from
  what they say and adjust when they correct you.

If they already supplied a goal, skip the menu and move straight to that goal.
If they want a tour without a task, show three short example requests, tailored to
any interests they supplied. Offer one small demonstration, not every workflow.
If they skip orientation, immediately return to their task.

## Check what this session can do

Read the available tool descriptions or perform a relevant read-only check. Do not
claim host/account capabilities based on a skill file, client name or user guess.
Check only capabilities needed for their first task, not every integration:

- Reading instructions requires access to the bundled files. Without it, explain
  how to select/enable the installed skill or provide its entrypoint; do not report
  that a plain chat attachment is a persistent installation.
- Work on a codebase needs readable project files; implementation also needs a
  writable workspace and appropriate test tools. Read project rules first.
- Fresh research needs browsing or supplied sources. Without browsing, use the
  provided material and label the freshness limit.
- Scripts need a supported execution tool and their own dependencies. Independent
  review needs a real separate reviewer; do not role-play a missing reviewer.
- Learning can start conversationally without LearnHarness history or a study
  queue. Use the single-session tutor when persistent storage is unavailable.

Explain only consequential gaps in plain language, then propose a useful next step
that the current session supports. Do not install plugins, connect accounts, scan
personal files broadly or grant permissions as part of orientation.

## Deliver a small first result

Agree on a concrete first task from their goal, normally feasible in a few minutes.
Use the library index/search and read the selected workflow. Public packages have
`references/index.md` and `scripts/find.py`; filesystem installations can use the
bundled CLI's `find` and `show`. Use exact IDs for overlapping names.

Examples of first steps, adapted to the person's actual request:

- Build/fix: inspect the supplied issue and relevant code, identify an observable
  behavior check, then follow the selected workflow's implementation boundaries.
- Learn: choose one concept, ask a short diagnostic, teach from the actual answer
  and check it with a fresh question. With no history or storage, use
  `socratic-tutor` if present; do not create a multi-day queue just for onboarding.
- Research: answer one bounded question from available sources, with attribution
  and stated unknowns. Check the index for the matching research workflow; if none
  fits, use the agent's normal supported research tools without inventing a skill.
- Explore: show three suitable workflows from the actual index with example
  requests and relevant tool requirements. A short guided tour is a valid result.

Do the chosen authorized work. Preserve its approval gates and repair limits.
Do not introduce sample repos, recurring reminders, paid calls, sends, publications
or merges merely to demonstrate installation. Never substitute an invented user's
answer for a diagnostic or claim a learning gain from an agent-written example.

## Make the next use easy

End with the result, the check actually performed and one reusable prompt tailored
to their goal: “Use rstack to <their next task>.” They need not memorize skill names.
Distinguish “ready to start” from a first task that was actually completed; tool
checks and answered setup questions alone are not proof of a useful first result.

Keep preferences in this conversation by default. If the user explicitly wants a
portable handoff, produce a short copyable note with their stated goal, chosen
workflow, observed capabilities, unresolved gaps and next prompt. Save it to a file
only if requested, outside the installed library and private data repositories.
Do not store secrets, personal paths, telemetry or an onboarding-complete flag.
Reorientation can reuse the note, but must re-check changed capabilities.
