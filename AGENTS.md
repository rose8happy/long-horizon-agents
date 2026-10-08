# Repository instructions

This repository is a reusable long-running agent project template. It is separate from any research project used to motivate it.

- Keep the core small: two persistent roles, durable project documents, and ordinary task programs where useful.
- User goals and explicit authorization take precedence over agent-generated plans. Never invent budget, time, approval, or verification gates.
- Preserve existing files during initialization. Make installation additive, local, and inspectable; no automatic model calls, account changes, scheduled tasks, or network requests.
- Keep platform details in `adapters/`. Model names and reasoning effort are configurable choices, not protocol requirements.
- The planner owns direction and the executor owns task execution and resource scheduling. Plan updates take effect at safe boundaries; do not modify a running task's contract.
- Task results and evidence belong in the project workspace. The conversation and scheduler prompt are not the canonical project state.
- Record valuable completed work, informative failures, and stopped directions in `HISTORY.md`; link detailed evidence instead of duplicating logs.
- Add checks only for a concrete failure risk. Test the initializer's preservation behavior and any recovery-sensitive task code; do not add ritual reviews.
- Use readable task names. No project secrets, private hostnames, experiment artifacts, or transcripts in examples.
- Python tooling uses the standard library and supports Python 3.10+. Prefer UTF-8 and LF.
- Commit coherent changes with a short description. A PR is useful for substantial future changes; initial repository creation can commit directly to `main`.

## Ownership while implementing

The primary owns integration, `README.md`, `docs/`, `roles/`, `templates/`, repository metadata and publishing. Delegated work owns only the files explicitly assigned to it. Do not create or update Git commits from a delegated task.
