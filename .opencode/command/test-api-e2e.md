---
description: Run backend API E2E tests through the repository's configured test command.
agent: runner
---

<purpose>
Run this repository's Backend API E2E test suite and return a concise summary with runner log pointers.

Backend API E2E tests exercise the running backend through real HTTP/API calls. Docker or Compose may be part of a project's setup, but Docker is not required by this command unless the resolved project command uses it.
</purpose>

<command>
User invocation:
  /test-api-e2e [fast|all|<target>] [--dry-run]

Examples:
/test-api-e2e
/test-api-e2e fast
/test-api-e2e all
/test-api-e2e auth
/test-api-e2e --dry-run
</command>

<inputs>
<arguments>$ARGUMENTS</arguments>

<parsing>
- `mode` = first positional token among `fast`, `all`, or any custom target string.
- `--dry-run` = resolve and print the command without executing it.
- Unknown flags must produce `NEEDS_INPUT` with the supported usage.
  </parsing>
  </inputs>

<resolution>
Resolve the API E2E command from repository root in this order:

1. Explicit project instruction:
   - Read `.samourai/AGENTS.md` (or root `AGENTS.md` as compatibility entrypoint).
   - Read `.samourai/ai/rules/testing-strategy.md` if present.
   - Prefer a command explicitly described as API E2E, backend E2E, system API test, or HTTP E2E test.

2. `package.json` scripts, in priority order:
   - `test:api:e2e`
   - `test:e2e:api`
   - `test:e2e`
   - `e2e`

   Use the package manager implied by lockfiles:
   - `pnpm-lock.yaml` → `pnpm run <script>`
   - `yarn.lock` → `yarn <script>`
   - `bun.lockb` or `bun.lock` → `bun run <script>`
   - otherwise → `npm run <script>`

3. `Makefile` targets, in priority order:
   - `test-api-e2e`
   - `api-e2e`
   - `test-e2e`

   Use `make <target>`.

4. Python conventions:
   - If `tests/e2e/` exists: `pytest tests/e2e`
   - Else if `tests/api/` exists: `pytest tests/api`
   - Else if `test/e2e/` exists: `pytest test/e2e`
   - Else if `test/api/` exists: `pytest test/api`

5. Go conventions:
   - If packages or directories include `e2e`, `api`, or `integration` tests, prefer the narrowest discoverable `go test` command.
   - Examples: `go test ./tests/e2e/...`, `go test ./tests/api/...`, `go test ./e2e/...`.
   - Do not fall back to broad `go test ./...` unless the project explicitly documents it as the API E2E command.

If no command is discoverable, STOP with:

```text
NEEDS_INPUT: no Backend API E2E command found
Define one in `.samourai/AGENTS.md`, root `AGENTS.md`, `.samourai/ai/rules/testing-strategy.md`, package.json, Makefile, or a conventional tests/e2e or tests/api path.
Usage: /test-api-e2e [fast|all|<target>] [--dry-run]
```
</resolution>

<argument_application>
After resolving the base command:

- `fast`: append or pass through only if the resolved command explicitly supports `fast`; otherwise prefer a documented fast API E2E command if present.
- `all`: append or pass through only if the resolved command explicitly supports `all`; otherwise run the base command.
- `<target>`: append or pass through only when the resolved tool has a standard target/filter form:
  - npm/pnpm/yarn/bun scripts: append `-- <target>`
  - pytest: append `-k <target>`
  - go test: append `-run <target>`
  - make: append `<target>` only if documented by the Makefile target help or project instructions
- If applying the mode/target is ambiguous, STOP with `NEEDS_INPUT` and show the resolved base command.
  </argument_application>

<dry_run>
If `--dry-run` is present:

1. Print `DRY_RUN`.
2. Print the resolved command.
3. Print the resolution source, such as `package.json script test:api:e2e`.
4. Do not execute the command.
</dry_run>

<behavior>
- Run from repository root.
- Delegate execution to `@runner` by executing the exact resolved command.
- Save logs under `.samourai/tmpai/run-logs-runner/<YYYY-MM-DD>/` per runner rules.
- Report:
  - exact command
  - resolution source
  - exit code
  - duration
  - log path(s)
  - top failure signal, if any
- Do not modify repository files.
- Do not fix failures.
- If the command fails, recommend `/check-fix` or `@fixer` for remediation.
</behavior>

<output>
Successful run:
- Status: SUCCESS
- Command: `<resolved command>`
- Resolution source: `<source>`
- Artifacts: runner log/cmd/meta paths
- Summary: concise pass signal

Failed run:
- Status: FAILED
- Command: `<resolved command>`
- Resolution source: `<source>`
- Artifacts: runner log/cmd/meta paths
- Top failure signal: first useful error snippet
- Next step: `/check-fix` or `@fixer`
</output>
