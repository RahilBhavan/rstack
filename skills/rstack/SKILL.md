---
name: rstack
description: Compose Rahil's installed skills into a task-specific workflow with source discovery, project-aware routing and observable checks. Use for rstack, requests to work with Rahil's stack, or coordinating work across his skill collection. Also use for new-user orientation. Simple questions and edits stay lightweight.
---

# rstack

For “orient me”, “onboard me” or a first-use tour, follow
[orientation](references/orientation.md). It adapts to the person’s goal and available
tools. Skip orientation for ordinary tasks unless requested.

Turn the request into a checked result using the relevant parts of the installed
library. All skills remain available. Load instructions as their steps become
relevant, rather than reading the entire collection into context.

The bundled CLI is `scripts/rstack.py`, relative to this file. Resolve its actual
absolute path before running it. Python 3.10+ and PyYAML 6 are required. `workflows`
lists the available plans without an inventory. `--help` describes the interface.
It never executes a leaf workflow or calls a model.

## Start from the actual request

1. Read the current project's instructions, relevant spec and design owner. Preserve
   explicit decisions, task ownership, existing permissions and remaining limits.
   Use `outcome-prompt` for substantive work. A direct answer or minor edit needs
   only appropriate evidence and a check.
2. Discover the relevant skills. Run the bundled CLI's `list` or `find "task words"`.
   If no catalog exists, run `inventory --project` with the actual project path.
   For another registered source root, use an explicit roots config as described in
   [catalog operation](references/catalog-operation.md). New files require a refresh.
3. Choose a workflow from `workflows`, then run `plan WORKFLOW`. These plans are
   guidance. Read only selected leaf `SKILL.md` files and their required references.
   The complete routing and overlap rules are in [routing](references/routing.md).
   An explicitly named skill takes priority over a generic recipe. For a task
   outside the recipes, search the catalog and use the exact relevant skill.

## Resolve before executing

- `find` ranks lexical candidates. It is not a semantic classifier, quality score
  or permission decision. Use the original request to select from candidates.
- `show NAME` returns the canonical source path. Multiple local variants require
  an explicit ID or a recorded, hash-pinned local preference. Inspect their sources
  and current project authority before choosing; do not merge instructions or
  select by newest mtime. Managed entries
  have namespaces such as `plugin/...`, `system/...` and `synced/...`.
  Bundled upstream IDs include `vendor/mattpocock/...`, `vendor/poteto/...`
  and `vendor/theo/...`; use those exact IDs when a bare name is ambiguous.
  Session plugin names such as `google-drive:google-sheets` resolve when unique.
- Plans expose missing or ambiguous skills and changed entry hashes. Refresh and
  inspect a changed source before relying on it. Missing required gates or an
  explicitly requested skill remain a gap. Continue independent useful work.
- Synced skills may reference Claude-only `/mnt` paths, browser tools or runtimes.
  Plugin caches may contain inactive or template packages. Check the actual live
  tools/platform before invoking them. Prefer the available purpose-built plugin;
  never claim a connector works because its instructions exist.
- Keep one lead workflow. Compose companions for a specific need. A whole-codebase
  audit, a diff review and a council are different scopes. Read the selected leaf
  rather than automatically running all three.

## Execute with evidence

State the intended outcome and consequential assumptions briefly, then perform the
authorized task. Keep source claims, decisions, generated artifacts and observations
distinct. Verify the exact result through the user's actual interface or intended
artifact, including retry/duplicates/restart where persistence is affected.

Use the target project's verification skill before generating a new one. For public
Rahil visuals, load current `rahil-design`, the required figure/design skills and
its exact-artifact review gate. Private Orbit and client identities retain ownership.

Delegate only when the user, selected skill or project instructions call for it.
Use current runtime orchestration rules, an available named model and the minimum
context. Existing provider requests, execution ownership and repair allowances
persist across nested workflows. A missing provider stays missing; do not substitute
unasked or turn one repair allowance into nested retry loops. Do not add daemons,
schedules, new infrastructure or model sweeps just to keep working.

Rstack does not grant sending, calendar writes, application submissions, publishing,
spending or merging authority. Reuse authorization already provided in the session;
do not ask again when it covers the exact action. An approval gate needs a concrete,
reviewable result first. Follow the selected workflow's specific external-action rules.

## Finish at the requested endpoint

Return the actual result, exact files/links when relevant, checks performed, unresolved
gates and what remains unknown. A completed agent run, passing compile or favorable
review score does not establish behavior, learning, hiring or audience outcomes.

For long tasks, use the owning checkpoint/task state; do not create a parallel control
system. For a demonstrated recurring failure, use `improve-skill` and correct the
earliest weak step. Record observed corrections instead of accumulating generic rules.

See [quality and evaluation](references/quality.md) for checks of rstack itself.

The pinned upstream libraries are readable through this checkout's vendor roots.
Read their full source and compatibility notes only when relevant. Do not activate
plugins, hooks, account connections, merges, sends or recurring automation merely
because an upstream skill describes them. Current project/runtime authority wins.
