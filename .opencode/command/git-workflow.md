---
description: Orchestrate the full git pipeline — code review, tests, conventional commit, push, PR creation — with explicit user checkpoints before each irreversible action.
agent: committer
subtask: true
---

<purpose>
Orchestrate the full git pipeline from uncommitted changes through to the created PR, with blocking user checkpoints before each irreversible operation (commit, push, PR).

Complements /commit and /pr by adding: pre-commit review via @code-reviewer, test validation, Conventional Commits message generation, and enriched PR description.

Used at the end of delivery after /review and /check, as a more structured alternative to sequential /commit + /pr.
</purpose>

<command>
User invocation:
  /git-workflow <target-branch> [flags]
Examples:
  /git-workflow main
  /git-workflow main --skip-tests
  /git-workflow main --draft-pr
  /git-workflow main --no-push
  /git-workflow develop --draft-pr --conventional
</command>

<inputs>
  <item>target-branch='$1' — Target branch for the PR (default: main). REQUIRED.</item>
  <item>flags='$ARGUMENTS' — Optional flags.</item>
</inputs>

<flags>
- `--skip-tests` : skip the test validation phase (Phase 2)
- `--draft-pr` : create the PR in draft mode
- `--no-push` : stop after the commit, do not push or create a PR
- `--conventional` : enforce Conventional Commits format (enabled by default)
- `--dry-run` : simulate without executing any git operations
</flags>

<session_state>
Persist state in `.git-workflow/state.json` to allow resumption:
```json
{
  "target_branch": "main",
  "status": "in_progress",
  "current_phase": 1,
  "completed_phases": [],
  "flags": {},
  "started_at": "ISO_TIMESTAMP"
}
```
On startup: check whether an existing session is in progress and offer to resume or restart.
</session_state>

<pipeline>

## Phase 1 — Pre-commit review

Collect git context:
```bash
git status
git diff --stat
git diff
git log --oneline -10
git branch --show-current
```

Delegate to @code-reviewer to analyse the changes:
- Security, correctness, performance, testing gaps
- Produce report in `.git-workflow/01-code-review.md`

### CHECKPOINT 1 — Approval required
```
Pre-commit review complete.
Issues found: [X critical, Y major, Z minor, W nit]

1. Approve → proceed to tests
2. Fix first → address critical/major issues
3. Pause → save state and stop
```
Do not proceed without explicit approval.

---

## Phase 2 — Tests & validation

If `--skip-tests`: document the skip, proceed to Phase 3.

Detect and run project tests (according to repo conventions):
- Unit tests
- Integration tests
- Coverage verification if available

Produce report in `.git-workflow/03-test-results.md`.

### CHECKPOINT 2 — Approval required
```
Tests complete.
Results: [X passed, Y failed, Z skipped]

1. Approve → generate commit message
2. Fix failing tests
3. Pause
```

---

## Phase 3 — Commit message (Conventional Commits)

Analyse the changes and categorise:

**Types**: `feat` | `fix` | `docs` | `style` | `refactor` | `perf` | `test` | `build` | `ci` | `chore` | `revert`

Strict format:
```
<type>(<scope>): <subject>    ← 72 chars max, imperative mood, no trailing period
<blank line>
<body>                         ← why + what (not how), 1-4 lines
<blank line>
BREAKING CHANGE: <desc>        ← if applicable
Refs: #<issue> / <workItemRef>
```

Propose in `.git-workflow/06-commit-messages.md`.

### CHECKPOINT 3 — Approval required
```
Proposed commit message:
[display full message]

1. Approve → execute git operations
2. Edit → specify changes
3. Pause
```

---

## Phase 4 — Push & branch (unless --no-push)

Pre-push checks:
- Branch name complies with repo conventions
- No conflicts with the target branch
- No sensitive data in the commits
- Protection rules respected

Display the exact planned commands:
```
Planned operations:
  git add -A
  git commit -F .git-workflow/06-commit-messages.md
  git push origin <branch> -u

1. Execute
2. Edit
3. Cancel
```

Execute only after explicit confirmation (option 1).

### CHECKPOINT 4 (if --no-push is not set)
```
Push complete. Branch: <branch>
1. Approve → create the PR
2. Pause
```

---

## Phase 5 — PR creation (unless --no-push)

Generate a complete PR description:
- Summary of changes (what + why)
- Change type
- Tests performed
- Breaking changes if applicable
- Reviewer checklist
- References to issues/tickets (extracted from the commit message)

Create via `gh pr create`:
- Title = commit subject
- Body = generated description
- Draft if `--draft-pr`
- Base = target-branch

Display the command before execution and request confirmation.

</pipeline>

<output>
Final report:
- Completed phases
- Issues found in review (counts by severity)
- Test results
- Commit SHA + message
- PR URL (if created)
- Files produced in `.git-workflow/`
</output>

<cleanup>
Files in `.git-workflow/` are temporary.
Add `.git-workflow/` to `.gitignore` if not already present.
Never commit the contents of `.git-workflow/`.
</cleanup>

<errors>
- Clean working tree (nothing to commit) → inform and STOP
- Failing tests not approved → block Phase 4
- `gh` not available → Phase 5: display the manual PR command
- Branch protection prevents push → inform, do not force
</errors>
