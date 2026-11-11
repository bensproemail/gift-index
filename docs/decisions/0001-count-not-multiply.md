# 0001 Rarity comes from counting charts, never from multiplying percentages

- **Status:** Accepted
- **Date:** 2026-11-11

## Context
Chart traits are linked (a Reflector always has no definition and Lunar authority; profile fixes the cross angle;
slow planets mark whole birth years). Multiplying published percentages overstates rarity by orders of magnitude.
Published figures for channels and gates did not exist in usable form. Ben approved counting our own charts.

## Decision
- Compute full charts for random birth moments with Swiss Ephemeris (Moshier mode, tropical, true node, Design =
  Sun 88 degrees earlier) and count every element directly.
- Main sample: 20,000 moments per birth year 1926–2026 (seeded). "Living people" weights years by a 2025 world
  age mix. "Born within 2 years" uses the five birth years around a person.
- Headline rarity = type + authority + definition + profile counted jointly. Channels and gates are reported as
  their own shares. Color, Tone, Base and arrows carry no rarity claim.
- Ego authority: a Manifestor with Ego authority is "Ego Manifested", a Projector is "Ego Projected".

## Consequences
Numbers are reproducible (`giftindex.sample`, `giftindex.count`). `tests/test_engine.py` fails if the count drifts
from the known profile shares or from the seven Rave Statistics (2009) figures. The age mix is approximate until
real UN figures are loaded.
