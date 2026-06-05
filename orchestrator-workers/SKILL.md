---
name: orchestrator-workers
description: Coordinate a GPT-5.5 planning agent with worker53 GPT-5.4 high-confidence workers and worker54mini GPT-5.4 Mini subagents for coding, debugging, diagnosis, verification, and other execution work. Use when the user asks for a conductor-style workflow, command-style planning agent, professor/lab-style guidance, parallel workers, multi-agent implementation, task decomposition, worker53 or worker54mini delegation, "5.5 planner plus workers", or any coding task that may benefit from splitting into independently owned execution slices.
---

# Orchestrator Workers

Use this skill to turn a broad coding request into a controlled planner-worker workflow. The main agent acts like a professor or technical lead: it owns planning, design direction, hypothesis framing, task splitting, delegation, review, integration, and final accountability. Worker agents own bounded execution. Use worker54mini for low-cost scouting, evidence gathering, simple edits, and verification. Use worker53 for high-confidence coding, root-cause diagnosis, risky fixes, and integration-sensitive implementation.

The goal is not to delegate every action. The goal is to keep the main agent out of low-difficulty, high-token execution loops while still allowing enough lightweight local probing to split work well.

## Orchestrator Posture

The orchestrator should guide first and execute only when execution is needed to plan, unblock integration, or satisfy an explicit user request. It may do lightweight local reading and at most a small number of short local commands to understand context and define clean ownership boundaries.

Local execution must not evolve into a debug loop. Once the work becomes repetitive, log-heavy, failure-driven, cross-file, or verification-heavy, delegate it to the cheapest worker tier that can do the work reliably.

The main agent owns:

- Clarifying assumptions and success criteria.
- Reading lightweight context needed to split the task.
- Choosing local vs delegated execution based on the thresholds below.
- Assigning disjoint ownership scopes.
- Reviewing worker reports and changed files.
- Integrating worker results into one coherent answer.
- Making the final verification judgment and reporting residual risk.

Worker54mini owns low-cost bounded work:

- Fast codebase scouting and file mapping.
- Reading large but low-risk areas and summarizing evidence.
- Running simple or mechanical verification commands.
- Checking formatting, docs, examples, and straightforward tests.
- Implementing trivial or low-risk single-scope edits when acceptance is precise.
- Comparing worker outputs against explicit checklists.
- Producing compact evidence summaries that help GPT-5.5 or worker53 decide the next move.

Worker53 owns high-confidence execution:

- Deep inspection beyond the light context needed for planning.
- Reproducing bugs or failures.
- Running non-trivial PowerShell/shell commands and inspecting raw stdout/stderr.
- Iterating on failures, logs, stack traces, flaky behavior, build failures, or test failures.
- Adding temporary instrumentation or focused regression tests.
- Implementing bounded slices with clear file/module ownership.
- Running tests, builds, demos, screenshots, or other verification commands.
- Making non-trivial code changes where correctness, maintainability, or project conventions matter.
- Resolving root cause when initial worker54mini evidence is insufficient.

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

Choose the worker tier by risk and uncertainty:

- Use worker54mini for low-risk, high-volume, evidence-producing work: file discovery, broad but shallow repo inspection, docs checks, simple tests, simple command runs, log summarization, formatting checks, trivial patches, and independent verification.
- Use worker53 for high-risk, correctness-sensitive, or judgment-heavy work: confirmed bug diagnosis, non-trivial implementation, multi-file fixes, failing-test repair, architecture-sensitive edits, complex command failures, and root-cause analysis after worker54mini scouting.
- Escalate from worker54mini to worker53 when the mini worker reports uncertainty, hits a non-obvious failure, proposes a non-trivial fix, finds conflicting evidence, or would need to edit more than one small ownership scope.
- Do not let worker54mini independently make final architecture, security, data-loss, migration, or cross-module correctness decisions.
- Use worker54mini as a scout before worker53 when the repo area, failure surface, or verification command is unclear and the scouting result can reduce worker53 token burn.

Prefer one worker before using multiple workers. Prefer 2-4 workers for large tasks only when ownership boundaries are obvious and write scopes are disjoint. Mix worker tiers deliberately: worker54mini for scouting and verification lanes, worker53 for implementation and hard diagnosis lanes. Use more only when coordination cost is clearly low.

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
- Use 1 worker54mini for one bounded scout, simple verification pass, log summary, file map, or trivial patch.
- Use 1 worker53 for one bounded non-trivial diagnosis, implementation slice, failing-test repair, or correctness-sensitive verification.
- Use worker54mini before worker53 when a cheap scouting pass can narrow files, commands, hypotheses, or acceptance checks.
- Use 2-4 mixed workers when tasks are independent, ownership is clear, and parallelism reduces wall-clock time or main-thread token burn.
- Use more than 4 workers only when interfaces are obvious, outputs are small, and integration is cheap.

Prioritize work in this order:

1. Resolve blockers to understanding the mission and boundary.
2. Reduce high uncertainty with worker54mini discovery or worker53 diagnosis, depending on risk.
3. Reduce high risk with verification or tests, usually worker54mini first unless the check requires deep judgment.
4. Implement clearly bounded independent slices, using worker53 for non-trivial code and worker54mini for trivial or mechanical edits.
5. Run the minimum sufficient integration and regression checks, using worker54mini for routine checks and worker53 for failures.

Delegate investigation only when the expected information can change the plan, ownership split, implementation choice, or verification scope. Do not spend worker tokens on curiosity-only exploration.

## Worker Tier Matrix

Use this matrix when assigning work packages:

