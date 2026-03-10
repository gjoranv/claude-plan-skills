# claude-plan-skills

Custom [Claude Code](https://claude.ai/code) skills for managing work across sessions using GitHub issues as execution plans.

## The problem

Claude Code starts fresh every session. Complex tasks that span multiple conversations lose their thread: what's been done, what decisions were made, what's still pending.

## The solution

Use a GitHub issue as a persistent plan. Four skills manage the full lifecycle:

| Skill | What it does |
|---|---|
| `/gh-create-plan` | Creates a structured GitHub issue with description, steps (as checkboxes), diagram, and links |
| `/gh-implement-plan` | Reads the issue, works through steps in order, commits after each step, checks off checkboxes |
| `/gh-update-plan` | Updates the issue with session progress, new decisions, and a commits table |
| `/gh-close-plan` | Finalizes the issue with a session log, final commit hashes, and closes it |

A new conversation can pick up exactly where the last one left off by reading the issue.

## Installation

Copy the skill directories into your Claude Code skills folder:

```bash
cp -r gh-create-plan gh-implement-plan gh-update-plan gh-close-plan ~/.claude/skills/
```

Or clone this repo and symlink:

```bash
git clone https://github.com/gjoranv/claude-plan-skills ~/git/claude-plan-skills
for skill in gh-create-plan gh-implement-plan gh-update-plan gh-close-plan; do
  ln -s ~/git/claude-plan-skills/$skill ~/.claude/skills/$skill
done
```

## Usage

```
/gh-create-plan owner/repo        # Create a plan issue in the given repo
/gh-implement-plan owner/repo#42  # Start implementing the plan
/gh-update-plan                   # Update the plan after a session
/gh-close-plan                    # Finalize and close the plan
```

After creating an issue, the skills accept a URL or `owner/repo#number`. If a plan issue was referenced earlier in the conversation, the argument can be omitted.

## Requirements

- [Claude Code](https://claude.ai/code)
- [GitHub CLI (`gh`)](https://cli.github.com/) authenticated

## Related

These skills are described in [Claude Code Doesn't Remember. Here's How I Fixed That.](https://gjoranv.hashnode.dev/claude-code-doesn-t-remember-here-s-how-i-fixed-that)
