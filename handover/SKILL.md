---
name: handover
description: Prepare a handover for continuing work in a new session. Use when the user asks to "hand over", "prepare handover", "wrap up for a new session", or "context dump".
argument-hint: "[plan-issue]"
allowed-tools: Bash, Read
---

Prepare everything needed for a new conversation to continue the current work seamlessly.

1. **Gather state**:
   - Current repo and branch
   - Uncommitted changes (`git status`, `git diff --stat`)
   - Recent commits on this branch
   - The plan issue (from argument, or ask the user)
2. **Summarize the session**: What was done, key decisions made, what's still in progress, any blockers or open questions.
3. **Offer to persist state** before handing over:
   - Update the plan issue (`/gh-update-plan`)
   - Commit uncommitted changes
   Ask the user which of these to do. Skip any already done.
4. **Capture learnings**: Ask the user: "Anything worth capturing from this session?" If yes, propose where each belongs:
   - **Instructions file** (CLAUDE.md, AGENTS.md, or similar): conventions, gotchas, build quirks
   - **Repo docs** (`docs/` or similar): architecture insights, design rationale
   - **Agent memory**: cross-project patterns, user preferences, or durable notes if the agent supports persistent memory

   Apply confirmed items. If nothing to capture, move on.
5. **Generate a handover prompt** that the user can paste into a new session. Include:
   - The plan issue reference (e.g. `/gh-read-plan owner/repo#12`)
   - The repo and branch to work in
   - A 3-5 sentence summary of where things left off
   - The specific next step to work on
   - Any gotchas or context the new session needs (e.g. "the tests pass locally but CI needs a config change first")

Rules:
- Keep the handover prompt concise. It should be copy-pasteable in one go.
- Do not include implementation details the plan issue already captures.
- If there's no plan issue, still generate a useful handover prompt with the repo, branch, and summary.
