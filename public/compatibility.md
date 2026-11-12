# Runtime compatibility

All indexed instructions and their complete reviewed source resources are bundled.
They do not require the maintainer's source folders. One router is installed;
103 leaf workflows are selected through its index, not 103 native slash commands.

- ChatGPT and Claude: use custom skill ZIP upload where enabled for your account.
  Read the index directly when a shell is unavailable. Code execution is needed
  only for scripts, and may require enabling it in your account.
- Codex, Claude Code and other Agent Skills clients: extract the root `rstack`
  folder into a supported skill directory, or use the standalone installer.
- Other assistants: give the agent the extracted `SKILL.md` and filesystem access.
  Native skill registration depends on that assistant supporting the format.

Each workflow keeps its original tool and platform requirements. GitHub workflows
need Git and repository access; UI checks need a supported browser; council/review
flows can require independent agents and specified model providers; media workflows
need their original rendering dependencies. Poteto includes Cursor-specific skills;
Theo includes T3-specific orchestration. Setup instructions remain source material,
not permission to change accounts, activate automations, install plugins or send.

LearnHarness is optional, separately licensed AGPL-3.0-only, and requires its desktop
app for live history. Its full source and license are included unmodified. Its
reader scripts are not a replacement for that app. Study-loop can work without its
history; advanced independent grading still requires an independent grader.

All original instruction/resource bytes and licenses remain intact. Entry filenames
alone become `instructions.md` so uploads contain exactly one `SKILL.md`. Resolve
references to nested SKILL.md files using that name. Parent source files are under
`references/source/`. For original layouts and development use the matching release
source archive. Eight upstream in-progress drafts and Benny helpers remain source
references, excluded from routing. No binary assets are silently dropped.

This public release excludes private project packages, provider caches and skills
whose redistribution rights have not been established. Filesystem rstack can
continue discovering those packages in place on their owner's computer. Public
packaging has been tested locally; account-level upload acceptance and actual leaf
workflow execution are separate checks, not implied by archive validation.
