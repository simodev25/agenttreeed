---
description: Execute a TDD cycle for a specific task or phase — writes failing test first, then implementation, then refactors.
agent: tdd-orchestrator
subtask: true
---

<purpose>
Invoke @tdd-orchestrator to implement a task or plan phase by strictly following the red-green-refactor cycle. Guarantees that tests are written BEFORE production code.

Used by @coder in /run-plan when the tdd-orchestrator skill is active, or invoked directly for a specific task.
</purpose>

<command>
User invocation:
  /tdd <workItemRef> [task description or phase number]
Examples:
  /tdd GH-42
  /tdd GH-42 phase 3
  /tdd GH-42 "implement user authentication"
  /tdd PDEV-123 next task
</command>

<inputs>
  <item>workItemRef='$1' — Tracker reference (e.g., `GH-456`, `PDEV-123`). REQUIRED.</item>
  <item>scope='$ARGUMENTS' — Phase number, task description, or "next task". OPTIONAL (default: next incomplete task in the plan).</item>
</inputs>

<discovery_rules>
<rule>Locate change folder: search `.samourai/docai/changes/**/*--<workItemRef>--*/`</rule>
<rule>Plan file: `chg-<workItemRef>-plan.md` — source of truth for tasks</rule>
<rule>Test-plan file: `chg-<workItemRef>-test-plan.md` — tests to implement</rule>
<rule>Spec file: `chg-<workItemRef>-spec.md` — acceptance criteria</rule>
</discovery_rules>

<scope_resolution>
Resolve the target task from $ARGUMENTS:
- "phase N" → all incomplete tasks in phase N
- "next task" or absent → first incomplete task in the plan
- free-form description → match against plan tasks (fuzzy match)
- If ambiguous → list candidates and request confirmation
</scope_resolution>

<process>
1. Resolve the change folder and locate plan + test-plan + spec
2. Read `.samourai/ai/agent/project-profile.md` if present and pass it to @tdd-orchestrator
3. Identify the target task(s) according to scope_resolution
4. For each task:
   a. Read the test-plan to identify the corresponding tests
   b. Invoke @tdd-orchestrator with: task, test_plan_path, spec_path
   c. @tdd-orchestrator executes the RED → GREEN → REFACTOR cycle
   d. Update the plan: mark [x] + evidence
   e. Commit via /commit (one commit per completed TDD task)
5. Final report: completed tasks, tests written, coverage, project profile applied
</process>

<integration>
This command integrates into the Samourai pipeline:
- Called by @coder in /run-plan when the tdd-orchestrator skill is active
- Can replace /run-plan for a specific task requiring strict TDD
- Commits produced follow the Conventional Commits format via /commit
</integration>

<output>
Structured report:
- Tasks processed + status (COMPLETE / PARTIAL / BLOCKED)
- Tests written (N unit / N integration / N e2e)
- Coverage delta
- Anti-patterns detected
- Project profile applied (`TMA`, `Build`, `Guide`, `Mix` or `none`)
- Suggested next action
</output>

<errors>
- Plan or test-plan missing → STOP with a clear message
- Target task not found → list available tasks
- GREEN phase impossible after 3 attempts → BLOCKED, document in the plan
</errors>
