---
#
description: Analyze user stories for completeness, consistency, and development readiness
agent: jira-analysis
subtask: true
---

<purpose>
Analyze user stories or tickets to assess completeness, identify gaps, extract structured requirements, and determine readiness for specification.

User invocation: `/analyze-user-stories <workItemRef>`

Produces a structured analysis report that surfaces missing acceptance criteria, ambiguities, edge cases, and questions for the product owner. Feeds into `/write-spec`.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `workItemRef` = first token matching pattern `<PREFIX>-<number>` (e.g., `PDEV-123`, `GH-456`)
- `--depth <quick|deep>`: analysis depth (default: deep)
- If no valid `workItemRef` found, output NEEDS_INPUT:
  ```
  NEEDS_INPUT: workItemRef required
  Usage: /analyze-user-stories <workItemRef>
  Example: /analyze-user-stories PDEV-123
  ```
</parsing>
</inputs>

<process>
1. Parse `workItemRef` from $ARGUMENTS
2. Read ticket content from tracker (via MCP or context)
3. Load system specification (`.samourai/docai/spec/**`) for cross-referencing
4. Load the `user-story-analysis` skill
5. Apply analysis framework:
   - Parse story structure (role/goal/benefit)
   - Assess completeness (problem, user perspective, AC, scope, dependencies)
   - Evaluate each AC for SMART criteria
   - Cross-reference with system spec for contradictions
   - Identify edge cases and non-functional requirements
6. Generate structured report
7. Report: analysis summary, questions, readiness verdict
</process>

<output>
After successful execution:
- Completeness score (X/10)
- List of missing or ambiguous elements
- Specific questions for product owner
- Readiness verdict: READY / NEEDS REFINEMENT / BLOCKED
- Recommendation: next command to run (e.g., `/write-spec <workItemRef>`)
</output>

<constraints>
- Never invent requirements — only surface what is missing
- Questions must be specific and actionable
- Do not suggest implementation approaches
- Cross-reference with system spec is mandatory when available
</constraints>
