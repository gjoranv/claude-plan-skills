---
name: gh-create-plan
description: Create a plan issue on GitHub. Use when planning a task, or when the user tells you to "create a github plan issue" with the repo name as argument.
allowed-tools: Bash
---

Never @mention other users in plan issues or comments.

Create a GitHub issue in repo $ARGUMENTS containing the detailed plan for the work in this conversation.
Derive a concise issue title from the conversation context. Ask the user if unclear.

The GitHub issue should be self-contained so that a new conversation can pick up the work without needing additional context.

Always include:

1. **Description**: Explain what, why, and how of the work
2. **Draw a diagram**: Show the flow, structure, or relationships. Omit unnecessary details, but show the big picture.
3. **Prerequisites**: List only non-obvious manual steps that need to be done before implementation (e.g., creating external resources, obtaining API keys, config changes). Omit this section entirely if there are no real prerequisites.
4. **Steps**: List the steps to be taken as checkboxes (`- [ ]`), with a brief explanation of each step. For complex steps, break them down into sub-steps.
5. **Links**: Include links to relevant documentation, code, resources, and related issues.

Format the issue clearly using headings, bullet points, and tables as needed.
When drawing diagrams, prefer Mermaid over ASCII. Use a separate comment for the diagram, with a short caption (three sentences max, no "Caption:" prefix).

After creating the issue, tell the user they can use `/gh-read-plan` and `/gh-update-plan` to continue working with it.
