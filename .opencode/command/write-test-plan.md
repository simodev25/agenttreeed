---
#
description: Generate or update change test plan
agent: test-plan-writer
subtask: true
---

<purpose>
Create or update a COMPLETE, requirements-driven TEST PLAN for a change.

User invocation: `/write-test-plan <workItemRef> [options]`

Options: `focus=backend`, `nfr-only`, `no-manual`, etc.

The TEST PLAN:

- Ensures full coverage of capabilities, interfaces, and acceptance criteria
- Aligns with implementation plan phases
- Maps scenarios to test types per `.samourai/ai/rules/testing-strategy.md`
  </purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `workItemRef` = first token matching pattern `<PREFIX>-<number>` (e.g., `PDEV-123`, `GH-456`)
- Remaining args = options (e.g., `focus=backend`)
- If no valid `workItemRef` found, output NEEDS_INPUT:
  ```
  NEEDS_INPUT: workItemRef required
  Usage: /write-test-plan <workItemRef> [options]
  Example: /write-test-plan PDEV-123 focus=backend
  ```
</parsing>
</inputs>

<discovery_rules>
Given `workItemRef`:

1. Search for folder: `.samourai/docai/changes/**/*--<workItemRef>--*/`
2. Locate spec: `chg-<workItemRef>-spec.md` (required)
3. Locate plan: `chg-<workItemRef>-plan.md` (optional)
4. Read: `.samourai/ai/rules/testing-strategy.md` (required)

Files:

- Spec: `chg-<workItemRef>-spec.md`
- Plan: `chg-<workItemRef>-plan.md`
- Test Plan: `chg-<workItemRef>-test-plan.md`
- Branch: `<change.type>/<workItemRef>/<slug>`
  </discovery_rules>

<process>
1. Parse `workItemRef` and options from $ARGUMENTS
2. Locate change folder, spec, plan per <discovery_rules>
3. Read `.samourai/ai/rules/testing-strategy.md`; FAIL if missing
4. Read `.samourai/blueprints/testing/` when available and pass it to
   `@test-plan-writer` as structural guidance only.
5. Extract F-#, AC-#, API-#, NFR-# from spec
6. Checkout/create branch
7. Delegate to `@test-plan-writer` agent (it has full template and rules)
8. Report: path to created test plan, next step: `/run-plan <workItemRef>`
</process>

<output>
After successful execution:
- Created/updated file path
- Branch name
- Coverage summary (how many AC-# covered, any TODOs)
- Recommendation: "Run `/run-plan <workItemRef>` to begin execution"
</output>

<constraints>
- Spec must exist; fail if not found
- Testing strategy must exist; fail if not found
- Only the test plan file may be written
- Derive all context from spec/plan; do not invent requirements
- Mark uncovered AC-# as TODO with open questions
</constraints>
