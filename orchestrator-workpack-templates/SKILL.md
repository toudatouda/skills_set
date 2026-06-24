---
name: orchestrator-workpack-templates
description: Companion templates for orchestrator-workers. Use with orchestrator-workers when a task needs standardized work-package decomposition, worker53/worker54mini prompts, ownership boundaries, acceptance criteria, escalation rules, or final integration checklists across projects.
---

# Orchestrator Workpack Templates

Use this skill together with `orchestrator-workers`.

`orchestrator-workers` decides when and how to delegate. This companion skill standardizes the shape of the delegated work: mission framing, work packages, worker prompts, acceptance checks, escalation boundaries, and final integration reporting.

Do not use this skill as a replacement for `orchestrator-workers`. Use it as the template layer after the orchestrator has decided that delegation or structured planning is useful.

## When To Use

Use this skill when the user asks for:

- A task split suitable for subagents.
- A repeatable multi-agent execution plan.
- Worker53 / worker54mini prompt templates.
- A reusable work-package breakdown.
- A complex debugging, implementation, verification, cleanup, or demonstration task that needs clear ownership and acceptance.
- A project-agnostic version of a previous successful orchestration pattern.

Use it especially when the task includes any of these risks:

- Multiple files or subsystems.
- Runtime commands, long logs, GUI processes, external services, or generated artifacts.
- Safety, claim-boundary, compliance, data-loss, or irreversible operations.
- A need to separate scouting from implementation and verification.

## Relationship To orchestrator-workers

The main agent should first apply `orchestrator-workers` decision rules:

- Keep tiny immediate blockers local.
- Delegate only bounded, useful work.
- Use worker54mini for low-cost scouting, verification, static checks, summarization, and trivial patches.
- Use worker53 for high-confidence implementation, root-cause diagnosis, failing-test repair, risky command diagnosis, and integration-sensitive work.
- Avoid parallel writes to the same file or subsystem.
- Review worker evidence before integrating.

Then use this skill to format the work into concrete work packages.

## Orchestrator Planning Frame

For any non-trivial task, produce the smallest useful version of this frame:

```text
Mission:
<one sentence objective>

Success criteria:
- <observable result>
- <required validation or artifact>

Scope:
- In scope: <files/subsystems/actions>
- Out of scope: <explicit non-goals>

Claim boundaries:
- Allowed to say: <accepted claims>
- Not allowed to say: <pending or unproven claims>

Signals:
- <observable evidence that indicates progress: exit codes, artifacts, metrics, screenshots, changed files, user-visible behavior>

Disturbances:
- <environmental or external factors that could perturb the task: flaky tests, GUI state, WSL/GPU state, permissions, network, long logs, concurrent edits>

Control actions:
- <allowed corrective actions: narrow scope, dispatch worker, escalate worker tier, rerun once, ask user, stop risky action>

Scheduling:
- Dependency graph: <WP ids and required predecessor outputs>
- Resource locks: <files, services, databases, GUI, runtime processes, generated artifacts, external systems>
- Parallel batches: <WP ids that may run together>
- Serial critical path: <WP ids that must run in order>

Local critical path:
- <what the main agent must do locally before or during delegation>

Work packages:
- WP0 ...
- WP1 ...

Integration plan:
- <how worker outputs will be reviewed and combined>

Final validation:
- <minimum sufficient commands/checks>
```

## Work Package Template

Each work package should have one primary output.

```text
Work Package <N>: <short name>

Tier:
<worker54mini | worker53>

Ownership:
- Read/write: <exact files, modules, directories, or responsibility>
- Read-only: <context paths>
- Forbidden: <paths, processes, actions, or subsystems>

Task:
<bounded execution request with one primary output>

Interfaces:
- Inputs: <files, commands, logs, artifacts, previous worker output>
- Dependencies: <other worker output or none>
- Outputs: <patch, diagnosis, verification report, artifact inventory, etc.>

Scheduling:
- Mode: <parallel-safe | serial-after:WP<N> | exclusive-resource>
- Dependencies: <none | WP ids and required outputs>
- Resource locks: <none | exact files/services/db/gui/runtime/artifacts/external state>
- Mutation scope: <read-only | writes:<paths> | runtime-state | external-state>
- Gate required before start: <none | repro confirmed | hypothesis ranked | fix merged | artifact inventory complete | user approval>

Acceptance:
- <evidence item>
- <command and expected status>
- <artifact/report requirement>

Escalation:
- Stop and report if <condition>.
- Do not broaden into <adjacent subsystem>.

Stop condition:
- <maximum retry count, timeout, evidence threshold, or safety boundary that ends the work package>

Output format:
- Summary:
- Evidence:
- Observed vs expected:
- Files changed:
- Verification:
- Risks / uncertainty:
- Ownership deviations:
- Escalation needed:
```

## worker54mini Prompt Template

Use worker54mini for evidence-first, low-risk work.

