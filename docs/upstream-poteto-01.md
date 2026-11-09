# poteto skills — part 1

## architect — enabled
[Read source](../vendor/poteto/skills/architect/SKILL.md)

Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape.

## arena — enabled
[Read source](../vendor/poteto/skills/arena/SKILL.md)

Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape.

## automate-me — enabled
[Read source](../vendor/poteto/skills/automate-me/SKILL.md)

Use for "automate me", "create/update/refresh my -mode skill", "turn/capture my preferences or working style into a skill", or wanting agents to follow how the user works. Drafts or revises a personal -mode skill via create-skill + unslop, optionally pulling fresh evidence from recent transcripts.

## benchmark-checklist — enabled
[Read source](../vendor/poteto/skills/benchmark-checklist/SKILL.md)

Vet a perf measurement (limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened) before you report or act on it. Use when you run a benchmark or report a speedup or regression you measured.

## blast-radius — enabled
[Read source](../vendor/poteto/skills/blast-radius/SKILL.md)

Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of writing it up. Use for 'blast radius of X', 'what could this break', or reviewing a small diff you don't trust.

## bro — enabled
[Read source](../vendor/poteto/skills/bro/SKILL.md)

Restate the last message in plain human language, with no jargon.

## correct — enabled
[Read source](../vendor/poteto/skills/correct/SKILL.md)

Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last. Prove each check fails on a real past mistake. Repeat this each time the operator corrects you. Use for /correct.

## create-formal-verification-skill — enabled
[Read source](../vendor/poteto/skills/create-formal-verification-skill/SKILL.md)

Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least, in any language, with whichever verification tool fits. Use for /create-formal-verification-skill, "model-check this race", "prove this invariant", or when concurrency, retries, state machines, parsers, or unsafe code need more than tests.

## create-verification-skill — enabled
[Read source](../vendor/poteto/skills/create-verification-skill/SKILL.md)

Generate a project-local verification skill that drives your app the way a user does — any language, framework, or platform. Use for /create-verification-skill, "make a control skill for this repo", or when a project has no scripted way to prove UI/CLI/service behavior.

## figure-it-out — enabled
[Read source](../vendor/poteto/skills/figure-it-out/SKILL.md)

Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after stepping away. Scales rigor to the task, runs a hypothesis loop, and logs decisions. Use for /figure-it-out or 'figure it out'.

## how — enabled
[Read source](../vendor/poteto/skills/how/SKILL.md)

Use for "how does X work", code walkthroughs before changing something, and placement / ownership / layering questions ("where should this live", "which package owns this", "is this the right layer"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation.

## in-your-own-words — enabled
[Read source](../vendor/poteto/skills/in-your-own-words/SKILL.md)

Restate in your own words what you think the user's goals are and what problem they're trying to solve. Use for /in-your-own-words.

## interrogate — enabled
[Read source](../vendor/poteto/skills/interrogate/SKILL.md)

Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", "find blind spots", or "tear this apart". Adversaries try to break a change or design, and only findings proven by a run survive.

## ketchup — enabled
[Read source](../vendor/poteto/skills/ketchup/SKILL.md)

Catch the user up on what changed in this chat since their last message, in plain words and small visuals. List every item waiting on them with what they need to decide it from the reply alone. Use for /ketchup.

## ketchup-video — enabled
[Read source](../vendor/poteto/skills/ketchup-video/SKILL.md)

Catch the user up like /ketchup, with a short subtitled video of slides for what happened and the waiting calls as text under it. Use for /ketchup-video.
