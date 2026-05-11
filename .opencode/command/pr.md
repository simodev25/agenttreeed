---
#
description: Create/update PR/MR title and description.
agent: pr-manager
subtask: true
---

<purpose>Trigger the @pr-manager agent to create/update the PR/MR for the current branch (writes `.samourai/tmpai/pr/<branch>/description.md`).</purpose>

<inputs>
  <optional>
    <args>$ARGUMENTS</args>
  </optional>
</inputs>

<instructions>
  <rule>Invoke `@pr-manager` now with the provided args.</rule>
  <rule>Tell `@pr-manager` to use `.samourai/blueprints/github/` as PR structure guidance when available.</rule>
  <rule>Do not restate its workflow; do not add extra commentary.</rule>
  <rule>If blocked, surface the agent's message without alteration.</rule>
  <rule>If successful, return exactly the agent's output.</rule>
</instructions>

<user_input>$ARGUMENTS</user_input>
