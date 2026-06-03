---
name: orchestrator-workers
description: Coordinate a GPT-5.5 planning agent with worker53 GPT-5.3 Codex subagents for coding, debugging, diagnosis, verification, and other heavy execution work. Use when the user asks for a conductor-style workflow, command-style planning agent, professor/lab-style guidance, parallel workers, multi-agent implementation, task decomposition, worker53 delegation, "5.5 planner plus 5.3 workers", or any coding task that may benefit from splitting into independently owned execution slices.
---

# Orchestrator Workers

Use this skill to turn a broad coding request into a controlled planner-worker workflow. The main agent acts like a professor or technical lead: it owns planning, design direction, hypothesis framing, task splitting, delegation, review, integration, and final accountability. Worker agents own bounded heavy lifting: deep repo inspection, non-trivial command execution, stdout/stderr analysis, reproduction loops, diagnosis loops, instrumentation, implementation slices, tests, builds, formatting, docs edits, and verification commands.

The goal is not to delegate every action. The goal is to keep the main agent out of low-difficulty, high-token execution loops while still allowing enough lightweight local probing to split work well.

## Orchestrator Posture

The orchestrator should guide first and execute only when execution is needed to plan, unblock integration, or satisfy an explicit user request. It may do lightweight local reading and at most a small number of short local commands to understand context and define clean ownership boundaries.

Local execution must not evolve into a debug loop. Once the work becomes repetitive, log-heavy, failure-driven, cross-file, or verification-heavy, delegate it to worker53.

The main agent owns:

- Clarifying assumptions and success criteria.
- Reading lightweight context needed to split the task.
- Choosing local vs delegated execution based on the thresholds below.
- Assigning disjoint ownership scopes.
- Reviewing worker reports and changed files.
- Integrating worker results into one coherent answer.
- Making the final verification judgment and reporting residual risk.

Worker53 owns:

- Deep inspection beyond the light context needed for planning.
- Reproducing bugs or failures.
- Running non-trivial PowerShell/shell commands and inspecting raw stdout/stderr.
- Iterating on failures, logs, stack traces, flaky behavior, build failures, or test failures.
- Adding temporary instrumentation or focused regression tests.
- Implementing bounded slices with clear file/module ownership.
- Running tests, builds, demos, screenshots, or other verification commands.

## Decision Rule

Use workers when delegation is likely to reduce main-thread token burn, avoid debug-loop drift, or parallelize genuinely independent work. Keep work local when it is tiny, tightly coupled, on the immediate critical path, or approval-sensitive.

Keep local when:

- The task is a tiny read-only check needed to form delegation prompts or ownership boundaries.
- The result is an immediate blocker that the orchestrator must know before it can split work.
- The task is a single-file or very small edit where delegation overhead exceeds execution cost.
- The work is tightly coupled and cannot be assigned a clean ownership boundary.
- The command is approval-sensitive, destructive, networked, or risky and the orchestrator must ask the user directly.
- Tool limitations prevent worker delegation.
- The user explicitly asks the orchestrator to run the command or make the edit directly.

Delegate immediately when any condition is met:

- More than 2 local commands would be needed for the same issue.
- A local command fails and the cause is not obvious from the first failure.
- Relevant command output is likely to exceed roughly 100-200 lines.
- The task requires reproducing a bug, inspecting logs, or iterating on failures.
- The fix is likely to touch more than 1-2 files.
- Verification requires more than one test, build, demo, screenshot, or environment command.
- The task needs substantial repo inspection beyond the files needed to split ownership.
- The task can be split into independent modules, routes, packages, adapters, tests, or verification passes.

Prefer one worker before using multiple workers. Prefer 2-4 workers for large tasks only when ownership boundaries are obvious and write scopes are disjoint. Use more only when coordination cost is clearly low.

Never delegate the immediate blocker if the main agent cannot make progress until that answer returns. Do the blocker locally, then delegate sidecar or downstream work.

## Token Discipline

Treat delegation as a token-control mechanism, not only a speed mechanism.

