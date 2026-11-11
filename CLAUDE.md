# The Gift Index

@.claude/harness-rules.md

## What this is
The chart counter behind Ben's Gift Index study, and the lookup tool built on it. The counter computes Human
Design charts for millions of random birth moments, counts how rare every chart element is, and scores seven
gift families. The lookup tool takes one birth moment and shows that chart's rarity and gift scores.
Brand: The Spiritual Weather Report (decision 0006). The code is standalone: it is NOT part of The Simulation or the
Spiritual Weather Report site's code.

## Stack
- Python 3 (numpy, pyswisseph in Moshier mode, pytest, ruff): the engine and the count. This is the reference.
- JavaScript (no framework, esbuild, vitest, eslint): the lookup page. It reads positions baked from the Python
  engine, so it cannot drift from it (decision 0004).
- A small Node script in `tools/xcheck` cross-checks against the site's independent engine.

## Commands
- `npm run check` — lint (eslint + ruff) and all tests (vitest + pytest). Must pass before any commit.
- `npm run codemap` — regenerate CODEMAP.md after adding/moving files.
- `npm run build` — build the lookup page as one file, `dist/index.html`.
- `python3 -m giftindex.lookup 1980-03-04 07:42 America/Chicago` — the lookup as plain text (that is the Sample Reader).
- First-time setup: `pip install -r requirements.txt --break-system-packages` and `npm ci`.

Rebuilding the data (only when the engine or the count changes), in this order:
- `python3 -m giftindex.sample living 20000 data/living.npz` — draw the main sample (seeded, about 5 minutes).
- `python3 -m giftindex.sample span 400000 data/alltime.npz 2371629.5 2462502.5` — the 1781–2030 comparison sample.
- `python3 -m giftindex.sample shift 40000 data/shift.npz` — the birth-time error sample.
- `python3 -m giftindex.count data/living.npz data/alltime.npz data/shift.npz data/results.json` — all tables.
- `python3 -m giftindex.bake web/data/ephem.bin` — bake the planet positions for the page (about 1 minute).
- `python3 -m giftindex.webref web/data/ref.json web/tests/fixtures.json` — the page's numbers and test fixtures.
- `node scripts/build-cities.mjs` — the birthplace list.
- `python3 tools/xcheck/validate.py <path to spiritual-weather-report clone>` — outside checks.

## Where things are
See `CODEMAP.md` (auto-generated). Don't explore the tree manually. In short:
- `giftindex/` — the Python engine, the count, the report and the command-line lookup.
- `web/engine/` — the same report in JavaScript (pure calculation, no page access).
- `web/ui/` — the lookup page. `web/data/` — generated data the page carries. `web/tests/` — JavaScript tests.
- `data/results.json` — the published numbers. The study document and the page are built from this file.

## Architecture rules (enforced by ESLint)
- `web/engine/**` may not import from `web/ui/**` and may not touch `document` or `window`.
- Every number the page shows comes from `web/data/ref.json`, which `giftindex.webref` builds from `data/results.json`.
- The page's report (`web/engine/report.js`) must equal the Python report (`giftindex/report.py`); a test compares them.

## Rules
- Birth data rule: never type or invent a real person's birth minute, birthplace or time zone. Examples use the
  made-up Sample Reader (4 Mar 1980, 7:42 am, Racine). Real charts are read at test time from the site repo's
  golden file and never copied here. The lookup page stores nothing a visitor types.
- Every number in the study must come from `data/results.json` or a labeled outside source.
- Never present a gift claim as proven. Label every claim: COUNT, RA, BOOK, CALC, STUDY, TEACHER, GK, MINE.
- Never multiply percentages across linked traits. Combined rarity comes only from counting.
- Naming (tested): on anything a reader sees, always "Jennie Marie", and never name her other business.

## Decisions
See `docs/decisions/`. Follow them; supersede with a new record rather than ignoring one.

## Current plan
See `docs/PLAN.md`.
