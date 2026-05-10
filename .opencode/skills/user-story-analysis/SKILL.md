---
name: user-story-analysis
description: Use when analyzing user stories for completeness, consistency, and readiness before specification
---

# User Story Analysis

## Overview

Systematically analyze user stories to ensure they are complete, consistent, testable, and ready for specification. Identifies gaps, ambiguities, and missing acceptance criteria before development begins.

## Objective

Transform raw or incomplete user stories into well-structured, actionable requirements with clear acceptance criteria, identified edge cases, and explicit scope boundaries.

## Inputs

- User story text (title, description, acceptance criteria if any)
- Related tickets or epic context (optional)
- System specification for cross-referencing (optional: `.samourai/docai/spec/**`)

## Outputs

- Structured analysis report with completeness score
- List of missing or ambiguous elements
- Suggested acceptance criteria (if missing)
- Questions for the product owner
- Risk and dependency assessment

## Steps

1. **Parse the user story** — Extract: role, goal, benefit (As a... I want... So that...)
2. **Assess completeness** — Check for: problem statement, user perspective, AC, scope, dependencies
3. **Evaluate acceptance criteria** — Are they specific, measurable, achievable, relevant, testable (SMART)?
4. **Cross-reference** — Check against system spec and related tickets for contradictions
5. **Identify edge cases** — What happens on error? Empty input? Concurrent access? Boundary values?
6. **Extract non-functional requirements** — Performance, security, accessibility implications
7. **Generate questions** — Specific, actionable questions for ambiguous or missing elements
8. **Produce report** — Structured output with score, findings, and recommendations

## Output Format

```markdown
## User Story Analysis

**Story**: <reference> — <title>
**Completeness**: X/10

### Structure
- Role: ✅ / ❌ (who)
- Goal: ✅ / ❌ (what)  
- Benefit: ✅ / ❌ (why)

### Acceptance Criteria Assessment
| AC # | Text | Testable | Complete | Issues |
|------|------|----------|----------|--------|
| 1 | ... | ✅ | ⚠️ | Missing boundary |

### Missing Elements
1. <what is missing and why it matters>

### Questions for Product Owner
1. <specific question>

### Suggested Improvements
1. <concrete suggestion>

### Verdict
READY / NEEDS REFINEMENT / BLOCKED
```

## Constraints

- Never invent requirements — only surface what is missing or ambiguous
- Always cross-reference against existing system specification when available
- Questions must be specific enough for a product owner to answer in one sentence
- Do not suggest implementation approaches — stay requirement-focused

## Examples

**Input**: "As a user, I want to search products"
**Output flags**: Missing benefit (why?), no acceptance criteria, no error handling, no performance requirements, ambiguous scope (what fields? full-text? filters?)

## Acceptance Criteria

- Every analyzed story has a completeness score
- All missing SMART criteria are identified
- Questions are specific and actionable (not "please clarify")
- Cross-reference with system spec is performed when available
