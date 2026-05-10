---
description: Scaffold Samourai artifacts for an existing project
agent: bootstrapper
subtask: false
---

<purpose>
Entry point for the Samourai bootstrap workflow. Delegates to `@bootstrapper` agent for multi-session project onboarding.

User invocation:
  /bootstrap [<project-name>]

Examples:
  /bootstrap
    → Start or resume bootstrap workflow; auto-detect project name from repo.

  /bootstrap my-billing-service
    → Start or resume bootstrap with "my-billing-service" as the project name hint.
</purpose>

<inputs>
- projectName='$1': string — OPTIONAL. Project name hint passed to `@bootstrapper`.
- allArguments='$ARGUMENTS': string — full argument string for additional context.
</inputs>

<process>
1. Pass project-name hint (if provided) to `@bootstrapper` agent.
2. Tell `@bootstrapper` to use `.samourai/blueprints/project-bootstrap/` as
   the structural reference for generated project instructions when available.
3. `@bootstrapper` checks for existing state at `.samourai/ai/local/bootstrapper-context.yaml`.
4. If state exists: resume from last phase.
5. If no state: start fresh with repo scan.
6. During interview, ask language selection first (French or English), lock it in state, then continue.
7. Follow the multi-session workflow:
   scan → assess → interview → mcp-setup → draft → review → write.
8. MCP setup phase: detect available tools, ask targeted questions,
   enable the relevant MCPs in `.opencode/opencode.jsonc`.
</process>

<notes>
- This command uses `subtask: false` because the bootstrap workflow is multi-session and needs the main conversation context.
- The `@bootstrapper` agent manages its own persistent state across sessions.
- For the manual (non-automated) adoption path, see `.samourai/core/governance/conventions/onboarding-existing-project.md`.
- Blueprints are references, not additional write permissions. The bootstrapper
  must still obey its own write allowlist.
</notes>
