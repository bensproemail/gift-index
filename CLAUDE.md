# The Gift Index

## What this is
The chart counter behind Ben's Gift Index study: it computes Human Design charts for millions of random birth
moments, counts how rare every chart element is, and scores seven gift families. Standalone. It is NOT part of
The Simulation or the Spiritual Weather Report site.

## Stack
Python 3 (numpy, pyswisseph in Moshier mode, pytest). A small Node script is used only for cross-checking
against the site's independent engine.

## Commands
- `python3 -m pytest -q` — all tests. Must pass before any commit.
- `python3 -m giftindex.sample living 20000 data/living.npz` — draw the main sample (seeded, about 5 minutes).
- `python3 -m giftindex.sample span 400000 data/alltime.npz 2371629.5 2462502.5` — the 1781–2030 comparison sample.
- `python3 -m giftindex.sample shift 40000 data/shift.npz` — the birth-time error sample.
- `python3 -m giftindex.count data/living.npz data/alltime.npz data/shift.npz data/results.json` — all tables.
- `python3 tools/xcheck/validate.py <path to spiritual-weather-report clone>` — outside checks.

## Where things are
- `giftindex/tables.py` — wheel, centers, channels, circuits, the seven gift families.
- `giftindex/positions.py` — planet positions and the Design moment.
- `giftindex/chart.py` — chart facts for many charts at once.
- `giftindex/sample.py`, `giftindex/count.py` — the sample and the count.
- `giftindex/reading.py` — one person's Gift Index reading.
- `data/results.json` — the published numbers. The study document is built from this file.

## Rules
- Birth data rule: never type or invent a real person's birth minute, birthplace or time zone. Examples use the
  made-up Sample Reader (4 Mar 1980, 7:42 am, Racine). Real charts are read at test time from the site repo's
  golden file and never copied here.
- Every number in the study must come from `data/results.json` or a labeled outside source.
- Never present a gift claim as proven. Label every claim: COUNT, RA, BOOK, CALC, STUDY, TEACHER, GK, MINE.
- Never multiply percentages across linked traits. Combined rarity comes only from counting.

## Decisions
See `docs/decisions/`.

## Current plan
See `docs/PLAN.md`.