```text
You are worker54mini, a GPT-5.4 Mini execution worker.
You are not alone in the codebase. Do not revert user edits or edits from other workers.

Role:
Low-cost scout, verifier, summarizer, docs/config checker, artifact inventory worker, or trivial-patch worker. Prefer evidence over broad judgment.

Workspace:
<workspace path>

Ownership:
<owned read/write files, or "read-only">

Task:
<bounded scouting, verification, summarization, or trivial edit request>

Interfaces:
- Read-only context: <paths>
- Forbidden: <paths/processes/actions>
- Dependencies: <other worker outputs if any>

Acceptance:
- <specific evidence proving completion>
- <required commands and expected status, if applicable>
- <artifact paths, if applicable>

Constraints:
- Keep output compact.
- Do not broaden scope.
- Do not run GUI, long-running runtime commands, or destructive commands unless explicitly assigned.
- If diagnosis or fix becomes non-obvious, stop and escalate instead of guessing.

Execution:
Run needed commands yourself, inspect stdout/stderr, and summarize key facts. Do not paste long logs.

Output:
- Summary:
- Evidence: key files inspected, command exit codes, and minimal relevant stdout/stderr facts.
- Observed vs expected:
- Files changed:
- Verification:
- Uncertainty / escalation trigger:
- Ownership deviations: state "none" or explain.
```

## worker53 Prompt Template

Use worker53 for high-confidence execution and diagnosis.

```text
You are worker53, a GPT-5.4 high-confidence execution worker.
You are not alone in the codebase. Do not revert user edits or edits from other workers.

Workspace:
<workspace path>

Ownership:
<exact files/modules/responsibility this worker owns>

Task:
<bounded diagnosis, implementation, or verification request>

Interfaces:
- Read-only context: <paths>
- Forbidden: <paths/processes/actions>
- Dependencies: <other worker outputs if any>

Acceptance:
- <specific behavior/evidence required>
- <commands to run and expected exit codes>
- <artifact paths or report requirements>

Constraints:
- Follow existing project patterns.
- Keep changes scoped.
- Avoid unrelated refactors.
- Diagnose errors before changing code.
- Do not claim acceptance unless the matching gate passed.
- Do not start unbounded runtime processes; use timeout and cleanup paths.

Execution:
Run needed commands yourself, inspect stdout/stderr, diagnose failures before changing code, make scoped edits when appropriate, and verify the result.

Output:
- Summary:
- Evidence: key files inspected, command exit codes, and minimal relevant stdout/stderr facts.
- Observed vs expected:
- Root cause or leading hypothesis:
- Files changed:
- Verification:
- Risks / unverified items:
- Ownership deviations: state "none" or explain.
- Escalation needed: state "none" or ask for a narrower follow-up.
```

## Common Workpack Patterns

### Closed-Loop Verification

Use when a task needs a clear accept/retry/escalate decision.

```text
Packages:
1. Define expected state: acceptance criteria, target artifact, metric, UI state, or command result.
2. Act: run the bounded command, patch, demo, or verification step.
3. Observe: collect exit code, artifact path, screenshot, metric, or minimal log excerpt.
4. Compare: state expected vs observed directly.
5. Correct: accept, retry once, escalate, block, or revise the plan.

Acceptance:
- Expected state is explicit.
- Observed evidence is concrete.
- Decision follows from the comparison.
- No open-ended repeated retries.
```

### Disturbance Handling

Use when external state may perturb the task.

```text
Common disturbances:
- Flaky tests or nondeterministic timing.
- GUI, GPU, display, or window-system state.
- Network, package registry, or external service failure.
- Permission or sandbox boundary.
- Long logs or noisy output.
- Concurrent user edits or generated files.

Default response:
- Capture one bounded evidence sample.
- Retry once only when the likely cause is transient and the retry is safe.
- If still unclear, escalate to worker53 or ask the user.
- Stabilize environment before changing more code.
- Report the disturbance separately from the project bug.
```

### Read-Only Inventory

Use before cleanup, migration, risky refactor, or broad implementation.

```text
WP: Inventory
Tier: worker54mini
Ownership: read-only
Task: Map relevant files, current commands, artifacts, and known risks. Do not edit.
Acceptance: compact file map, implemented vs pending status, and ambiguity list.
Escalation: stop if docs/configs contradict each other.
```

### Runtime Or GUI Rehearsal

Only one worker may launch the runtime or GUI.

```text
Packages:
1. Preflight scout, worker54mini, read-only.
2. Runtime launch owner, worker53, the only worker allowed to start the process.
3. Monitor, worker54mini, samples resource/process status.
4. Artifact collector, worker54mini, reports logs/manifests/screenshots if available.
5. Claim reviewer, worker54mini, checks presentation or acceptance language.

Acceptance:
- Launch command result is known.
- Artifacts are reported.
- Human-visible quality or runtime health is assessed.
- No residual process remains.
- Claims remain bounded.
```

### Failure Diagnosis

Use when a command fails or hangs.

