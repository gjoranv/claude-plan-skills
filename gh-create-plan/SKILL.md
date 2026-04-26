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

**Issue body** (should rarely need updating):

1. **What and Why**: What problem is being solved and why it matters. Do not include the how/design.
2. **Prerequisites**: List only non-obvious manual steps needed before implementation. Omit this section entirely if there are no real prerequisites.

**After creating the issue body**, add comments in this order:

1. **Design comment**: The how. Technical approach, key abstractions, boundaries, trade-offs. This is where design changes are tracked.
2. **Steps comment**: Group steps under numbered headings (`### Step 1: ...`, `### Step 2: ...`). Each step contains checkboxes for its sub-tasks. Always number the top-level steps explicitly. For each step, note which other steps it depends on (e.g., "Depends on step 2"). Mark independent steps as such. This makes it easy to work on steps in parallel across conversations.
3. **Diagram comment**: Show the flow, structure, or relationships. Use the most appropriate chart type (prefer Mermaid over ASCII). Short caption (three sentences max, no "Caption:" prefix).
4. **Links comment**: Links to relevant documentation, code, resources, and related issues. Updated as new child issues, PRs, or useful references are found.

Format the issue in a clear and organized way, using headings, subheadings, bullet points, and tables as needed to enhance readability.

After creating the issue, tell the user they can use `/gh-read-plan` and `/gh-update-plan` to continue working with it.
