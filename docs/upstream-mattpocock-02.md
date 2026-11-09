# mattpocock skills — part 2

## to-spec — enabled
[Read source](../vendor/mattpocock/skills/engineering/to-spec/SKILL.md)

Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed.

## to-tickets — enabled
[Read source](../vendor/mattpocock/skills/engineering/to-tickets/SKILL.md)

Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).

## triage — enabled
[Read source](../vendor/mattpocock/skills/engineering/triage/SKILL.md)

Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs.

## wayfinder — enabled
[Read source](../vendor/mattpocock/skills/engineering/wayfinder/SKILL.md)

Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.

## wizard — enabled
[Read source](../vendor/mattpocock/skills/engineering/wizard/SKILL.md)

Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.

## chief-of-staff — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/chief-of-staff/SKILL.md)

Pursue a long-running goal in a single session by co-ordinating subagents.

## claude-handoff — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/claude-handoff/SKILL.md)

Hand the current conversation off to a fresh background agent that picks up the work immediately.

## loop-me — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/loop-me/SKILL.md)

Grill me about specs for the workflows I want to build, within this workspace.

## setup-ts-deep-modules — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/setup-ts-deep-modules/SKILL.md)

Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only through its entry-point files. User-invoked.

## software-factory — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/software-factory/SKILL.md)

Upstream experimental draft with malformed YAML; reference-only.

## writing-beats — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/writing-beats/SKILL.md)

Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it.

## writing-fragments — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/writing-fragments/SKILL.md)

Writing, explore: mine raw fragments, no structure yet.

## writing-shape — reference-only
[Read source](../vendor/mattpocock/skills/in-progress/writing-shape/SKILL.md)

Writing, exploit: shape raw material into an article, paragraph by paragraph.

## git-guardrails-claude-code — enabled
[Read source](../vendor/mattpocock/skills/misc/git-guardrails-claude-code/SKILL.md)

Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.

## migrate-to-shoehorn — enabled
[Read source](../vendor/mattpocock/skills/misc/migrate-to-shoehorn/SKILL.md)

Migrate test files from as type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace as in tests, or needs partial test data.
