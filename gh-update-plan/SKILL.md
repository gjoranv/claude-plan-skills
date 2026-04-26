---
name: gh-update-plan
description: Update a GitHub plan issue with progress. Use when planning a task, or when the user tells you to "update the github plan issue".
argument-hint: "[owner/repo#number] [--local]"
allowed-tools: Bash, Read, Write, Edit
---

Exit plan mode before executing this skill. You must actually run `gh` commands to update the issue; do not just describe what you would do. Use `gh` to read, edit, and comment on issues. This includes using `gh api` to update issue bodies and edit or create comments. Do not ask for permission to update comments — it is expected.

**Workflow for editing issue bodies and comments:**
1. Use a stable temp directory per issue: `/tmp/plan-update-OWNER-REPO-NUMBER`. This allows reuse across invocations.
2. **Fetch or reuse**: If `--local` is passed and the temp directory already has files from a previous invocation, skip fetching and reuse the cached files. Otherwise, fetch content from GitHub using `gh api` and save to the temp directory using the Write tool. Do NOT use shell redirects (`>`).
3. Use the Read and Edit tools to modify the temp files (not shell commands like sed/awk).
4. Upload using `--input` with `jq` to properly JSON-encode the content:

- Edit issue body: `jq -Rs '{body: .}' <tempdir>/body.md | gh api repos/OWNER/REPO/issues/NUMBER -X PATCH --input -`
- Create comment: `jq -Rs '{body: .}' <tempdir>/comment.md | gh api repos/OWNER/REPO/issues/NUMBER/comments --input -`
- Edit comment: `jq -Rs '{body: .}' <tempdir>/comment-COMMENTID.md | gh api repos/OWNER/REPO/issues/comments/COMMENT_ID -X PATCH --input -`

Never embed content directly in shell arguments or use `-f body=@file` (it uploads the literal string, not the file contents).

By default, always fetch the latest from GitHub before making changes. Use `--local` only when you know the issue hasn't been updated since the last fetch.

Never @mention other users in plan issues or comments.

Update the GitHub issue $ARGUMENTS (issue URL or `owner/repo#number`). If no argument is given, use the issue referenced earlier in this conversation. If no issue can be determined, ask the user.

1. Verify that it contains the detailed plan for the work in this conversation. If not, ask the user to verify that the correct issue was given.
2. **Conformance check**: Ensure the issue follows the standard plan format. If not, lightly restructure:
   - Convert plain step lists to checkboxes (`- [ ]` / `- [x]`)
   - Add missing section headings (Description, Steps, Links)
   - If there is no diagram in either the issue body or comments, and the work would benefit from one, add a diagram in a separate comment (Mermaid preferred, three sentence max caption, no "Caption:" prefix)
3. If the design approach has changed or new key decisions were made, update the **Design** comment (or the body for old-format issues that have the how in the body). Omit raw exploration; only include conclusions.
4. Check off completed steps (`- [x]`) based on the work done in this conversation. Steps may be in a separate **Steps** comment (new format) or in the issue body (old format). Check both locations and update wherever the steps are found.
5. If the issue body or comments contain a diagram, check if it is still accurate. If not, update it.
6. If steps need rewording or new steps are needed, update them wherever they are (Steps comment or body). If steps are still in the body and there are many updates, consider migrating them to a separate Steps comment.
7. Update the **Links** comment with any new references (child issues, PRs, documentation, resources). Links may be in a separate comment (new format) or in the body (old format). If in the body, consider migrating to a comment.
8. If useful commands for testing or verifying the work were discovered during this session, add or update a **Useful commands** comment (separate from the issue body). If such a comment already exists, edit it rather than creating a new one.
9. Add or update a **Commits** table in a separate comment (not the issue body) with all git commits related to this work. Each row should include the git ref (short SHA), description, and date. If a commits comment already exists, edit it rather than creating a new one. Also include links to related PRs. Note: these hashes may be from a feature branch and could change after merge — the `gh-close-plan` skill will update them to final hashes on main.
10. Review existing comments on the issue for outdated or incorrect information. If the comment is your own, edit it directly with corrections. If it belongs to someone else, add a reply with the correction.
11. Add a comment summarizing what was done in this session: new insights, changes in understanding, and any remaining open questions.
