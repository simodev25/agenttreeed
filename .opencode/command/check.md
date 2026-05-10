---
#
description: Run this repo's quality gates script and summarize results via the run-logs-runner.
agent: runner
---

<purpose>
Run the repository's configured quality gates command and return a concise, high-signal summary with log pointers.

This command is intended for humans to invoke directly.
Agents should preferentially call `@runner` directly for execution/log-heavy tasks.
</purpose>

<command>
User invocation:
  /check [fast|slow|all|<gate>...] [--skip-autofix] [--dry-run]

Examples:
/check # default (usually all)
/check fast
/check slow
/check lint test
</command>

<resolution>
Determine which quality gates command to run:

1. Read `.samourai/AGENTS.md` (or root `AGENTS.md` as compatibility entrypoint) and look for an explicit quality gates runner instruction.
   - If `.samourai/AGENTS.md` or the root `AGENTS.md` entrypoint includes a command like `./scripts/quality-gates.sh` (preferred) or any referenced path/command for quality gates, use that.
   - If multiple are present, prefer the most explicit "Run all quality gates" instruction.

2. Default fallback if no instruction found:
   - `./scripts/quality-gates.sh`

3. Pass through user-provided arguments (fast/slow/all/<gate>...) as-is to the resolved command.

4. Always run from repository root.
   </resolution>

<project_skills_activation>
Before running quality gates:

1. Discover generated project skills in `.opencode/skills/project/**/SKILL.md`.
2. Select up to 2 skills most relevant to quality-gate context (build/test/ci/debug).
3. Apply selected skills as local execution constraints (command choice, expected checks, known pitfalls).
4. If no relevant project skill is found, continue with default quality-gate resolution.
</project_skills_activation>

<behavior>
- Delegate actual execution to `@runner` (this command uses it as its agent).
- Ensure logs are saved under `.samourai/tmpai/run-logs-runner/<YYYY-MM-DD>/` and that output includes:
  - exact command
  - exit code
  - duration
  - log path(s)
  - `project_skills_applied` (selected names or empty list)
  - top error snippets and tail excerpts
- If quality gates fail, prominently surface:
  - which gate(s) failed
  - pointers mentioned by `quality-gates.sh` (e.g., `.samourai/tmpai/playwright-report`, `.samourai/tmpai/playwright-report/ai-failures.jsonl`)
</behavior>

<notes>
- Do not attempt fixes; this command is run-only.
- For fixing failures, use `/check-fix` (@fixer) or invoke `@fixer` directly.
</notes>