```text
Packages:
1. Evidence pass, worker54mini, reproduce once and collect command, exit code, short logs, and implicated files. Do not edit.
2. Diagnosis/fix, worker53, implement a scoped fix only after the likely cause is confirmed.
3. Verification, worker54mini or main agent, rerun minimum sufficient checks.

Acceptance:
- Failure subsystem identified.
- Fix scope is narrow.
- Verification passes or blocker is explicit.
- No repeated blind retries.
```

### Artifact Cleanup

Use before moving or deleting generated outputs.

```text
Packages:
1. Inventory, worker54mini, read-only keep/delete/archive recommendation.
2. Cleanup executor, worker53 or main agent, explicit paths only.
3. Verification, worker54mini, confirm keep paths, ignore rules, and validation commands.

Rules:
- Prefer archive over delete for evidence.
- Never move active environment backing files unless verified safe.
- Before recursive delete or move, verify absolute paths are inside the intended workspace.
```

### Contract Or Gate Hardening

Use for safety boundaries, API contracts, scenario contracts, data schemas, or acceptance gates.

```text
Packages:
1. Contract scout, worker54mini, read-only current-state map.
2. Contract hardening, worker53, scoped validator/config/docs update.
3. Independent verification, worker54mini, runs static checks and claim-boundary review.

Acceptance:
- Validator catches the target class of error.
- Docs and config agree.
- Runtime acceptance is not claimed unless proven.
```

### Build Or Test Repair

```text
Packages:
1. Reproduction, worker54mini if simple; worker53 if failure is likely complex.
2. Root-cause fix, worker53.
3. Regression verification, worker54mini.

Acceptance:
- Exact failing command and exit code are known.
- Root cause or leading hypothesis is grounded in logs/source.
- Fix is scoped.
- Relevant tests/builds pass.
```

## Dispatch Guidance

### Scheduling Classification

Classify every work package before dispatch. If a package cannot be classified, keep it local or serial until the missing dependency, lock, or mutation scope is explicit.

Use `parallel-safe` only when:

- Packages are read-only, or write to disjoint files, modules, generated artifacts, and subsystems.
- They do not share mutable runtime state, database state, GUI state, browser state, simulator state, hardware state, or external services.
- Their outputs are independent reports, patches, inventories, or verification results.
- No package depends on another package's output, decision, artifact, or command result.

Use `serial-after:WP<N>` when:

- A package needs another package's evidence, patch, artifact, diagnosis, or decision.
- Packages touch the same file, same module, same migration/schema, same generated artifact, same runtime config, or same ownership boundary.
- The work follows a phase gate such as reproduce before hypothesize, hypothesize before instrument, instrument before fix, or fix before regression claim.
- The later package would duplicate, invalidate, or race the earlier package's result.

Use `exclusive-resource` when:

- A package launches, stops, configures, or mutates shared services, GUI apps, browsers, databases, simulators, hardware, containers, package managers, credentials, or global/project runtime state.
- The action is destructive, irreversible, expensive to repeat, or changes external state.
- Only one worker can safely own the environment, runtime, artifact directory, or claim boundary.

Default to serial for writes unless disjoint ownership is concrete. Default to exclusive-resource for runtime, GUI, simulator, database, hardware, and external-service actions.

Prefer these splits:

- One worker54mini scout before worker53 when file ownership is unclear.
- One worker53 for a tightly coupled fix.
- Two to four workers only when write scopes are disjoint.
- Read-only verification in parallel with implementation only when it does not duplicate work.
- Parallel batches of read-only scouts, artifact inventories, or independent static checks.
- Serial chains for diagnosis phase gates, shared-file edits, schema/config changes, and fix-then-verify flows.
- Exclusive owners for runtime launch, GUI/browser control, simulator sessions, database mutation, cleanup, and external-service operations.

Avoid these splits:

- Multiple workers editing the same file.
- Multiple workers starting the same runtime service.
- One worker asked to "understand the whole project".
- Worker54mini making final architecture, security, migration, or data-loss decisions.
- Any parallel package whose dependency, resource lock, or mutation scope is implicit.
- Parallel diagnosis packages that change more than one variable against the same failure loop.

## Integration Checklist

Before final response, the orchestrator checks:

- Did each worker stay within ownership?
- Were user edits preserved?
- Are generated artifacts ignored or intentionally tracked?
- Are acceptance criteria actually satisfied?
- Has each result been compared against expected state?
- Are verified facts separated from inferred claims?
- Are command failures explained with exit codes and short evidence?
- Are runtime or GUI processes cleaned up?
- Are claim boundaries accurate?
- Is the final answer based on accepted gates, not aspirational goals?

## Final Report Template

```text
Summary:
<what was accomplished>

Changes:
- <files/modules changed>

Validation:
- <command>: <exit code/result>

Observed vs expected:
- Expected: <target state>
- Observed: <evidence>
- Decision: <accepted / pending / escalated / blocked>

Artifacts:
- <paths, if any>

Residual risks:
- <pending gates or unverified items>

Next recommended step:
<one or two concrete actions>
```
