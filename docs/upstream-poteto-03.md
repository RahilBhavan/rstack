# poteto skills — part 3

## principle-guard-the-context-window — enabled
[Read source](../vendor/poteto/skills/principle-guard-the-context-window/SKILL.md)

Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents; keep summaries in the main thread, not raw payloads.

## principle-laziness-protocol — enabled
[Read source](../vendor/poteto/skills/principle-laziness-protocol/SKILL.md)

Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem.

## principle-make-operations-idempotent — enabled
[Read source](../vendor/poteto/skills/principle-make-operations-idempotent/SKILL.md)

Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless of partial prior runs.

## principle-migrate-callers-then-delete-legacy-apis — enabled
[Read source](../vendor/poteto/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)

Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers.

## principle-minimize-reader-load — enabled
[Read source](../vendor/poteto/skills/principle-minimize-reader-load/SKILL.md)

Apply when reviewing or shaping code that's hard to trace. Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope.

## principle-model-the-domain — enabled
[Read source](../vendor/poteto/skills/principle-model-the-domain/SKILL.md)

Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files.

## principle-never-block-on-the-human — enabled
[Read source](../vendor/poteto/skills/principle-never-block-on-the-human/SKILL.md)

Apply when tempted to ask 'should I do X?' on reversible work.

## principle-outcome-oriented-execution — enabled
[Read source](../vendor/poteto/skills/principle-outcome-oriented-execution/SKILL.md)

Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code.

## principle-prove-it-works — enabled
[Read source](../vendor/poteto/skills/principle-prove-it-works/SKILL.md)

Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'

## principle-redesign-from-first-principles — enabled
[Read source](../vendor/poteto/skills/principle-redesign-from-first-principles/SKILL.md)

Apply when integrating a new requirement into an existing design.

## principle-separate-before-serializing-shared-state — enabled
[Read source](../vendor/poteto/skills/principle-separate-before-serializing-shared-state/SKILL.md)

Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant.

## principle-sequence-verifiable-units — enabled
[Read source](../vendor/poteto/skills/principle-sequence-verifiable-units/SKILL.md)

Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer.

## principle-subtract-before-you-add — enabled
[Read source](../vendor/poteto/skills/principle-subtract-before-you-add/SKILL.md)

Apply when sequencing an addition, refactor, or rewrite. Remove dead code, redundant validators, and stub references first, then build on the simpler base.

## principle-test-behavior-not-implementation — enabled
[Read source](../vendor/poteto/skills/principle-test-behavior-not-implementation/SKILL.md)

Apply when you write, change, or keep a test. Assert what the code's users can observe, so that the test fails when that behavior breaks and keeps passing when only the internals change.

## principle-type-system-discipline — enabled
[Read source](../vendor/poteto/skills/principle-type-system-discipline/SKILL.md)

Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, exhaust variants, derive from authoritative schemas.
