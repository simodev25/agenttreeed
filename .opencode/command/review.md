---
#
description: Review change vs spec, plan, code quality heuristics, and repo rules; append remediation phase if needed.
agent: reviewer
subtask: true
---

<purpose>
Invoke the unified reviewer in local mode. Validates the change diff against specification, implementation plan, code quality heuristics (security, performance, correctness, etc.), and repository rules. If gaps found, appends a remediation phase to the plan.
</purpose>

<command>
User invocation:
  /review <workItemRef> [directives...]
Examples:
  /review PDEV-123
  /review GH-456 dry run
  /review PDEV-123 base=staging
  /review GH-456 head=feat/GH-456/new-endpoint base=production preview only
  /review PDEV-123 no commit
</command>

<inputs>
  <item>workItemRef='$1' — Tracker reference (e.g., `PDEV-123`, `GH-456`). REQUIRED.</item>
  <item>directives: remainder free-text. OPTIONAL.</item>
  <item>Derived flags: baseBranch, headRef, commit (default true), dryRun (default false).</item>
</inputs>

<project_skills_activation>
Before analyzing the change:

1. Discover generated project skills in `.opencode/skills/project/**/SKILL.md`.
2. Select up to 2 skills most relevant to review context (review rules, architecture conventions, sensitive zones, quality expectations).
3. Apply selected skills as repository-local review constraints.
4. If no relevant project skill is found, continue with generic review framework only.
</project_skills_activation>

<discovery_rules>
<rule>Locate change folder: search `.samourai/docai/changes/**/*--<workItemRef>--*/`</rule>
<rule>If not found, search: `.samourai/docai/changes/**/chg-<workItemRef>-spec.md`</rule>
<rule>Spec file: `chg-<workItemRef>-spec.md`; derive slug & change.type from frontmatter.</rule>
<rule>Plan file: `chg-<workItemRef>-plan.md`</rule>
<rule>Folder pattern: `.samourai/docai/changes/YYYY-MM/YYYY-MM-DD--<workItemRef>--<slug>/`</rule>
<rule>Abort with clear error if spec OR plan missing.</rule>
</discovery_rules>

<branch_resolution>
<rule>changeBranch = `<change.type>/<workItemRef>/<slug>`</rule>
<rule>headRef: directives override, else try changeBranch, fallback: current HEAD.</rule>
<rule>baseBranch: directives override, else `main`, fallback: `master`.</rule>
<rule>Compute merge-base and gather symmetric diff `baseBranch...headRef`.</rule>
</branch_resolution>

<directive_parsing>
Directives (case-insensitive):

- Base branch: `base=<branch>` | `base branch <branch>` | `compare vs <branch>`
- Head ref: `head=<ref>` | `head ref <ref>` | `branch <ref>`
- Disable commit: `commit=false` | `no commit`
- Dry run: `dry run` | `preview only`
  Unrecognized tokens ignored.
  </directive_parsing>

<pre_flight>

1. Validate workItemRef format (uppercase prefix + hyphen + digits).
2. Resolve spec; extract change.type & slug.
3. Resolve plan; parse phases & existing remediation.
4. Load repository rules (`.samourai/AGENTS.md`, root `AGENTS.md`, `.samourai/ai/rules/**`).
5. Resolve branches & compute diff metadata.
6. If dryRun: prepare preview but do NOT write.
   </pre_flight>

<review_method>
The reviewer agent applies its full review framework:

**Spec/plan compliance (local mode):**
- Scope compliance: changed files align with spec capabilities
- Plan alignment: all tasks done, acceptance criteria have evidence
- Plan task audit: OPEN_TASKS, DONE_BUT_UNCHECKED, CHECKED_BUT_MISSING
- Out-of-scope detection: changes to files not in plan

**Code quality heuristics (both modes):**
- Full built-in heuristic framework: correctness, security, performance, reliability, API compat, testing gaps, documentation, dependencies
- Repository-local rules from `.samourai/ai/agent/code-review-instructions.md` and `.samourai/ai/rules/`

**Ticket context (when available):**
- Acceptance criteria verification against implementation
- Linked issue traversal for additional constraints and decisions

The reviewer loads all available context — spec, plan, ticket, repo rules, heuristics — and applies them holistically. Do not duplicate heuristic definitions here; they live in the reviewer agent prompt.
When available, pass `.samourai/blueprints/code-review/` as structural guidance
for checklist and review output shape. The blueprint does not change publish
permissions or write scope.
</review_method>

<findings_format>
`[severity: major|minor|nit] <file>[:line] — <description>; fix: <action>`
</findings_format>

<remediation_phase>
If findings exist, append new phase to plan:

```
### Phase X: Code Review Remediation

- Goal: Address code review findings.
- Tasks:
  - [ ] <precise fix per finding>
- Acceptance criteria:
  - Must: All fixes implemented and validated.
  - Must: Updated tests pass.
- Files and modules: <paths>
- Completion signal: docs(plan): remediate review findings for <workItemRef>
```

Rules:

- X = max existing phase + 1.
- Do NOT modify earlier phases.
- Append revision log entry.
  </remediation_phase>

<commit_rules>

- If commit=true and not dryRun: stage plan file, create Conventional Commit via `/commit`.
- If commit=false: write only.
- Dry run: no write; include preview in output.
  </commit_rules>

<output>
1. Review Summary: pass/fail; changed files count; key themes.
2. Findings: one line per item.
3. Plan Update: "Added Phase X" OR "No plan changes required." OR dry-run preview.
4. Branch info: base, head, changeBranch.
5. Project skills applied: selected names (or none).
6. Next action: suggest `/run-plan <workItemRef>` if remediation added.
</output>

<constraints>
- Only modify plan file; never touch spec or code.
- Never include `.samourai/docai/changes/current` in paths.
- Idempotent: re-running yields no duplicate tasks.
- No external network calls.
</constraints>

<errors>
- Missing spec or plan: abort with message.
- Unable to derive slug or change.type: abort.
- Branch resolution failure: fallback to HEAD; note in summary.
- Empty diff: advisory; no remediation unless plan gaps found.
</errors>
