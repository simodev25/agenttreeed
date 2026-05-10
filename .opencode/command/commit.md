---
#
description: Delegate a single Conventional Commit.
agent: committer
subtask: true
---

<purpose>Trigger the @committer agent to create exactly one Conventional Commit.</purpose>

<inputs>
  <optional>
    <intent>$ARGUMENTS</intent>
  </optional>
</inputs>

<instructions>
  <rule>Invoke `@committer` now.</rule>
  <rule>Do not restate its workflow; do not add extra commentary.</rule>
  <rule>If blocked, surface the agent's message without alteration.</rule>
  <rule>If successful, return exactly the agent's output.</rule>
</instructions>

<intent>
$ARGUMENTS
</intent>
