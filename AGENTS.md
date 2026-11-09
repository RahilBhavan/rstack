# rstack

Rahil's local skill composition and discovery kit. Read `docs/specs/rstack-v1.md`
before changing behavior. The canonical entry point is `skills/rstack/SKILL.md`.

- Preserve leaf skills, attribution, project instructions and existing permissions.
- Catalog every discovered skill. Load only the task's relevant skills.
- A cached manifest proves files exist, not that a connector or workflow works.
- Keep machine paths, source inventories and review runs in ignored `.local/`.
- Do not copy vendor caches or third-party skills into a release without license review.
- Test with `python3 -m unittest discover -s tests -v`.
- Run `python3 rstack.py doctor` after refreshing the local inventory.
- No network, model calls, external writes or recurring jobs from the CLI.
- Workspaces and builds belong on disk. Preserve unrelated work.
- For CI, follow `~/.agents/ci-runner-policy.md` when present.

This repository contains instructions and local utilities. It is not a sandbox,
model runner, scheduler or replacement for T3 orchestration.
