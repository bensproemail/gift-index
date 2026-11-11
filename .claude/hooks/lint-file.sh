#!/bin/bash
# After Claude edits a file, lint just that file. Errors are fed back to Claude (exit 2).
input=$(cat)
file=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
cd "$CLAUDE_PROJECT_DIR" || exit 0
[ -z "$file" ] && exit 0
case "$file" in
  *.js|*.jsx|*.ts|*.tsx|*.mjs|*.cjs) ;;
  *) exit 0 ;;
esac
[ -x node_modules/.bin/eslint ] || exit 0
out=$(node_modules/.bin/eslint --no-warn-ignored "$file" 2>&1)
if [ $? -ne 0 ]; then
  echo "ESLint errors in $file — fix before continuing:" >&2
  echo "$out" | head -40 >&2
  exit 2
fi
exit 0
