# 0003 Use the development harness, adapted to a Python + JavaScript repo

- **Status:** Accepted
- **Date:** 2026-11-11

## Context
AI-assisted sessions waste tokens re-exploring code, re-deciding settled questions, and reasoning about
correctness that a check could confirm. Ben's standard harness assumes a JavaScript project; this repo's engine
is Python and only the lookup page is JavaScript.

## Decision
- Every change must pass `npm run check`. It runs ESLint and ruff (lint), then vitest and pytest (tests).
- ruff checks real mistakes only (unused or undefined names). Python style is not enforced.
- `CODEMAP.md` is the index of where things live (Python and JavaScript). Non-obvious choices go in `docs/decisions/`.
- Layer rule: `web/engine/**` is pure calculation. It may not import from `web/ui/**` or touch `document`/`window`.
- Generated data (`web/data/**`) is committed so the page can be built and tested without re-running the count.

## Consequences
Claude reads CLAUDE.md, CODEMAP.md and these records at the start of a session instead of scanning the code.
Hooks lint each edited JavaScript file and run the full check before a session ends. `dist/` is not committed.
