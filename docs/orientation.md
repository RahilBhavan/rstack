# Start with orientation

After installing rstack, say:

> Use rstack to orient me.

You can also say “onboard me” or “help me get started with rstack.” If you already
know your goal, include it: “Orient me—I want to learn SQL and I’m using Claude.”

Your agent gives a short introduction, asks only the missing questions, checks
which tools your first task needs and helps you get a small useful result. You can
choose building/fixing, learning, research, or a quick tour. You do not need to know
skill names, connect accounts or share personal information. Orientation is optional;
say “skip the tour” to move directly to your task, or ask to resume later.

Examples:

- “I’m new to coding. Help me understand the project I uploaded.”
- “I want to learn SQL, but I don’t have any study-tracking tools.”
- “I use a coding agent. Show me how to start a test-driven bug fix.”
- “Give me a quick tour before I pick a task.”

Preferences stay in the conversation. Ask for a copyable handoff note if you want to
carry your goal and next prompt into another session. A note is saved to disk only
when you request it. Rstack does not add telemetry, a profile database, automatic
reminders or account integrations during orientation.

If a required tool is missing, the agent explains the gap and offers a useful next
step supported by that session. It will not claim that all integrations are connected
or simulate an independent reviewer. It distinguishes setup readiness from a first
task actually completed and checked.

## Filesystem clients

```sh
python3 rstack.py orientation
# Aliases: orient, onboard
```

This prints the guide for your agent; it does not run a model or start an interactive
terminal wizard. It works before catalog inventory and makes no changes. In a chat
client, simply use the natural-language prompt above; Python is not required to
read the orientation instructions.

The maintained guide is
[orientation.md](../skills/rstack/references/orientation.md). Both public ZIP formats
bundle the same guide. Installation output points new users to the starting prompt.
The public collection remains one router plus 103 leaf workflows; orientation is
part of the router, not an extra native skill competing for discovery.
