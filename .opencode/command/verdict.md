---
#
description: Evaluate change readiness and produce GO/NO-GO verdict
agent: verdict
subtask: true
---

<purpose>
Evaluate overall change readiness for merge/release by aggregating quality signals. Produces a definitive GO or NO-GO verdict.

User invocation: `/verdict <workItemRef>`

Aggregates: build status, test results, review findings, spec compliance, gap analysis, documentation status. Produces an advisory verdict for the human reviewer.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `workItemRef` = first token matching pattern `<PREFIX>-<number>` (e.g., `PDEV-123`, `GH-456`)
- `--skip <gate>`: skip a specific soft gate (must justify)
- If no valid `workItemRef` found:
  ```
  NEEDS_INPUT: workItemRef required
  Usage: /verdict <workItemRef>
  Example: /verdict PDEV-123
  ```
</parsing>
</inputs>

<discovery_rules>
Given `workItemRef`:
1. Search for folder: `.samourai/docai/changes/**/*--<workItemRef>--*/`
2. Locate: PM notes, spec, plan, test plan, review reports
3. Check quality gate artifacts in `.samourai/tmpai/`
</discovery_rules>

<process>
1. Parse `workItemRef` from $ARGUMENTS
2. Locate all change artifacts per discovery rules
3. Delegate to `@verdict` agent with workItemRef
4. Agent evaluates:
   - Hard gates: build passes, tests pass, no critical findings, AC satisfied
   - Soft gates: code reviewed, test coverage, docs updated, plan complete
   - Health indicators: commit hygiene, branch status, performance
5. Report: gate results, risk assessment, verdict
</process>

<output>
After successful execution:
- Gate evaluation table (status + evidence for each gate)
- Risk level: Low / Medium / High
- Verdict: GO or NO-GO
- Required actions (if NO-GO)
</output>

<constraints>
- Never issue GO if any hard gate fails
- Soft gate failures produce GO with warnings
- Always provide evidence for each gate
- Verdict is advisory — human makes the final call
- Same inputs must produce same verdict
</constraints>
