---
name: gh-close-plan
description: Close a GitHub plan issue with a summary. Use when the user tells you to "close the github plan issue".
allowed-tools: Bash, Read, Edit
---

Never @mention other users in plan issues or comments.

Close the GitHub issue $ARGUMENTS (issue URL or `owner/repo#number`). If no argument is given, use the issue referenced earlier in this conversation. If no issue can be determined, ask the user.

**Workflow for editing issue bodies and comments:**
1. Create a unique temp directory: `mktemp -d /tmp/plan-close-XXXXX`
2. Fetch content from GitHub and save to files in that directory (e.g. `body.md`, `comment-COMMENTID.md`)
3. Use the Read and Edit tools to modify the temp files
4. Upload using `--input` with `jq` to properly JSON-encode the content:

- Edit issue body: `jq -Rs '{body: .}' <tempdir>/body.md | gh api repos/OWNER/REPO/issues/NUMBER -X PATCH --input -`
- Create comment: `jq -Rs '{body: .}' <tempdir>/comment.md | gh api repos/OWNER/REPO/issues/NUMBER/comments --input -`
- Edit comment: `jq -Rs '{body: .}' <tempdir>/comment-COMMENTID.md | gh api repos/OWNER/REPO/issues/comments/COMMENT_ID -X PATCH --input -`

Never embed content directly in shell arguments or use `-f body=@file` (it uploads the literal string, not the file contents). Always fetch the latest from GitHub before making changes.

1. Read the issue and its comments to understand the full history of the work.
2. Check off completed steps (`- [x]`) in the issue body based on the work done in this conversation.
3. Verify that all steps are checked off. If any are incomplete, ask the user whether to proceed or leave the issue open.
4. Add or update a **Commits** table comment with the final commit hashes from main. Feature branch hashes change after squash/rebase merge, so look up the corresponding commits on main and replace the old hashes.
5. **Clean up session comments**: Delete all individual session comments and replace them with a single consolidated **Session Log** comment. Structure it with dated sections (`### YYYY-MM-DD`) for each session that contributed something worth keeping. Include only key findings, decisions, and insights. Drop sessions that had nothing noteworthy.
6. Add a closing comment summarizing:
   * What was accomplished
   * Links to the final PR(s) or commits
   * Any follow-up work or known limitations
7. Close the issue.
