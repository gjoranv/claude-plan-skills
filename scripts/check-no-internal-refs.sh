#!/usr/bin/env bash
#
# Guard: this is a public repo and must stay born-clean. The skills are synced
# from private copies that DO carry internal references (a specific memory CLI,
# team repos, personal-org paths); this check fails the build if any leak in.
#
# Scans tracked markdown (where skill/readme content lives). Runs in CI and can
# be wired as a local pre-commit hook:
#   ln -sf ../../scripts/check-no-internal-refs.sh .git/hooks/pre-commit
#
# To extend: add tokens to DENY. Keep patterns specific enough not to trip on
# generic English ("recall", "capture") or this repo's own identity.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

# Internal system + company tokens that must never appear in this public repo.
# Substring match (not word-boundary): git grep -E does not honor \b portably,
# and substrings are what we want anyway (daim-common, daim-personal, ...).
DENY='daim|konfekt|vespaai|vespa-engine|/Users/'

hits_deny=$(git grep -nEI "$DENY" -- '*.md' || true)

# Any personal-org path (e.g. gjoranv/docs, ~/git/gjoranv/...), except this
# repo's own clone URL and the author's public handle (medium.com/@gjoranv).
hits_org=$(git grep -nEI 'gjoranv/' -- '*.md' | grep -vE 'gjoranv/claude-plan-skills|@gjoranv' || true)

if [ -n "$hits_deny$hits_org" ]; then
  echo "FAIL: internal reference(s) found in a public repo:"
  echo
  [ -n "$hits_deny" ] && echo "$hits_deny"
  [ -n "$hits_org" ] && echo "$hits_org"
  echo
  echo "Keep this repo born-clean: no memory-CLI name, team/company repos, or"
  echo "personal-org paths. Genericize before committing. If a hit is a false"
  echo "positive, refine DENY in scripts/check-no-internal-refs.sh."
  exit 1
fi

echo "OK: no internal references found."
