# Harness working rules (travel with this repo)

These rules exist to save tokens and prevent rework. Prefer deterministic checks over reasoning.

## Start of every session
1. Read the project's `CLAUDE.md`, then `CODEMAP.md`, then the titles in `docs/decisions/`.
2. Do NOT re-read the whole codebase. Use `CODEMAP.md` to find where things live, then open only the files you need.
3. If `CODEMAP.md` or `docs/decisions/` is missing, regenerate it with `npm run codemap` and create `docs/decisions/` from the template.

## While working
- Before writing new functionality, search `CODEMAP.md` for something that already does it. Reuse before you build.
- Never decide "is this correct?" by reasoning alone. Run `npm run check` (lint + architecture + tests) and trust the result.
- Fix failures the checks report. Don't argue with a check; if a rule is wrong, record a decision and change the rule.
- Follow decisions in `docs/decisions/`. Don't re-debate them. To change one, write a new decision that supersedes it.
- When you make a non-obvious choice (library, data shape, folder layout, trade-off), write a short decision record using `docs/decisions/0000-template.md`.
- After adding, moving or renaming files, run `npm run codemap`.

## Keeping the main context small
- For "where is X / how does Y work" questions across many files, delegate to the `code-scout` subagent and use its short report.
- To run the full check suite and get only the failures, delegate to the `check-runner` subagent.
- Don't paste large files or long logs into the conversation; summarize.

## Long autonomous runs
- Work from a written plan in `docs/PLAN.md`. Tick items off as they pass checks.
- Commit after each item that passes `npm run check`, with a clear message.
- If stuck on the same failure 3 times, stop, write what you tried in `docs/PLAN.md`, and move to the next item.
