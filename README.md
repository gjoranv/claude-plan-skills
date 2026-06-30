# claude-plan-skills

Custom [Claude Code](https://claude.ai/code) skills for managing work across sessions using GitHub issues as execution plans.

## The problem

Claude Code starts fresh every session. Complex tasks that span multiple conversations lose their thread: what's been done, what decisions were made, what's still pending.

## The solution

Use a GitHub issue as a persistent plan. Seven skills manage the full lifecycle:

| Skill | What it does |
|---|---|
| `/gh-create-plan` | Creates a structured GitHub issue with description, design, steps, diagram, and links as separate comments |
| `/gh-read-plan` | Reads the issue, identifies completed and pending steps, and briefs the session |
| `/gh-implement-plan` | Works through steps in order, commits after each step, checks off checkboxes |
| `/gh-update-plan` | Updates the issue with session progress, new decisions, and a commits table |
| `/gh-close-plan` | Consolidates session logs, captures learnings, finalizes commit hashes, and closes |
| `/gh-create-pr` | Creates a PR using `--web` to open the browser with title and body pre-filled for editing before submission |
| `/handover` | Prepares a handover prompt for continuing work in a new session |

A new conversation can pick up exactly where the last one left off by reading the issue with `/gh-read-plan`, or by pasting a `/handover` prompt from the previous session.

## Installation

Copy the skill directories into your Claude Code skills folder:

```bash
cp -r gh-create-plan gh-read-plan gh-implement-plan gh-update-plan gh-close-plan gh-create-pr handover ~/.claude/skills/
```

Or clone and symlink (recommended — picks up new skills on `git pull`):

```bash
git clone https://github.com/gjoranv/claude-plan-skills ~/git/claude-plan-skills
for d in ~/git/claude-plan-skills/*/SKILL.md; do
  ln -sfn "$(dirname "$d")" ~/.claude/skills/
done
```

### Codex

These skills are agent-neutral and work with Codex. Copy them to the Codex skills folder:

```bash
cp -r gh-create-plan gh-read-plan gh-implement-plan gh-update-plan gh-close-plan gh-create-pr handover ~/.codex/skills/
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

**PR footer**: Copy `gh-create-pr/pr-footer-example.md` to `~/.claude/skills/gh-create-pr/pr-footer.md` and edit. Appended to every PR body, separated by `---`. Supports `{{model}}` placeholder (replaced with the current model name at submission time).

## Requirements

- [Claude Code](https://claude.ai/code)
- [GitHub CLI (`gh`)](https://cli.github.com/) authenticated

## Related

- [Claude Code Doesn't Remember. Here's How I Fixed That.](https://medium.com/@gjoranv/claude-code-doesnt-remember-here-s-how-i-fixed-that-0992cbeb6d37) - how these skills work and why GitHub issues are the persistence layer
- [I Don't Start With a Plan. Here's What I Do First.](https://medium.com/@gjoranv/i-dont-start-with-a-plan-here-s-what-i-do-first-9f6192177298) - the investigation phase before creating a plan, and the handover skill for continuing across sessions
