---
#
description: Execute quality gates, fix any issues found, and create a single high-quality Conventional Commit summarizing all changes made.
agent: fixer
subtask: true
---

<purpose>
Run all project quality gates (build, test, lint), automatically fix any failures found, and commit all fixes in a single Conventional Commit.

User invocation: `/check-fix [--fast]`

Complements `/check` (which only reports) by adding automatic remediation. Delegates to `@fixer` for diagnosis and repair, then to `@committer` for the final commit.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- `--fast`: force fast quality gates first (when defined in project conventions), then proceed to full gates
- No arguments: if fast quality gates are defined by the project, run them first; otherwise run full quality gates directly
</parsing>
</inputs>

<process>
1. Discover generated project skills in `.opencode/skills/project/**/SKILL.md`; select up to 2 relevant to build/test/ci/debug; apply as local constraints
2. Read `.samourai/ai/agent/project-profile.md` when present and apply correction strategy:
   - TMA: minimal fix, regression protection, preserve existing behavior
   - Build: preserve feature intent, coverage, and release readiness
   - Guide: fix clarity, accuracy, links, and audience fit
   - Mix: classify the failure and apply the matching mode
3. Determine fast-gate strategy: if project defines fast quality gates, run them first (or force this path with `--fast`); if fast gates are not defined, continue directly to full gates
4. Run full quality gates (build, test, lint per project conventions)
5. If failures found: systematically diagnose and fix each issue
6. Re-run quality gates to verify fixes
7. Repeat until all gates pass
8. Delegate to `@committer` to create a single Conventional Commit summarizing all fixes
</process>

<output>
After successful execution:
- All quality gates passing
- Single commit with fixes (if any were needed)
- Summary: `project_skills_applied`, `project_profile_applied`, gates run, issues fixed
</output>

<constraints>
- Fix issues systematically — do not skip or ignore failures
- Minimize fix scope — smallest change that resolves the issue
- Preserve existing behavior — fixes must not introduce regressions
- Always re-verify after fixing
- Delegate commit entirely to `@committer`
</constraints>
