---
name: gh-create-pr
description: Create a GitHub PR from the current branch. Use when the user asks to "create a PR", "open a pull request", or "submit a PR".
allowed-tools: Bash
---

Create GitHub pull request(s) from the current branch. If this session touched multiple repos (check conversation context, plan issue, or ask the user), create a PR in each repo. Run steps 1-7 for each repo in sequence.

1. **Check state**: Run `git status` and `git branch --show-current`.
2. **Prepare a branch**:
   - Always fetch the latest base branch (main/master) first.
   - If the current branch is main/master, create a new branch off the freshly fetched base. Pick a short, descriptive branch name from the conversation context (e.g. `resource-tags-docs`). Move any uncommitted changes to the new branch.
   - Otherwise, rebase the current branch onto the freshly fetched base. If there are conflicts, stop and ask the user to resolve them.
3. **Handle uncommitted changes**: If there are uncommitted changes on the (now non-master) branch, ask the user if they want to commit first. Do not proceed until the working tree is clean.
4. **Push the branch**: Push the current branch to remote with `git push -u origin`.
5. **Gather context**: Read the git log for all commits on this branch since it diverged from the base branch. If a plan issue was referenced in this conversation, read it for additional context. Check for a PR template at `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md` in the repo. If one exists, use it as the structure for the PR description.
6. **Create the PR**: Use `gh pr create --web` with `--title` and `--body` to open the browser with the PR pre-filled, letting the user edit before submitting. Do not use `--edit` (opens a terminal editor, unreliable).
   - A concise title (under 70 characters)
   - Body: for trivial PRs (single commit, simple change), a few plain-text sentences covering what, why, and how it was tested. For non-trivial PRs (multi-commit, multi-file, or complex changes), use three sections: `## What`, `## Why`, `## Tested`. Keep each section concise; reviewers read the diff for details.
   - Link to the plan issue only if it is in the same repo as the PR. Do not link to plan issues in other repos.
   - Do not set reviewers or labels.
   - **Footer**: Check for `~/.claude/skills/gh-create-pr/pr-footer.md`. If it exists, append its content to the PR body, separated by `---`. Replace `{{model}}` with the model name powering this session (e.g. "Claude Opus 4.6").
7. **Post-creation**: After the PR is created:
   - If creating PRs across multiple repos, cross-link them in each PR description (e.g. "Related: owner/other-repo#N"). Do NOT cross-link from a public repo to a non-public repo.

Rules:
- Never create a PR without pushing the branch first.
- Keep the description concise. No empty boilerplate sections.
