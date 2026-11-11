#!/bin/bash
# Before Claude finishes, run the full check suite. If it fails, Claude must keep working.
input=$(cat)
# Prevent infinite loops: if we already blocked once this turn, let Claude stop.
if printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || exit 0
grep -q '"check"' package.json 2>/dev/null || exit 0
# Refresh the code map so the next session starts current.
grep -q '"codemap"' package.json && npm run -s codemap >/dev/null 2>&1
out=$(npm run -s check 2>&1)
if [ $? -ne 0 ]; then
  echo "npm run check is failing. Fix these before finishing:" >&2
  echo "$out" | tail -40 >&2
  exit 2
fi
exit 0
