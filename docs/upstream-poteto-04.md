# poteto skills — part 4

## recall — enabled
[Read source](../vendor/poteto/skills/recall/SKILL.md)

Reconstruct your recent working context from your own chat history, live state, and the shared record (user reports, prior fixes, incidents), then hand back a tight current-state brief. Use for 'recall my work on X', 'catch me up', 'what have I been working on', 'where did I leave off', before starting or resuming work.

## reflect — enabled
[Read source](../vendor/poteto/skills/reflect/SKILL.md)

Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.

## setup-pstack — enabled
[Read source](../vendor/poteto/skills/setup-pstack/SKILL.md)

Configure which models pstack uses per role and at what reasoning budget. Detects your available models and writes an always-applied rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.

## sharpen — enabled
[Read source](../vendor/poteto/skills/sharpen/SKILL.md)

Make a task deeper, not bigger, then rewrite the prompt. Use for /sharpen.

## show-me-your-work — enabled
[Read source](../vendor/poteto/skills/show-me-your-work/SKILL.md)

Keep a reviewable decision trail for long-running or unattended work: a TSV log with one row per decision (what, why, evidence, result). Local by default; commit it when a reviewer needs the trail to trust the result. Use for /show-me-your-work, autonomous or multi-phase runs, or work a human reviews after stepping away.

## statechart — enabled
[Read source](../vendor/poteto/skills/statechart/SKILL.md)

Check a TLA+ model of a system that moves between states, such as a product flow, a protocol, or a service, and draw it as a Mermaid statechart. The report gives the shortest path to each state that breaks a rule. Use for /statechart, or to show a bug as a path through states.

## swarm — enabled
[Read source](../vendor/poteto/skills/swarm/SKILL.md)

Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration.

## tdd — enabled
[Read source](../vendor/poteto/skills/tdd/SKILL.md)

Use only when the user explicitly asks for TDD, a failing test, or a regression test, OR when the bug has an obvious cheap local test target. Skip when the test path is unclear, expensive, integration-heavy, or not requested.

## teach — enabled
[Read source](../vendor/poteto/skills/teach/SKILL.md)

Explain a body of work plainly so a person actually understands it. Runs the how and why skills and weaves what they find into one clear explanation. Use for 'teach me this', 'help me really understand X', 'explain this change or subsystem to me'.

## technical-writing — enabled
[Read source](../vendor/poteto/skills/technical-writing/SKILL.md)

Layered technical-writing standard: Diátaxis structure, Google developer style sentences, STE instruction rules, Global English syntax. Use for /technical-writing or when writing or reviewing docs, RFCs, readmes, PR descriptions, or commit messages.

## typescript-best-practices — enabled
[Read source](../vendor/poteto/skills/typescript-best-practices/SKILL.md)

TypeScript best practices. Use when reading or editing any .ts or .tsx file.

## unslop — enabled
[Read source](../vendor/poteto/skills/unslop/SKILL.md)

Cut AI tells from any writing.

## why — enabled
[Read source](../vendor/poteto/skills/why/SKILL.md)

Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Discovers available MCPs and queries each evidence category (source control, issue tracker, long-form docs, real-time chat, infrastructure observability, error tracking, product analytics warehouse) in parallel, then returns a cited read on decisions and tradeoffs. Use how for runtime behavior…
