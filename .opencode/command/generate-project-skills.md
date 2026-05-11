---
description: Analyze the current repository and generate a small set of high-value project-specific skills.
subtask: false
---

<purpose>
Create project-specific OpenCode skills in `.opencode/skills/project/` from concrete repository evidence.

This command extends the V1 kit incrementally:
- it complements generic skills already in `.opencode/skills/*`,
- it does not change the global delivery architecture,
- it keeps generation small, concrete, and directly usable.
</purpose>

<command>
User invocation:
  /generate-project-skills [directives]

Examples:
  /generate-project-skills
  /generate-project-skills dry run
  /generate-project-skills max=2
  /generate-project-skills domain=backend max=3 focus=test,debug
  /generate-project-skills domain=frontend max=3 focus=review,build
  /generate-project-skills domain=ci refresh
</command>

<inputs>
  <item>directives='$ARGUMENTS' — optional free-text directives.</item>
  <item>Parsed flags (case-insensitive):
    - `dry run` | `preview only`: analyze and propose only, no file writes.
    - `refresh`: allow overwriting existing files in `.opencode/skills/project/**`.
    - `max=<n>`: number of skills to generate in this pass, clamped to 1..3 (default: 3).
    - `domain=<name>`: optional project domain for large repositories; kebab-case output folder, e.g. `backend`, `frontend`, `ci`, `security`, `data`.
    - `focus=<csv>`: optional priority hints among `run,test,architecture,build,review,debug,migration,ci`.
  </item>
</inputs>

<write_scope>
Allowed write paths:
- `.opencode/skills/project/README.md`
- `.opencode/skills/project/<skill-name>/SKILL.md`
- `.opencode/skills/project/<domain>/<skill-name>/SKILL.md`

No other files may be created or modified by this command.
Generated skills are not slash commands. This command MUST NOT create files
under `.opencode/command/**`, MUST NOT add command front matter, and MUST NOT
tell users to invoke a generated skill as `/<skill-name>`.
</write_scope>

<analysis_sources>
Use only repository-local, high-signal sources:
- `README*`
- `docs/**`
- `scripts/**`
- `Makefile`
- `package.json`
- `pyproject.toml`
- CI configs (`.github/workflows/**`, `.gitlab-ci.yml`, etc.)
- visible tree conventions (`src/`, `app/`, `tests/`, `services/`, `infra/`, etc.)
- project rules (`.samourai/AGENTS.md`, root `AGENTS.md`, governance files)
</analysis_sources>

<blueprint_reference>
When available, read `.samourai/blueprints/skills/` before generating skills:
- `skill.blueprint.yaml` defines the expected contract.
- `skill.template.md` provides the reusable structure.

The blueprint is a structural reference only. It does not expand write scope,
does not allow command generation, and does not override this command's
constraints.
</blueprint_reference>

<selection_rules>
Generate FEW skills with HIGH value:

1. Target count:
   - Default: 2 to 3 skills per focused generation pass.
   - Hard limit: 3 skills per pass, not 3 skills for the whole project.
   - For large repositories, run multiple focused passes by domain instead of generating a large batch at once.
   - If more than 3 candidates are useful in the current pass, rank them and recommend the next `domain=`/`focus=` pass.

2. Evidence threshold:
   - Every generated skill must cite at least 2 concrete repository anchors (files/commands/rules).
   - If evidence is weak, skip the skill.

3. Priority order:
   - Commands that unblock everyday work first (`run`, `test`, `build`, `ci`).
   - Then local architecture/review/debug conventions.

4. Anti-vagueness:
   - No generic advice detached from this repository.
   - No copied generic skills from `.opencode/skills/*`.
   - No "best practices" sections without local anchors.
</selection_rules>

<skill_requirements>
Each generated skill file MUST:
- live in `.opencode/skills/project/<kebab-name>/SKILL.md` for small repositories, or `.opencode/skills/project/<domain>/<kebab-name>/SKILL.md` when `domain=<name>` is provided
- include front matter with:
  - `name`
  - `description`
- include concrete sections:
  - `## When to use`
  - `## Inputs`
  - `## Procedure`
  - `## Validation`
  - `## Source Anchors`

Procedure requirements:
- Provide executable commands when possible.
- Reference exact local paths.
- Include known local pitfalls only when evidenced.
- Do not present the skill itself as executable. A skill may include shell
  commands for agents to run, but it is activated by agents or workflows, not
  invoked directly as a slash command.
</skill_requirements>

<process>
1. Parse directives (`dry run`, `refresh`, `max`, `domain`, `focus`).
2. Scan analysis sources and extract concrete signals:
   - run/test/build commands
   - architecture conventions and module boundaries
   - review/debug/CI local practices
3. Build candidate skill topics and rank by evidence + day-to-day value.
4. Keep top N candidates for this pass (`N = max`, default 3, never > 3 per pass).
5. Generate or update `.opencode/skills/project/README.md` index, grouped by domain when domain folders exist.
6. Generate skills under `.opencode/skills/project/<skill>/SKILL.md` or `.opencode/skills/project/<domain>/<skill>/SKILL.md`.
   - If skill exists and `refresh` is absent: keep existing file and skip overwrite.
7. Return a concise summary:
   - analyzed sources
   - selected skills + rationale
   - created/updated/skipped files
   - next recommended usage examples
</process>

<dry_run_behavior>
When `dry run` is enabled:
- Do not write files.
- Output proposed skill list, target paths, and key anchors per skill.
</dry_run_behavior>

<constraints>
- Incremental scope only; do not refactor global kit architecture.
- Do not touch delivery commands or agent roles.
- Do not generate more than 3 skills in a single pass.
- Do not treat 3 as a global project limit; recommend additional focused passes for large projects.
- Do not generate placeholder or vague content.
</constraints>
