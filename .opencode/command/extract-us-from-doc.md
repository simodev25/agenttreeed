---
#
description: Extract structured user stories from business documents
agent: jira-analysis
subtask: true
---

<purpose>
Extract structured user stories from unstructured business documents (requirements documents, meeting notes, product briefs, specifications).

User invocation: `/extract-us-from-doc <file_path_or_pasted_content>`

Transforms prose requirements into well-formed user stories with acceptance criteria, traceability to source sections, and flagged ambiguities.
</purpose>

<inputs>
<arguments>$ARGUMENTS</arguments>
<parsing>
- First argument: file path to document or indicator to use pasted content from conversation
- `--domain <context>`: optional domain context
- `--backlog <workItemRef_prefix>`: optional backlog to check for duplicates
- If no input found:
  ```
  NEEDS_INPUT: document content required
  Usage: /extract-us-from-doc <file_path>
  Or paste document content in the conversation and run: /extract-us-from-doc
  ```
</parsing>
</inputs>

<process>
1. Parse input from $ARGUMENTS or conversation context
2. Load the `us-from-document` skill
3. Parse document structure (sections, headings, bullet points)
4. Identify explicit and implicit requirements
5. Group related requirements into user stories
6. Structure each story: As a [role], I want [goal], so that [benefit]
7. Define testable acceptance criteria for each story
8. Cross-reference with existing backlog if provided
9. Flag ambiguities and contradictions with specific questions
10. Generate output with traceability to source sections
</process>

<output>
After successful execution:
- Number of stories extracted
- Structured user stories with AC
- Traceability: source section → user story
- Ambiguities and questions list
- Suggested priority for each story
</output>

<constraints>
- Never invent requirements not present in the source
- Mark inferred requirements explicitly
- Preserve original terminology from the source
- Flag contradictions between document sections
</constraints>
