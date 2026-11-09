# rstack v1

Original request: "Go through and make rstack use all my skills and the skills I have taken as well, make this one of the best setups in the world"

Rahil can give one entry point a task and have it compose the relevant parts of
his entire installed skill library, with sources, task-specific checks and an
honest account of unavailable capabilities.

## Scope

Inventory shared, Codex, Claude, nested synced, project and plugin skill roots.
Retain all variants and detect collisions. Reference existing packages in place.
Create a portable router and CLI that discovers skills on another machine rather
than embedding Rahil's machine paths. Install the router locally without replacing
existing skills. Separate task preparation, execution, review and external actions.

The initial user is Rahil on this Linux processing host. "Best in the world" is a
quality ambition. It does not establish a benchmark rank or authorize unlimited
model spending, publishing, account changes or recurring automation.

## Acceptance

- AC-1: An inventory covers configured roots recursively, including nested skills;
  canonical symlink aliases collapse, while different same-name packages remain visible.
- AC-2: Every valid entry has an exact path, entry hash, description, source kind,
  source evidence and a pack. Invalid manifests and broken links are reported.
- AC-3: Every entry can be found by ID or description. Ambiguous names require an
  explicit variant. Managed cache presence is labeled separately from live tool access.
- AC-4: Workflow plans resolve relevant skills, expose missing/ambiguous dependencies,
  state permission and verification boundaries, and never execute the task themselves.
- AC-5: The router covers engineering, research, design, media, content, career,
  learning, personal operations, documents, connected workspaces and skill maintenance.
  Unclassified skills remain searchable and usable.
- AC-6: Installation is previewable, repeatable and refuses existing foreign paths.
  Removal only unlinks the router owned by this installation. Originals are untouched.
- AC-7: A clean copy works with synthetic skill roots and no personal inventory.
  Drift, missing sources, duplicate variants and malformed configuration are exercised.
- AC-8: A fresh independent agent uses the router on realistic tasks. Its actual
  artifacts, findings and untested capabilities are retained. One review repair allowance.
- AC-9: README, attribution and a verification report distinguish tested local
  utilities, instruction-level routing and untested leaf workflows.

## Shape and seams

A SourceRoot has a path, source kind and label. A SkillEntry has a stable ID derived
from its name/namespace and canonical source identity, metadata and an entry hash.
A Catalog is a dated observation, not a capability claim. A Workflow lists a primary
skill plus conditional companions, required inputs, checks and stopping conditions.

Discovery reads local manifests. Planning is a pure transform over the catalog and
workflow definitions. CLI adapters print results or explicitly refresh local state.
Installation only owns `rstack` directory links. No background processes or telemetry.

## Checks and limits

Use synthetic roots to test filesystem edge cases, a clean-copy installation cycle,
real local discovery, drift diagnostics and actual plan output. Do not execute every
leaf workflow: many require accounts, Mac hardware, specific projects or paid models.
No aggregate agent performance or productivity claim until measured on real tasks.
