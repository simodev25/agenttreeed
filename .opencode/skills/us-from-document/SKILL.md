---
name: us-from-document
description: Use when extracting user stories from business documents (Word, PDF, specs, meeting notes)
---

# User Stories from Document

## Overview

Extract structured user stories from unstructured business documents. Transforms prose requirements, meeting notes, product briefs, or legacy specifications into well-formed user stories with acceptance criteria.

## Objective

Produce a set of actionable user stories from a source document, each with clear role, goal, benefit, and testable acceptance criteria.

## Inputs

- Source document content (text, markdown, or pasted content from Word/PDF)
- Domain context (optional): product area, target users, technical constraints
- Existing backlog (optional): to avoid duplicates

## Outputs

- List of structured user stories in standard format
- Traceability: which document section → which user story
- Questions and ambiguities requiring human clarification

## Steps

1. **Parse document** — Identify sections, requirements, and stakeholder intent
2. **Extract requirements** — Find explicit and implicit requirements
3. **Group by capability** — Cluster related requirements into user stories
4. **Structure each story** — As a [role], I want [goal], so that [benefit]
5. **Define acceptance criteria** — Testable conditions for each story
6. **Cross-reference** — Check for duplicates against existing backlog
7. **Flag ambiguities** — Mark unclear requirements with specific questions
8. **Produce output** — Structured story list with traceability

## Output Format

```markdown
## Extracted User Stories

**Source**: <document name/reference>
**Stories extracted**: N
**Questions pending**: M

### US-1: <title>
**As a** <role>, **I want** <goal>, **so that** <benefit>
**Source**: Section X, paragraph Y
**Acceptance Criteria**:
- [ ] AC-1: <testable condition>
- [ ] AC-2: <testable condition>
**Priority**: High / Medium / Low (inferred from document emphasis)

### US-2: ...

### Ambiguities
1. Section X mentions "fast response" — what is the target latency?
2. ...
```

## Constraints

- Never invent requirements not present in the source document
- Mark inferred requirements explicitly as "inferred from..."
- Preserve original terminology from the source document
- Flag contradictions between different document sections

## Acceptance Criteria

- Every identifiable requirement in the document maps to a user story
- Each story follows the standard format (role/goal/benefit)
- Each story has at least one testable acceptance criterion
- Traceability links every story to its source section
