# Orientation verification — v0.4.0

November 11, 2026. This release adds optional orientation inside the existing router,
with a shared guide, CLI aliases and an installer next prompt. The public scope
remains 104 entries. Upstream leaf sources and licenses are unchanged.

73 tests pass through the shared local workload gate. New behavior checks exercise
`orientation`, `orient` and `onboard` from a copied installed skill, without source
checkout access, catalog creation or filesystem side effects. They build and install
the public archive, verify the exact shared guide is present, preserve the 103-leaf
manifest count and check install/reinstall next prompts. Existing checks cover both
ZIP formats, entry links, hashes, conflict protection and deterministic packaging.
Package checks, public skill metadata validation and diff whitespace checks pass.
The CLI version smoke check reports 0.4.0.

Instruction review covers a user who supplies a goal immediately, a tour-only user,
a learner without history/storage, a code task without writable files, missing
browsing and independent-review tools, skipping, resuming and optional handoff
notes. These are source-level scenario reviews, not observed newcomer sessions.
Orientation never claims completion from setup questions alone or fabricates a
learner's answer. Preferences stay conversational unless the person requests a
handoff or file. No profile database, account connections or recurring automation
are introduced.

Actual ChatGPT/Claude account upload and human onboarding outcomes remain
unobserved. New users must install/enable the updated skill or plugin through their
client's supported flow. The CLI prints agent instructions; it is not an interactive
terminal questionnaire or a model runtime.
