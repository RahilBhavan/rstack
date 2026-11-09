# poteto skills — part 2

## maintain-formal-verification-skill — enabled
[Read source](../vendor/poteto/skills/maintain-formal-verification-skill/SKILL.md)

Bring a project's formal verification back in line with the code after the code changes: find the commits that touched verified code, update the model, harness, or properties to describe the code as it is now, rerun, and say whether each failure is drift in the verification or a bug in the code. Use for /maintain-formal-verification-skill, "is the model still true to the code", or after merges and refactors that touc…

## maintain-verification-skill — enabled
[Read source](../vendor/poteto/skills/maintain-verification-skill/SKILL.md)

Periodic pass that keeps a project's verification skill and feature map honest: parallel source readers per feature, one live session driving every feature, at most one PR of proven corrections. Use for /maintain-verification-skill or "audit the verify skill".

## make-bot-ui — enabled
[Read source](../vendor/poteto/skills/make-bot-ui/SKILL.md)

Use when building a custom UI (page, dashboard, buttons) that should wake a Grok Bot over a webhook, when the user must provide a webhook sender key, or when exposing that UI on Tailscale.

## no-comments — enabled
[Read source](../vendor/poteto/skills/no-comments/SKILL.md)

Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints.

## poteto-help — enabled
[Read source](../vendor/poteto/skills/poteto-help/SKILL.md)

Guides users through pstack setup, /poteto-mode, and picking the skill, playbook, or principle for a task. Type /poteto-help with a question.

## poteto-mode — enabled
[Read source](../vendor/poteto/skills/poteto-mode/SKILL.md)

poteto's agent style for concise, detailed responses, deliberate subagents, unslopped prose, simple code, and verified work. Use for poteto, /poteto-mode, or requests to work in this style.

## principle-attack-the-premise — enabled
[Read source](../vendor/poteto/skills/principle-attack-the-premise/SKILL.md)

Apply when two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before you write another fix that assumes it.

## principle-boundary-discipline — enabled
[Read source](../vendor/poteto/skills/principle-boundary-discipline/SKILL.md)

Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions.

## principle-build-the-lever — enabled
[Read source](../vendor/poteto/skills/principle-build-the-lever/SKILL.md)

Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun.

## principle-encode-lessons-in-structure — enabled
[Read source](../vendor/poteto/skills/principle-encode-lessons-in-structure/SKILL.md)

Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.

## principle-exhaust-the-design-space — enabled
[Read source](../vendor/poteto/skills/principle-exhaust-the-design-space/SKILL.md)

Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. Build 2-3 competing prototypes and compare side by side before committing.

## principle-experience-first — enabled
[Read source](../vendor/poteto/skills/principle-experience-first/SKILL.md)

Apply when product, UX, or feature-scope tradeoffs come up. Choose user delight over implementation convenience; ship fewer polished features over more rough ones.

## principle-explain-the-number — enabled
[Read source](../vendor/poteto/skills/principle-explain-the-number/SKILL.md)

Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result. Find what limits it, and rule out that it measured something other than the work you think.

## principle-fix-root-causes — enabled
[Read source](../vendor/poteto/skills/principle-fix-root-causes/SKILL.md)

Apply when debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate.

## principle-foundational-thinking — enabled
[Read source](../vendor/poteto/skills/principle-foundational-thinking/SKILL.md)

Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious.
