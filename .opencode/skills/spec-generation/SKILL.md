---
name: spec-generation
description: Use when generating or refining change specifications from requirements and user stories
---

# Specification Generation

## Overview

Generate comprehensive, implementation-agnostic change specifications from user stories, requirements, and domain context. Ensures every specification is complete, consistent, and ready to drive implementation planning.

## Objective

Produce a canonical `chg-<workItemRef>-spec.md` that serves as the single source of truth for what a change must achieve, without prescribing how.

## Inputs

- User story or ticket content (required)
- Planning session context or PM summary (required)
- System specification (`.samourai/docai/spec/**`) for context
- Change spec template (`core/templates/change-spec-template.md`)

## Outputs

- Complete specification file following the change spec template
- Traceable acceptance criteria linked to requirements
- Explicit scope boundaries (goals and non-goals)
- Risk assessment and dependency list

## Steps

1. **Gather context** — Read ticket, user story analysis, PM planning summary
2. **Review system spec** — Understand current behavior and contracts
3. **Define problem** — Articulate what is broken or missing from user perspective
4. **Set goals** — Define measurable outcomes (not tasks)
5. **Define scope** — Explicit boundaries: what changes, what does not
6. **Write acceptance criteria** — Each AC is specific, testable, non-overlapping
7. **Identify risks** — Technical, business, and integration risks
8. **List dependencies** — Prerequisites and external requirements
9. **Define DoD** — What "done" looks like beyond AC (docs, tests, review)
10. **Self-review** — Verify: Is every AC testable? Is scope unambiguous? Are risks addressed?

## Output Format

Follow `core/templates/change-spec-template.md` structure:
- Problem / Goal
- Scope / Non-goals
- Acceptance Criteria (numbered, testable)
- Definition of Done
- Risks / Edge cases
- Dependencies

## Constraints

- No implementation details (no code, no architecture decisions)
- Every AC must be independently testable
- Non-goals only where genuine ambiguity exists
- Information stated once, in one section (no duplication)

## Examples

**Good AC**: "When a user searches with an empty query, the system displays the 10 most recent products"
**Bad AC**: "Search should work well" (not testable, not specific)

## Acceptance Criteria

- Spec follows the canonical template structure
- Every user story requirement maps to at least one AC
- No AC is a duplicate or subset of another
- Risks section addresses identified edge cases
- Spec is implementation-agnostic
