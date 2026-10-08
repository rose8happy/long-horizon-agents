# Adopt a project

Use the canonical workspace selected by the user and project instructions. Do not initialize a Windows entry directory when the project lives on a remote host. Resolve this skill's physical directory for its bundled scripts; run them where the canonical project can actually be accessed.

## Existing project records

Inspect the existing goal, plan, current-state, decisions, and history entry points before writing new ones. Reuse these records. Do not create a second ledger merely to satisfy template filenames.

If the project uses different paths, write a short `.agent/PROJECT.md` map in the canonical workspace. For example:

```markdown
# Long Horizon Agents project map

- Canonical workspace: the user-selected project repository
- Mission and authorization: AGENTS.md, docs/PROJECT_GOAL.md
- Plan: docs/plan/CURRENT.md (planning sections)
- Live state and next action: TRACKING.md (current sections)
- Decisions: docs/decisions/
- Valuable history: docs/history.md
- Planner instructions: existing project planner instructions
- Executor instructions and resource owner: existing project controller instructions
```

Use actual paths and sections. Where one existing file carries several roles, agree on distinct sections and avoid simultaneous edits. An absent historical index can be added when there is valuable work to record; it is not a prerequisite for the next task.

Add a small marked entry to `AGENTS.md` that tells future agents to use `$long-horizon-agents` for this project's long-running work and read `.agent/PROJECT.md`. Preserve all existing instructions and marked blocks. With an older harness block, merge only the missing loader line; do not replace the user's role or workspace rules. An established authorization remains valid after adoption.

## New project records

Run the bundled preserving initializer:

```sh
python <skill-directory>/scripts/init_project.py --target <canonical-project> --name "Project name"
```

Use shell quoting appropriate for the actual paths. The initializer creates the project documents, local role instructions and an `AGENTS.md` loader. It makes no model calls and does not create schedules. Existing files are preserved.

Fill the necessary mission and initial plan from the user's request and available evidence. Record authorization exactly as given; a template placeholder is not permission. Do not send the user off to manually fill documents when their request already supplies the information.

## Begin work

With two existing role chats, each uses this skill with its assigned role and the same mapped records. If only one is assigned, use the temporary combined mode described in `SKILL.md`; do not create or message another chat merely because the harness has two roles. When the user explicitly requests two persistent chats, use the host's task tools if available, otherwise provide precise starting prompts and identify the missing capability.

Record who owns direction and who owns each launch resource. Start the first authorized useful task immediately. Configure a scheduled continuation when requested or already authorized; use the host adapter and reuse the role's existing wake. Installation alone is not a request to enable background work in every project.
