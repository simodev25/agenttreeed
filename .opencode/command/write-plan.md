---
#
description: Generate or update implementation plan
agent: plan-writer
subtask: true
---

<purpose>
Produce (or update) a fully structured IMPLEMENTATION PLAN from the canonical CHANGE SPECIFICATION.

User invocation: `/write-plan <workItemRef>`

Writes (or updates): `chg-<workItemRef>-plan.md` in the same change folder as the spec.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `workItemRef` = first token matching pattern `<PREFIX>-<number>` (e.g., `PDEV-123`, `GH-456`)
- If no valid `workItemRef` found, output NEEDS_INPUT:
  ```
  NEEDS_INPUT: workItemRef required
  Usage: /write-plan <workItemRef>
  Example: /write-plan PDEV-123
  ```
</parsing>
</inputs>

<discovery_rules>
Given `workItemRef`:

1. Search for folder: `.samourai/docai/changes/**/*--<workItemRef>--*/`
2. Locate spec: `chg-<workItemRef>-spec.md`
3. If spec not found → FAIL

Files:

- Spec: `chg-<workItemRef>-spec.md`
- Plan: `chg-<workItemRef>-plan.md`
- Branch: `<change.type>/<workItemRef>/<slug>`
  </discovery_rules>

<process>
1. Parse `workItemRef` from $ARGUMENTS
2. Locate change folder and spec file per <discovery_rules>
3. Extract slug, type, owners, etc. from spec front matter
4. Read `.samourai/ai/agent/project-profile.md` when present and pass it to `@plan-writer`.
5. Checkout/create branch
6. Delegate to `@plan-writer` agent (it has full template, project profile policy, and rules)
7. Report: path to created plan, project profile applied, next step: `/write-test-plan <workItemRef>` or `/run-plan <workItemRef>`
</process>

<output>
After successful execution:
- Created/updated file path
- Branch name
- Project profile applied: mode/modifiers used, or `none` if absent
- Recommendation: "Run `/write-test-plan <workItemRef>` to generate the test plan, or `/run-plan <workItemRef>` to begin execution"
</output>

<constraints>
- Spec must exist; fail if not found
- Only the plan file may be written
- Derive all context from spec; do not invent
</constraints>
