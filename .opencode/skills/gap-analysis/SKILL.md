---
name: gap-analysis
description: Use when comparing artifacts across the development lifecycle to identify missing coverage and inconsistencies
---

# Gap Analysis

## Overview

Systematically compare development artifacts (user stories, specifications, plans, tests, code) to identify gaps, inconsistencies, and missing coverage. Ensures traceability across the entire development lifecycle.

## Objective

Produce a gap report that identifies every disconnect between development artifacts, with severity, location, and remediation recommendations.

## Inputs

- workItemRef to locate change artifacts (required)
- Scope: which comparison dimensions to analyze (optional, defaults to all)
- Artifacts in the change folder: spec, plan, test plan, code changes

## Outputs

- Gap report with coverage matrix
- Prioritized list of gaps with remediation actions
- Coverage percentage across artifact dimensions

## Steps

1. **Collect artifacts** — Locate all change artifacts via discovery rules
2. **Extract requirements** — Parse AC from spec, tasks from plan, cases from test plan
3. **Map traceability** — Cross-reference: AC ↔ plan tasks ↔ test cases ↔ code
4. **Identify gaps** — Find requirements without implementation, tests without AC, etc.
5. **Assess severity** — Critical (missing core functionality) → Minor (documentation gap)
6. **Build coverage matrix** — Visual representation of traceability
7. **Generate report** — Structured output with findings and remediation

## Output Format

See gap-analysis agent output format (coverage matrix + gap list + verdict).

## Constraints

- Read all artifacts before reporting gaps
- Distinguish between intentional exclusions (non-goals) and true gaps
- Be precise: reference specific AC numbers, plan task IDs, test case IDs

## Acceptance Criteria

- Every AC in spec appears in coverage matrix
- Gaps are actionable (clear remediation path)
- Severity ratings are consistent and justified
- Coverage percentage is mathematically correct
