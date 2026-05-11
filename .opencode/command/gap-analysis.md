---
#
description: Analyze gaps between development artifacts (spec, plan, tests, code)
agent: gap-analysis
subtask: true
---

<purpose>
Systematically compare development artifacts to identify gaps, inconsistencies, and missing coverage across the change lifecycle.

User invocation: `/gap-analysis <workItemRef>`

Produces a coverage matrix and gap report showing traceability between user stories, specifications, plans, tests, and code.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `workItemRef` = first token matching pattern `<PREFIX>-<number>` (e.g., `PDEV-123`, `GH-456`)
- `--scope <dimension>`: specific comparison (e.g., "spec-vs-code", "us-vs-spec", "plan-vs-code"). Default: all
- `--focus <area>`: priority area (e.g., "security", "error-handling")
- If no valid `workItemRef` found:
  ```
  NEEDS_INPUT: workItemRef required
  Usage: /gap-analysis <workItemRef>
  Example: /gap-analysis GH-456
  ```
</parsing>
</inputs>

<discovery_rules>
Given `workItemRef`:
1. Search for folder: `.samourai/docai/changes/**/*--<workItemRef>--*/`
2. Locate: spec, plan, test plan, PM notes in the change folder
3. Identify changed files: `git diff main...HEAD --name-only`
</discovery_rules>

<process>
1. Parse `workItemRef` from $ARGUMENTS
2. Locate all change artifacts per discovery rules
3. Delegate to `@gap-analysis` agent with workItemRef and scope
4. Agent performs multi-dimensional comparison:
   - User story → Spec (every requirement addressed?)
   - Spec → Plan (every AC has a task?)
   - Spec → Tests (every AC has test coverage?)
   - Spec → Code (every AC implemented?)
   - Plan → Code (every task completed?)
5. Report: gap report with coverage matrix and verdict
</process>

<output>
After successful execution:
- Coverage matrix (AC × artifact dimension)
- Gap list with severity and remediation
- Coverage percentage
- Verdict: PASS (full traceability) or FAIL (gaps found)
</output>

<constraints>
- Read ALL artifacts before reporting gaps
- Distinguish intentional exclusions (non-goals) from true gaps
- Reference specific AC numbers, task IDs, and test case IDs
- Severity: critical = missing core functionality, major = incomplete coverage
</constraints>