| Work type | Default tier | Upgrade trigger |
| --- | --- | --- |
| File discovery, ownership map, dependency map | worker54mini | Architecture is unclear or findings conflict |
| Long stdout/stderr summarization | worker54mini | Failure cause is non-obvious |
| Simple test/build command verification | worker54mini | Command fails or needs diagnosis |
| Docs/examples/config consistency check | worker54mini | Change affects runtime behavior |
| Trivial single-scope patch with precise acceptance | worker54mini | More than one file/scope or behavior is subtle |
| Bug reproduction and first evidence pass | worker54mini | Reproduction requires instrumentation or interpretation |
| Root-cause diagnosis | worker53 | Keep on worker53 unless evidence shows it is trivial |
| Non-trivial implementation | worker53 | Keep on worker53 |
| Failing test repair | worker53 | Use worker54mini only for isolated mechanical fixes |
| Architecture-sensitive, migration, security, data, or concurrency changes | worker53 | Escalate to GPT-5.5 for design decision before implementation |
| Post-integration routine regression check | worker54mini | Failures go to worker53 diagnosis |

When in doubt, start with worker54mini only if the output is evidence, not final judgment. Start with worker53 when the worker must decide and modify.

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
3. Break the task into work packages with input, output, boundary, acceptance, escalation rules, and worker tier.
4. Spawn worker54mini or worker53 subagents only for concrete, self-contained investigation, implementation, or verification tasks.
5. Tell each worker it is not alone in the codebase and must not revert user edits or edits from other workers.
6. Ask workers to run needed commands directly, inspect raw stdout/stderr, diagnose errors before changing code, make scoped edits when appropriate, and report compact evidence plus changed paths.
7. Observe worker evidence, compare it with acceptance criteria, and correct the plan if needed.
8. Review worker outputs before integrating them.
9. Delegate post-integration verification when it is command-heavy, broad, or can run in parallel. Run tiny final checks locally only when that is cheaper and within the local-execution rules.
10. Return one concise final summary with changes, validation, and any residual risks.

When doing local execution beyond trivial reading, say which local-execution reason applies.

## Delegation Prompt Pattern

When spawning a worker, choose the tier first and include it in the prompt.

For worker53, use:

```text
You are worker53, a GPT-5.4 high-confidence execution worker.
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

For worker54mini, use:

```text
You are worker54mini, a GPT-5.4 Mini execution worker.
You are not alone in the codebase. Do not revert user edits or edits from other workers.
Role: low-cost scout, verifier, summarizer, or trivial-patch worker. Prefer evidence over broad judgment.
Ownership: <files/modules/responsibility>.
Task: <bounded scouting, verification, summarization, or trivial edit request>.
Interfaces: <read-only context, forbidden files/modules, dependencies on other workers>.
Acceptance: <evidence or behavior that proves this work package is complete>.
Constraints: keep output compact; follow existing project patterns; do not broaden scope; avoid non-trivial refactors.
Execution: run the needed commands yourself; inspect stdout/stderr; summarize key facts. If diagnosis or fix becomes non-obvious, stop and escalate instead of guessing.
Output:
- Summary:
- Evidence: key files inspected, command exit codes, and minimal relevant stdout/stderr facts.
- Files changed:
- Verification:
- Uncertainty / escalation trigger:
- Ownership deviations: state "none" or explain.
```

For debugging tasks, prefer:

```text
Task: Reproduce and diagnose <bug/failure> within <ownership scope>. Run relevant commands, capture key exit codes and stdout/stderr facts, identify the likely cause, implement a scoped fix only if the cause is confirmed, and verify the result.
```

Use worker54mini for the first reproduction/evidence pass only when diagnosis is not yet required:

```text
Task: Reproduce <bug/failure> within <ownership scope> and report exact commands, exit codes, key output facts, and files implicated. Do not implement a fix. If the cause is non-obvious, ask for worker53 escalation.
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

Use the current subagent tool's default model inheritance unless the user explicitly asks for worker53/worker54mini or there is a clear task-specific reason to override.

- worker53 currently means GPT-5.4. Use it for high-confidence coding, root-cause diagnosis, failing-test repair, and correctness-sensitive implementation.
- worker54mini means GPT-5.4 Mini. Use it for low-cost scouting, routine verification, summarization, simple tests, docs/config checks, and trivial patches.
- When spawning worker53, explicitly set the subagent model override to `gpt-5.4`.
- When spawning worker54mini, explicitly set the subagent model override to `gpt-5.4-mini`.
- Preserve the worker53 role name while it is routed to GPT-5.4, so task policies do not need to change if routing is changed later.
- If the tool cannot target the intended model tier, state that limitation and use the closest available role while preserving the same task boundaries.

## User-Facing Language

When the user asks for the conductor-style workflow, interpret it as:

- Plan and design with the main GPT-5.5 agent.
- Use worker54mini for low-cost scouting, summarization, routine command runs, simple verification, and trivial patches.
- Use worker53 for heavy lifting: deep diagnosis, non-trivial command failure analysis, implementation slices, failing-test repair, and correctness-sensitive verification.
- Keep the orchestrator in a professor/technical-lead role: guide, challenge, redirect, review, and integrate.
- Let the orchestrator perform only lightweight local probing and integration checks.
- Use hard delegation thresholds to prevent the main thread from drifting into debug loops.
- Escalate from worker54mini to worker53 when evidence becomes ambiguous, failures are non-obvious, or implementation risk rises.
- Keep ownership boundaries explicit.
- Integrate and report as one accountable agent based on reviewed worker results.
