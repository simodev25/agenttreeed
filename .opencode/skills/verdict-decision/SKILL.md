---
name: verdict-decision
description: Use when evaluating change readiness and producing a GO/NO-GO decision based on quality gates
---

# Verdict Decision

## Overview

Evaluate change readiness by aggregating quality signals across the development lifecycle. Produces a definitive GO/NO-GO verdict based on hard gates (must pass) and soft gates (advisory).

## Objective

Provide an evidence-based, deterministic verdict on whether a change is ready for human review and merge.

## Inputs

- workItemRef to locate change artifacts (required)
- PM notes with phase completion status
- Quality gate results (build, tests, lint)
- Review status and findings

## Outputs

- Structured verdict report with gate evaluations
- Risk assessment
- Required actions (if NO-GO)

## Steps

1. **Collect evidence** — Read PM notes, review reports, quality gate logs
2. **Evaluate hard gates** — Build, tests, critical findings, spec compliance
3. **Evaluate soft gates** — Code review, test coverage, documentation, plan completion
4. **Assess risk** — Aggregate gate results into risk level
5. **Render verdict** — GO (all hard gates pass) or NO-GO (any hard gate fails)
6. **List actions** — Required remediation for NO-GO verdict

## Output Format

See verdict agent output format (gate table + risk assessment + verdict).

## Constraints

- Never issue GO if any hard gate fails
- Soft gate failures produce GO with warnings
- Same inputs must produce same verdict (deterministic)
- Verdict is advisory — human makes the final call

## Acceptance Criteria

- All hard gates are evaluated with evidence
- Verdict is clearly stated (GO or NO-GO)
- NO-GO includes specific required actions
- Risk level is justified by gate results
