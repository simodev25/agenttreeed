---
name: code-analysis
description: Use when analyzing code for quality, patterns, dependencies, and improvement opportunities
---

# Code Analysis

## Overview

Perform structured code analysis to assess quality, identify patterns, map dependencies, and surface improvement opportunities. Provides actionable insights without modifying code.

## Objective

Produce a comprehensive code analysis report covering quality metrics, architectural patterns, dependency mapping, and prioritized improvement recommendations.

## Inputs

- Target: file path, directory, module, or component to analyze
- Focus area (optional): "security", "performance", "maintainability", "dependencies"
- Baseline metrics (optional): previous analysis for comparison

## Outputs

- Code quality assessment with metrics
- Pattern and anti-pattern identification
- Dependency map (internal and external)
- Prioritized improvement recommendations

## Steps

1. **Scope definition** — Identify files, modules, and boundaries to analyze
2. **Static analysis** — Measure complexity, coupling, cohesion, duplication
3. **Pattern recognition** — Identify design patterns and anti-patterns
4. **Dependency mapping** — Internal dependencies and external library usage
5. **Security scan** — Hardcoded secrets, injection vectors, unsafe operations
6. **Performance review** — Algorithm complexity, I/O patterns, resource management
7. **Synthesize findings** — Prioritize by impact and effort
8. **Generate report** — Structured output with actionable recommendations

## Output Format

```markdown
## Code Analysis Report

**Target**: <scope>
**Date**: <ISO date>
**Files analyzed**: N

### Quality Metrics
| Metric | Value | Rating |
|--------|-------|--------|
| Avg complexity | X | ⚠️ Medium |
| Duplication | X% | ✅ Low |
| Test coverage | X% | ❌ Below threshold |

### Patterns Found
- ✅ <good pattern>: <where and why it works>
- ⚠️ <anti-pattern>: <where and impact>

### Recommendations (prioritized)
1. [HIGH] <recommendation with rationale>
2. [MEDIUM] <recommendation>
```

## Constraints

- Read-only: never modify analyzed code
- Report only actionable findings with concrete locations
- Distinguish between style preferences and genuine quality issues
- Consider project profile when assessing patterns

## Acceptance Criteria

- All files in scope are analyzed
- Findings include file paths and line numbers
- Recommendations are prioritized by impact
- Security findings are always flagged regardless of focus area
