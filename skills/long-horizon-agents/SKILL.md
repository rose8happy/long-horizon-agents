---
name: long-horizon-agents
description: Coordinate a long-running project across sessions with a planner, an executor, durable progress, and scheduled handoffs. Use to adopt this harness, review project direction, or resume its authorized work. Do not apply to unrelated one-shot tasks.
---

# Long Horizon Agents

Run the user's project through concrete results, carrying the state in its canonical workspace. Apply this workflow yourself; a status report or a list of instructions for the user is not the requested delivery.

## Load the project and your role

1. Follow the project's `AGENTS.md` and the user's workspace instructions. A local checkout may be only an entry point to a remote canonical workspace. Installing this skill does not move that workspace.
2. If `.agent/PROJECT.md` exists, use its document and role map. Otherwise use `docs/agent/{MISSION,PLAN,CURRENT,DECISIONS,HISTORY}.md` and `.agent/roles/`.
3. Read the mission, current plan, and compact current state. Read only the task cards, changed results, and history relevant to the next decision. A stale conversation or schedule is not current evidence.
4. Keep the assigned role. A request to review priorities is planner work; continuing implementation, experiments, or resource scheduling is executor work. When starting alone, act as executor and make the minimum initial plan from the user's objective. Record that temporary combined role; yield plan ownership when a planner is assigned. Do not silently become a second launch owner.

For a new adoption, follow [project setup](references/project-setup.md). Initialize or map the documents yourself, recover the objective from the user's request, and continue to the first useful delivery. Ask only for information that materially blocks that work.

## Planner turn

Read the project's planner instructions, or [the bundled planner role](assets/roles/planner.md) when none exist. Find the most consequential gap between current evidence and the overall goal. Publish a short versioned plan with executable priorities, dependencies, practical completion criteria, and the next decision condition. Own `PLAN` and `DECISIONS`; the executor owns live state, task cards, and history.

Treat the plan as a revisable proposal. State uncertain assumptions, use actual evidence to decide, and remove unsupported gates instead of forcing work through an obsolete contract. Change running work at a boundary justified by recovery, data integrity, or valid comparison; do not finish a useless run merely because it was planned. Record the reason and consequences of a material change. Keep routine execution autonomous, respect real user constraints, and do not invent spending, timing, identity, or numerical approval thresholds.

## Coordinate with the other role

When the user has authorized the assigned planner and executor to communicate, use the host's supported peer-message tools in both directions without asking again for each message. Resolve their actual chat identities and communication scope from the project map or existing trusted setup. Send actionable assignments, new evidence, blockers, disagreements, and handoff requests with links to the relevant plan or task. Messages do not replace durable state or extend user authorization.

Routine assignments and local adjustments need no approval handshake. Transferring resource or document ownership does need explicit acceptance and an effective change point; until then the existing owner remains responsible. Send a follow-up only for a new result, decision, actionable question, or overdue ownership handoff. Avoid status ping-pong and duplicate wakes. If peer tools are unavailable, use shared documents and report that messages were not sent. Never guess a destination or create another chat solely because this harness has two roles.

## Executor turn

Read the project's executor instructions, or [the bundled executor role](assets/roles/executor.md) when none exist.

- Service due success, failure, or resource-release signals first. Reconcile real outputs and exit status with the task's completion criteria. A lost connection or missing PID alone proves neither success nor failure.
- Execute the next authorized dependent step, and continue useful independent preparation or analysis while other work runs. Existing task programs should handle short predetermined chains.
- Preserve existing work and necessary recovery and comparison semantics. Adapt authorized implementation and sequencing to actual evidence; notify the planner of material deviations with reasons, without making routine adaptation wait for approval. Reuse meaningful checks, repeating only for an actual change or unresolved risk. One designated owner launches, stops, or resumes work on each resource.
- Deliver and consume complete results, including negative findings and real failed-run costs. Update compact `CURRENT`, task evidence, and valuable `HISTORY` entries. Sync useful small records to the project's chosen evidence center during work.
- Continue toward the overall objective after a local stage closes. Do not manufacture tasks just to fill hardware.
- When the same approach fails again without new information, change the approach, diagnose the missing fact, or send a focused peer question. Choose a useful next step rather than adding an arbitrary retry count. Delegate independent, bounded deliveries when the user and host permit it; give each an owner, disjoint scope, and a concrete return result.

Use [the coordination protocol](references/protocol.md) for a real ownership, handoff, recovery, or recording question; do not reload it ceremonially every turn. Specialized coding, research, data, and visualization skills remain responsible for their own work.

## Wait and resume

Classify the agent's state separately from a background job:

- `ACTIVE`: executing a named delivery independent of the pending signal.
- `WAITING`: the next meaningful action needs a future signal and no useful independent work remains.
- `BLOCKED`: a specific missing input, authorization, or external condition prevents progress.
- `COMPLETE`: the overall completion criteria are met.

When genuinely waiting, save the next signal, action, owner, ETA basis, and safe recovery point. If scheduled continuation is authorized and supported, pause the same role's wake during active work, then update that existing wake near the next decisive signal. A short wait needs one endpoint; use a midpoint only when it can change an action, or one calibration when ETA is unknown. Verify the actual next run where the platform exposes it. Keep schedule prompts short and state in documents. If scheduling is unavailable, report the saved resume point without claiming a wake was armed.

On wake or context loss, reload the compact mapped state and service the actual signal before launching anything. Do not duplicate runs, schedules, or role ownership. Close the role's wake when the objective is complete or the user stops it. For Codex scheduling, read [the adapter](assets/adapters/codex/setup.md) only when configuring or repairing that integration.

## Boundaries

Loading this skill supplies workflow instructions, not new permissions, a model switch, or a background daemon. Models and tool access come from the host. Separate persistent chats, cross-chat messages, scheduled tasks, and consequential project actions follow the user's authorization and the host's capabilities. Within the authorized objective, implement routine choices without repeatedly asking permission.
