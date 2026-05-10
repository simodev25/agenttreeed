---
name: documentation-generation
description: Use when generating or updating system documentation, API docs, or technical guides
---

# Documentation Generation

## Overview

Generate clear, accurate, and maintainable technical documentation. Covers system specifications, API documentation, architecture guides, and operational runbooks. Documentation is always derived from code and specifications — never invented.

## Objective

Produce documentation that is accurate (matches the code), complete (covers all public interfaces), and useful (answers developer questions).

## Inputs

- Source code or module to document
- Existing documentation to update (if any)
- Documentation template (from `core/templates/`)
- Target audience: developers / operators / end-users

## Outputs

- Generated or updated documentation files
- Coverage report (what is documented vs what needs documentation)

## Steps

1. **Audit existing docs** — What exists, what is outdated, what is missing
2. **Analyze source** — Read code to understand behavior, interfaces, contracts
3. **Cross-reference** — Verify existing docs against current code
4. **Generate/update** — Write documentation following templates and conventions
5. **Verify accuracy** — Every statement matches current code behavior
6. **Self-review** — Is it clear? Complete? Would a new developer understand it?

## Output Format

Follow project documentation conventions and templates:
- Feature specs → `core/templates/feature-spec-template.md`
- Test specs → `core/templates/test-spec-template.md`
- System docs → `.samourai/docai/spec/**`

## Constraints

- Never invent behavior — document only what code actually does
- Use existing templates and naming conventions
- Mark uncertain areas with TODO rather than guessing
- Keep documentation DRY — link rather than duplicate

## Acceptance Criteria

- Documentation matches current code behavior
- All public interfaces are documented
- Examples are runnable and correct
- No orphan references to deleted/renamed elements
