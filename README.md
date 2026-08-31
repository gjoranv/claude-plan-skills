# claude-plan-skills

Custom skills for managing work across sessions using GitHub issues as execution plans. Works with Claude Code, Codex, and other agents that support skills.

## The problem

An AI coding agent loses context between sessions. Complex tasks that span multiple conversations lose their thread: what's been done, what decisions were made, what's still pending.

## The solution

Use a GitHub issue as a persistent plan:

| Skill | What it does |
|---|---|
| `/gh-create-plan` | Creates a structured GitHub issue with steps, design, diagram, links, and agent sessions as separate comments |
| `/gh-read-plan` | Reads the issue, identifies completed and pending steps, and briefs the session |
| `/gh-implement-plan` | Works through steps in order, commits after each step, checks off checkboxes |
| `/gh-update-plan` | Updates the issue with progress, tracks which agent sessions worked on it. Supports `--preview` (diff before uploading) |
| `/gh-close-plan` | Consolidates session logs, captures learnings, finalizes PRs table, and closes |
| `/gh-create-pr` | Creates a PR using `--web` to open the browser with title and body pre-filled for editing |
| `/handover` | Prepares a handover prompt for continuing work in a new session |

A new conversation can pick up exactly where the last one left off by reading the issue with `/gh-read-plan`, or by pasting a `/handover` prompt from the previous session.

## Installation

Clone and symlink:

### Claude Code

```bash
git clone https://github.com/gjoranv/claude-plan-skills ~/git/claude-plan-skills
for d in ~/git/claude-plan-skills/*/SKILL.md; do
  ln -sfn "$(dirname "$d")" ~/.claude/skills/
done
```

### Codex

```bash
for d in ~/git/claude-plan-skills/*/SKILL.md; do
  ln -sfn "$(dirname "$d")" ~/.codex/skills/
done
```

## Usage

```
/gh-create-plan owner/repo        # Create a plan issue in the given repo
/gh-read-plan owner/repo#42       # Read the plan into the current session
/gh-implement-plan owner/repo#42  # Start implementing the plan
/gh-update-plan                   # Update the plan after a session
/gh-close-plan                    # Finalize and close the plan
/gh-create-pr                     # Create a PR, opens browser for editing
/handover                         # Prepare a handover for a new session
```

After creating an issue, the skills accept a URL or `owner/repo#number`. If a plan issue was referenced earlier in the conversation, the argument can be omitted.

## Customization

**Plan repos**: Create `~/.claude/skills/plan-config.json` to configure where plan issues are created:

```json
{
  "personalRepo": "your-user/plans",
  "teamRepo": "your-org/team-plans"
}
```

Both fields are optional. If only one is set, it's used by default. `/gh-create-plan` accepts `personal`, `team`, or `owner/repo` as argument. Plans in the `teamRepo` get a frozen team record on close.

**PR footer**: Copy `gh-create-pr/pr-footer-example.md` to `~/.claude/skills/gh-create-pr/pr-footer.md` and edit. Appended to every PR body, separated by `---`. Supports `{{model}}` placeholder (replaced with the current model name at submission time).

## Requirements

- [GitHub CLI (`gh`)](https://cli.github.com/) authenticated

## Related

- [Claude Code Doesn't Remember. Here's How I Fixed That.](https://medium.com/@gjoranv/claude-code-doesnt-remember-here-s-how-i-fixed-that-0992cbeb6d37) - how these skills work and why GitHub issues are the persistence layer
- [I Don't Start With a Plan. Here's What I Do First.](https://medium.com/@gjoranv/i-dont-start-with-a-plan-here-s-what-i-do-first-9f6192177298) - the investigation phase before creating a plan, and the handover skill for continuing across sessions
