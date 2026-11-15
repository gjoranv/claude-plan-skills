---
name: gh-close-plan
description: Close a GitHub plan issue with a summary. Use when the user tells you to "close the github plan issue".
argument-hint: "[owner/repo#number]"
allowed-tools: Bash, Read, Write, Edit
---

Never @mention other users in plan issues or comments.

Close the GitHub issue $ARGUMENTS (issue URL or `owner/repo#number`). If no argument is given, use the issue referenced earlier in this conversation. If no issue can be determined, ask the user.

**Workflow for editing issue bodies and comments:**
1. Create a unique temp directory: `mktemp -d /tmp/plan-close-XXXXX`
2. Fetch content from GitHub using `gh api` and save it to files in the temp directory (e.g. `body.md`, `comment-COMMENTID.md`). In Claude Code, prefer the Write tool. Do not embed fetched content directly in shell arguments.
3. Modify the temp files with the agent's normal file-edit mechanism. In Claude Code, prefer the Read and Edit tools. Avoid ad hoc `sed`/`awk` rewrites.
4. Upload using `--input` with `jq` to properly JSON-encode the content:

- Edit issue body: `jq -Rs '{body: .}' <tempdir>/body.md | gh api repos/OWNER/REPO/issues/NUMBER -X PATCH --input -`
- Create comment: `jq -Rs '{body: .}' <tempdir>/comment.md | gh api repos/OWNER/REPO/issues/NUMBER/comments --input -`
- Edit comment: `jq -Rs '{body: .}' <tempdir>/comment-COMMENTID.md | gh api repos/OWNER/REPO/issues/comments/COMMENT_ID -X PATCH --input -`

Never embed content directly in shell arguments or use `-f body=@file` (it uploads the literal string, not the file contents). Always fetch the latest from GitHub before making changes. Do not rely on previously fetched copies that may be stale.

1. Read the issue and its comments to understand the full history of the work.
2. Check off completed steps (`- [x]`) based on the work done. Steps may be in a separate **Steps** comment (new format) or in the issue body (old format). Check both locations.
3. Verify that all steps are checked off. If any are incomplete, ask the user whether to proceed or leave the issue open.
4. Finalize the **PRs** comment as a table: `| PR | What | Agent session |`. PR column: `org/repo#N` as a link. What column: brief description. Agent session column: the session that added the PR. If the existing comment uses a different format (bullet list, old-style table), reformat it to this table structure.
5. **Clean up comments**: Non-structural comments fall into two categories based on their heading:
   - **`### Session:` prefix**: These are session summaries. Delete them and consolidate into a single **Session Log** comment with dated sections (`### YYYY-MM-DD`). Keep only key findings, decisions, and insights. Drop sessions with nothing noteworthy.
   - **Any other heading** (e.g. "Research:", "Considered:", "Implementation notes:", "Verification:"): These are standalone findings with lasting value. Keep them as separate comments, or merge into the Design comment if they are design decisions.
   **Never delete structural comments** (Steps, Design, Diagram, Links, Useful commands, Agent sessions, PRs). See `gh-create-plan` for the canonical list and order.
   **Tidy the Links comment**: give every bare link a one-line description and group the links under short headings when there are more than 10, as `gh-update-plan` step 7 describes.
6. **Capture learnings**: Before closing, review the work for non-obvious discoveries worth persisting. If a durable-memory CLI is configured, offer its capture flow. Otherwise, ask the user "Anything worth capturing?" and propose where each belongs:
   - **Instructions file** (CLAUDE.md, AGENTS.md, or similar): conventions, gotchas, build quirks
   - **Repo docs** (`docs/` or similar): architecture insights, design rationale
   - **Memory**: cross-project patterns, user preferences

   For a **company-shareable plan** (opened in the `teamRepo` from `~/.claude/skills/plan-config.json`), distill a frozen team **record** summarizing what was decided and why, recording this plan issue in the provenance field the store defines, so the closed plan carries no unique living knowledge and becomes safely archival. One record per independently citable outcome (usually one per plan). Split only when different consumers would cite different parts; never split by timeline or implementation phase. Write no record if no `teamRepo` is configured or the plan is not in that repo; the capture of learnings above still applies.

   **Check the records checkout before writing** anything into it. Each check that fails stops the record step and leaves the checkout exactly as found; report the reason and ask the user how to proceed.
   1. `git fetch` the store's remote.
   2. Stop if the remote's default branch cannot be determined (`git symbolic-ref refs/remotes/origin/HEAD`, or `git remote show origin`).
   3. Stop if the checkout is on any branch other than that default branch.
   4. Stop on any uncommitted change, staged or not (`git status --porcelain` must be empty).
   5. Fast-forward to the remote default branch (`git merge --ff-only`); stop if the branches have diverged.

   **Follow the store's own standard.** Read the store's `index.md` for the record format, register the record where the store lists them, and make the finished record satisfy the store's "Writing a record" section. If `index.md` exists but has no "Writing a record" section, write by the procedure below and propose adding that section to the store. If `index.md` is missing, stop: the record format itself is then unknown.

   Before landing, check the finished record and its catalog registration against the store's `index.md`.

   The procedure while writing:
   - Verify each fact against the artifact it came from (PR, commit, document, test run) before stating it.
   - Explain every term; a reader who meets it here for the first time must be able to understand it from the record.
   - Write for a reader who was not part of the work and has only the team's repositories and the artifacts they link.
   - If a durable-memory CLI is configured, run a diagnostic query for the new record and inspect the title, description, and sources it returns before landing it.

   **Land it the store's way.** Once the record and its registration are written, land them as the store's "Landing a record" section says. If that section is missing, stop and report; do not choose a landing method yourself.

   **Close-time breadcrumb**: if this plan is a child of a parent plan that has a team record, and the store supports linking a follow-up record to its parent, propose that link on the parent's record in the form the store defines. Never rewrite a landed record's body; skipping the link loses nothing (the follow-up is independently findable).

   Apply confirmed items. If the user says nothing to capture, move on.
7. Add a closing comment summarizing:
   * What was accomplished
   * Links to the final PR(s)
   * Any follow-up work or known limitations
8. Close the issue.
