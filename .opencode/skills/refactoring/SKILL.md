---
name: refactoring
description: Use when planning or executing code refactoring to improve quality while preserving behavior
---

# Refactoring

## Overview

Plan and execute safe, incremental code refactoring. Every transformation preserves existing behavior, verified by tests. Follows the principle: make the change easy, then make the easy change.

## Objective

Improve code quality (readability, maintainability, performance) through systematic, test-verified transformations without changing external behavior.

## Inputs

- Target code (file path, module, or component)
- Refactoring goal (optional): "reduce duplication", "simplify", "extract module"
- Constraints (optional): patterns to preserve, APIs to keep stable

## Outputs

- Refactoring plan with ordered transformations
- Before/after comparison
- Test verification results for each step

## Steps

1. **Baseline** — Run all relevant tests; they must pass before starting
2. **Analyze** — Identify code smells and improvement opportunities
3. **Plan** — Order transformations from lowest to highest risk
4. **Execute** — Apply one transformation at a time
5. **Verify** — Run tests after each transformation
6. **Report** — Summarize changes, metrics improvement, risk assessment

## Output Format

```markdown
## Refactoring Plan

**Target**: <file/module>
**Goal**: <what improves>
**Baseline tests**: ✅ All passing (N/N)

### Transformations
1. [LOW RISK] Extract method `X` from `Y` — reduces method length from 45→18 lines
2. [LOW RISK] Remove duplicate logic in `Z` — 3 instances → 1 shared function
3. [MEDIUM RISK] Introduce interface for `W` — decouples module dependencies
```

## Constraints

- NEVER refactor without passing tests as baseline
- One transformation per commit (atomic, reversible)
- If no tests exist, write characterization tests FIRST
- Preserve public API contracts unless explicitly changing them
- When in doubt, prefer the smaller, safer refactoring

## Acceptance Criteria

- All tests pass before AND after refactoring
- Each transformation is atomic and independently reversible
- No new features or behavior changes introduced
- Code metrics improve measurably
