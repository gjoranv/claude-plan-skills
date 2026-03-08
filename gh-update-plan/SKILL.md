---
name: gh-update-plan
description: Update a GitHub plan issue with progress. Use when planning a task, or when the user tells you to "update the github plan issue".
allowed-tools: Bash, Read, Edit
---

You must actually run `gh` commands to update the issue; do not just describe what you would do. Do not ask for permission to update comments — it is expected.

**Workflow for editing issue bodies and comments:**
1. Create a unique temp directory: `mktemp -d /tmp/plan-update-XXXXX`
2. Fetch content from GitHub and save to files in that directory (e.g. `body.md`, `comment-COMMENTID.md`)
3. Use the Read and Edit tools to modify the temp files
4. Upload using `--input` with `jq` to properly JSON-encode the content:

- Edit issue body: `gh api repos/OWNER/REPO/issues/NUMBER -X PATCH --input <(jq -Rs '{body: .}' <tempdir>/body.md)`
- Create comment: `gh api repos/OWNER/REPO/issues/NUMBER/comments --input <(jq -Rs '{body: .}' <tempdir>/comment.md)`
- Edit comment: `gh api repos/OWNER/REPO/issues/comments/COMMENT_ID -X PATCH --input <(jq -Rs '{body: .}' <tempdir>/comment-COMMENTID.md)`

Never embed content directly in shell arguments or use `-f body=@file` (it uploads the literal string, not the file contents).

Always fetch the latest from GitHub before making changes. Do not rely on previously fetched copies that may be stale.

Never @mention other users in plan issues or comments.

Update the GitHub issue $ARGUMENTS (issue URL or `owner/repo#number`). If no argument is given, use the issue referenced earlier in this conversation. If no issue can be determined, ask the user.

1. Verify that it contains the detailed plan for the work in this conversation. If not, ask the user to verify that the correct issue was given.
2. **Conformance check**: Ensure the issue follows the standard plan format. If not, lightly restructure:
   - Convert plain step lists to checkboxes (`- [ ]` / `- [x]`)
   - Add missing section headings (Description, Steps, Links)
   - If there is no diagram and the work would benefit from one, add it in a separate comment (Mermaid preferred, three sentence max caption, no "Caption:" prefix)
3. Check off completed steps (`- [x]`) in the issue body based on the work done in this conversation.
4. If the issue body or comments contain a diagram, check if it is still accurate. If not, update it.
5. If steps need rewording or new steps are needed, update them directly in the body.
6. If the issue contains links to relevant documentation or related issues, check if they are still relevant.
7. Add or update a **Commits** table in a separate comment with all git commits related to this work. Each row should include the git ref (short SHA), description, and date. If a commits comment already exists, edit it rather than creating a new one. Include links to related PRs.
8. Add a comment summarizing what was done in this session: new insights, changes in understanding, and any remaining open questions.
