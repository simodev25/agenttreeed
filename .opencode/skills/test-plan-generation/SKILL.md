---
name: test-plan-generation
description: Use when generating test plans with traceability to acceptance criteria and specifications
---

# Test Plan Generation

## Overview

Generate comprehensive test plans that ensure every acceptance criterion has corresponding test coverage. Establishes traceability from requirements through test cases to verify complete coverage.

## Objective

Produce a `chg-<workItemRef>-test-plan.md` with test strategy, test cases matrix, and full traceability to specification acceptance criteria.

## Inputs

- Change specification (`chg-<workItemRef>-spec.md`) — required
- System test strategy (`.samourai/core/governance/conventions/testing-strategy.md`) — if available
- Test plan template (`core/templates/test-plan-template.md`)
- Existing test infrastructure and patterns in the codebase

## Outputs

- Complete test plan with strategy, cases, and traceability matrix
- Coverage analysis (which AC are covered, which need attention)
- Data setup and environment requirements

## Steps

1. **Read specification** — Extract all acceptance criteria and edge cases
2. **Review test strategy** — Align with project testing conventions
3. **Determine test levels** — Unit, integration, e2e for each AC
4. **Design test cases** — Positive, negative, boundary for each AC
5. **Build traceability matrix** — AC → test cases mapping
6. **Identify data requirements** — Test fixtures, mocks, seeds
7. **Define manual verification** — What cannot be automated
8. **Self-review** — Every AC has ≥1 test case; every test traces to an AC

## Output Format

Follow `core/templates/test-plan-template.md`:
- Test Strategy (levels, tools, approach)
- Test Cases Matrix (AC → test cases with expected results)
- Traceability Matrix (AC ↔ test case cross-reference)
- Data Setup Notes
- Manual Verification Checklist

## Constraints

- Every AC must have at least one test case
- Test cases must include both positive and negative scenarios
- Do not write test code — only describe test cases
- Mark any AC that cannot be tested with current infrastructure as TODO

## Examples

**AC**: "When cart is empty, checkout button is disabled"
**Test cases**:
- TC-1: Verify checkout button is disabled when cart has 0 items (positive)
- TC-2: Verify checkout button becomes enabled when item is added (state transition)
- TC-3: Verify checkout button returns to disabled when last item is removed (regression)

## Acceptance Criteria

- 100% AC coverage in traceability matrix (or explicit TODO with reason)
- Every test case has expected result defined
- Negative test cases exist for each error scenario in spec
- Test strategy aligns with project conventions
