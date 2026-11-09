# Attribution and distribution

Rstack's router, workflow compositions, local utilities, tests and documentation
were assembled for Rahil Bhavan. The underlying library contains original work,
adaptations and independently maintained packages. Installation location does not
establish authorship. The catalog records source evidence for later inspection.

## Known source families

- [pstack / Poteto](https://github.com/cursor/plugins/tree/main/pstack): inspiration
  for a central mode and task-specific playbooks; the local collection also includes
  adopted engineering principles and verification-related skills. The pinned pstack source is now included under vendor/poteto, with its MIT notice.
- [tstack / Theo](https://github.com/t3dotgg/tstack): the local adapted PR delivery
  and multi-model review family. Its MIT license and source notices remain with the pinned source under vendor/theo.
- [Matt Pocock's skills](https://github.com/mattpocock/skills): engineering,
  specification, testing and interview workflows in the installed collection.
  The pinned upstream collection is under vendor/mattpocock with its MIT notice; local adaptations remain separate variants.
- Tobia Donadon's Construct material: local adapted product-manager, code-reviewer,
  art-director, motion-director, review-miner and launchr workflows. Adjacent SOURCE.md
  files in the installed packages record their sources; they are not bundled here.
- Rahil's project skills and design systems: outcome, operations, research, content,
  recruiting, host coordination and project-specific workflows. Some combine
  upstream ideas; do not treat this category as an originality certification.
- OpenAI/plugin/harness packages, Notion, Google Drive, Sites, Pages and other
  vendor-managed skills: remain managed in their installed locations. Cached
  packages and account access are distinct. Their code/assets/terms are not
  redistributed by this repository.
- Claude synced collections and Omarchy system skills: referenced in place with
  explicit source kinds. Compatibility with this session is checked per task.

The local catalog stores adjacent SOURCE/SOURCES/LICENSE pointers, their hashes
and source URLs found in manifests. Its provenance status starts **unreviewed**.
These pointers may describe an input/reference rather than the skill's author.
No legal clearance, complete dependency license audit or ownership proof is claimed.

## What a release contains

The initial learning release contained the original rstack composition layer plus
the five leaf packages below. Version0.2.0 additionally includes the explicitly
licensed upstream snapshots described at the end of this file. It does
not copy the rest of the inventoried third-party packages, private source evidence,
accounts or assets.
The manifest inventory, preferences, personal machine paths, test runs and source
repair backup are local state and are ignored by Git.

The MIT license in this repository applies to its original files. It does not
relicense anything referenced by the catalog or located outside this repository.
Any future vendor/leaf bundle needs its own explicit allowlist, source revisions,
license review and privacy review before distribution. Personal account permissions,
client assets and historical action authorizations do not transfer to another user.

## Explicit learning-bundle extension — November 9, 2026

Rahil explicitly requested adding his MacBook exam skills and documenting their installation. The same day he asked to add Jane Street's `socratic-tutor` (MIT) and to combine it with LearnHarness's `learnharness` data-reader skill (AGPL-3.0-only). He then asked for a loop that improves on them; `study-loop` is original rstack work under the root MIT license and leaves the vendored packages unedited. The release allowlist for this extension is only `rstack`, `exam-prep`, `practice-exam-factory`, `socratic-tutor`, `learnharness` and `study-loop`. The four imported leaf bundles are preserved byte-for-byte, with adjacent SOURCE records and per-file hash manifests (`docs/exam-source-manifest.json`, `docs/tutor-source-manifest.json`, the latter with upstream commits). `learnharness` keeps its own AGPL-3.0 LICENSE and is distributed unmodified as a separate work; the root MIT license does not cover it. Inspection covered all selected files for course inputs and embedded account material; no course files, answers, account data, vendor cache or purchased design package was copied. No independent chain-of-title certification is claimed; preserve all original notices and external dependency terms. This explicit owner-requested extension supersedes the earlier router-only release description for these four named packages only. The rest of the installed catalog remains referenced in place.

## Explicit upstream extension v0.2.0 — November 9, 2026

Rahil requested Matt Pocock, Poteto and other collections in the public kit. This
release includes pinned, unmodified upstream snapshots of mattpocock/skills,
cursor/plugins/pstack and t3dotgg/tstack under vendor/. Their MIT notices and
supporting source remain intact; hashes and commits are in
[upstream-sources.json](docs/upstream-sources.json). The root MIT notice does not
replace their copyright notices or LearnHarness's AGPL-3.0-only terms.

The source includes39 Matt skill packages (31 active,8 in-progress reference-only),
58 Poteto skill packages and9 Theo skill packages, alongside the six learning
packages. Default discovery covers104 packages total. These collections supersede
the earlier six-package-only release scope; they do not include vendor caches,
private project skills, paid assets or unreviewed Construct materials. Copies of
upstream setup instructions are not permission to activate their integrations.
