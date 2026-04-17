---
name: gh-create-plan
description: Create a plan issue on GitHub. Use when planning a task, or when the user tells you to "create a github plan issue" with the repo name as argument.
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Never @mention other users in plan issues or comments.

Create a GitHub issue in repo $ARGUMENTS containing the detailed plan for the work in this conversation.
Derive a concise issue title from the conversation context. Ask the user if unclear.

The GitHub issue should be self-contained so that a new conversation can pick up the work without needing additional context. Omit raw exploration and back-and-forth; only include the conclusions.

Think as a software architect first. Before writing steps, consider: What are the key abstractions? Where should boundaries be? What's the simplest design that solves the problem? What will be hard to change later? Let these decisions shape the plan structure.

Before creating the plan, ask the user if there are related repos with similar implementations that should inform the approach. If so, review them to understand how the problem was solved there, and incorporate relevant patterns into the plan.

Always include:

1. **Description**: Explain what, why, and how of the work
2. **Draw a diagram**: Show the flow, structure, or relationships. Omit unnecessary details, but show the big picture.
3. **Prerequisites**: List only non-obvious manual steps that need to be done before implementation (e.g., creating external resources, obtaining API keys, config changes). Do not list obvious things like repo access or tool installation. Omit this section entirely if there are no real prerequisites.
4. **Steps**: Group steps under numbered headings (`### Step 1: ...`, `### Step 2: ...`). Each step contains checkboxes for its sub-tasks. Always number the top-level steps explicitly. For each step, note which other steps it depends on (e.g., "Depends on step 2"). Mark independent steps as such. This makes it easy to work on steps in parallel across conversations.
5. **Links**: Include links to relevant documentation, code, resources, and related issues.

Format the issue in a clear and organized way, using headings, subheadings, bullet points, and tables as needed to enhance readability.
When drawing diagrams, use the most appropriate chart type (prefer Mermaid over ASCII) to show the flow, structure, or relationships. Use a separate comment for the diagram, with a short caption (three sentences max, no "Caption:" prefix).

After creating the issue, tell the user they can use `/gh-read-plan` and `/gh-update-plan` to continue working with it.