- Do not paste long stdout/stderr into the main thread. Ask workers to summarize key facts, exit codes, and the minimal relevant excerpts.
- Do not ask multiple workers to inspect the same broad area.
- Do not spawn workers for trivial file reads, one-line edits, or single short commands.
- Stop local execution once it starts repeating. Repeated command attempts, repeated search passes, and log-chasing belong to workers.
- Ask workers for compact, evidence-based reports instead of narrative transcripts.
- After workers return, review only the files and evidence needed to integrate.

## Systems Engineering Frame

Treat each non-trivial request as a small systems-engineering problem before treating it as a set of prompts.

Use this frame when the task is broad, ambiguous, multi-file, risky, or likely to need workers:

- Mission: restate the user's goal, success criteria, and constraints.
- Boundary: identify what is inside scope, outside scope, and unknown.
- WBS: break the work into concrete work packages with one primary output each.
- Interfaces: define ownership, read/write boundaries, dependencies, and expected artifacts for each worker.
- Integration: decide how worker outputs will be merged and reviewed.
- Verification: define requirement-level, module-level, integration-level, and regression checks.
- Lessons: note reusable findings only when they affect future orchestration.

Do not make the frame verbose by default. Use the smallest explicit version that improves delegation quality.

## Work Breakdown Rules

Use work breakdown to convert broad intent into bounded execution.

Each delegated work package should have:

- Input: files, modules, failing behavior, command, or artifact to inspect.
- Output: one primary result, such as a diagnosis, patch, test, verification report, or risk assessment.
- Boundary: owned files/modules, read-only context, forbidden files/modules, and dependencies.
- Acceptance: what evidence proves the work is done.
- Escalation: what the worker should report instead of guessing or broadening scope.

Avoid work packages that ask a worker to "understand the whole project" or "fix everything". If the ownership boundary is unclear, first delegate a narrow discovery or diagnosis task, then split implementation after evidence returns.

## Operations Research Dispatch Rules

Treat orchestration as a constrained scheduling problem. Optimize for enough confidence at the lowest combined cost of main-thread tokens, worker coordination, wall-clock delay, merge conflict risk, and repeated inspection.

Dispatch by expected value:

- Use 0 workers for tiny, single-file, immediate-critical-path tasks.
- Use 1 worker for one bounded diagnosis, implementation slice, or verification pass.
- Use 2-4 workers when tasks are independent, ownership is clear, and parallelism reduces wall-clock time or main-thread token burn.
- Use more than 4 workers only when interfaces are obvious, outputs are small, and integration is cheap.

Prioritize work in this order:

1. Resolve blockers to understanding the mission and boundary.
2. Reduce high uncertainty with diagnosis or discovery.
3. Reduce high risk with verification or tests.
4. Implement clearly bounded independent slices.
5. Run the minimum sufficient integration and regression checks.

Delegate investigation only when the expected information can change the plan, ownership split, implementation choice, or verification scope. Do not spend worker tokens on curiosity-only exploration.

## Feedback Control Loop

Run orchestration as a closed loop:

```text
Plan -> Delegate -> Observe Evidence -> Compare With Acceptance -> Correct Plan -> Integrate -> Verify
```

Handle deviations explicitly:

- Worker output incomplete: narrow the task and retry once.
- Worker crosses ownership: inspect the deviation before integrating.
- Workers disagree: compare evidence and commands, not model identity.
- Verification fails: delegate diagnosis instead of letting the main agent enter a debug loop.
- Scope expands: restate mission, boundary, and acceptance before adding workers.
- Token burn rises: reduce worker count, compress report format, or switch to the next highest-value check.

## Workflow

1. Read only lightweight context needed to define the mission, boundary, and ownership split.
2. State a short plan when the work is substantial, including the local critical path and delegated sidecar work.
3. Break the task into work packages with input, output, boundary, acceptance, and escalation rules.
4. Spawn worker53 subagents only for concrete, self-contained investigation, implementation, or verification tasks.
5. Tell each worker it is not alone in the codebase and must not revert user edits or edits from other workers.
6. Ask workers to run needed commands directly, inspect raw stdout/stderr, diagnose errors before changing code, make scoped edits when appropriate, and report compact evidence plus changed paths.
7. Observe worker evidence, compare it with acceptance criteria, and correct the plan if needed.
8. Review worker outputs before integrating them.
9. Delegate post-integration verification when it is command-heavy, broad, or can run in parallel. Run tiny final checks locally only when that is cheaper and within the local-execution rules.
10. Return one concise final summary with changes, validation, and any residual risks.

When doing local execution beyond trivial reading, say which local-execution reason applies.

## Delegation Prompt Pattern

When spawning a worker, include:

```text
You are worker53, a GPT-5.3 Codex execution worker.
You are not alone in the codebase. Do not revert user edits or edits from other workers.
Ownership: <files/modules/responsibility>.
Task: <bounded investigation, implementation, or verification request>.
Interfaces: <read-only context, forbidden files/modules, dependencies on other workers>.
Acceptance: <evidence or behavior that proves this work package is complete>.
Constraints: follow existing project patterns; keep changes scoped; avoid unrelated refactors.
Execution: run the needed commands yourself; inspect stdout/stderr; diagnose errors before changing code.
Output:
- Summary:
- Evidence: key files inspected, command exit codes, and minimal relevant stdout/stderr facts.
- Root cause or leading hypothesis:
- Files changed:
- Verification:
- Risks / unverified items:
- Ownership deviations: state "none" or explain.
- Escalation needed: state "none" or ask for a narrower follow-up.
```

For debugging tasks, prefer:

```text
Task: Reproduce and diagnose <bug/failure> within <ownership scope>. Run relevant commands, capture key exit codes and stdout/stderr facts, identify the likely cause, implement a scoped fix only if the cause is confirmed, and verify the result.
```

For verification tasks, prefer:

```text
Task: Verify <behavior/change> within <ownership scope>. Run the relevant test/build/demo commands, inspect failures if any, and report command names, exit codes, key output facts, and residual risk. Do not edit files unless verification cannot proceed without a small obvious fix; report any such fix explicitly.
```

## Ownership Patterns

Use ownership boundaries such as:

- Frontend component vs backend endpoint.
- Implementation vs tests.
- Parser vs renderer.
- One route, package, module, adapter, or feature flag per worker.
- Reproduction/diagnosis worker vs implementation worker.
- Read-only verification worker while diagnosis or implementation continues elsewhere.

Avoid splits where multiple workers need to edit the same file unless the work can be cleanly staged by sequence. If workers must touch nearby files, name each write scope explicitly.

## Integration Rules

- Trust worker findings enough to avoid repeating their whole task, but review their changed files and evidence.
- Prefer integrating smaller patches as they arrive.
- Resolve conflicts by preserving user changes first, then worker intent.
- Keep main-agent actions focused on planning, review, integration, and final judgment.
- If a worker returns incomplete work, narrow the task and retry once before escalating.
- If a worker crosses its ownership boundary, inspect that deviation before integrating.
- If worker outputs disagree, compare evidence first; do not resolve by authority or model identity.

## Model Selection

Use the current subagent tool's default model inheritance unless the user explicitly asks for worker53 or there is a clear task-specific reason to use GPT-5.3 Codex. When an explicit worker53 model override is needed, use the tool's current model name for GPT-5.3 Codex.

## User-Facing Language

When the user asks for the conductor-style workflow, interpret it as:

- Plan and design with the main GPT-5.5 agent.
- Use worker53 for heavy lifting: deep inspection, command execution, reproduction, diagnosis, implementation slices, and verification.
- Keep the orchestrator in a professor/technical-lead role: guide, challenge, redirect, review, and integrate.
- Let the orchestrator perform only lightweight local probing and integration checks.
- Use hard delegation thresholds to prevent the main thread from drifting into debug loops.
- Keep ownership boundaries explicit.
- Integrate and report as one accountable agent based on reviewed worker results.
