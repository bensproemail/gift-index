# 0004 The lookup page reads planet positions baked from the Python engine

- **Status:** Accepted
- **Date:** 2026-11-11

## Context
The lookup tool must run in a browser (Ben and his readers use phones; there is no server). Swiss Ephemeris,
which the count uses, does not run there except as AGPL/GPL WebAssembly builds. A separate MIT astronomy library
(astronomy-engine) was measured against our engine on 3,000 moments: it differs by 2 to 12 arcseconds for the
planets and up to 59 arcseconds for the true Node. That is enough to put a placement on the other side of a line
or Tone edge, so a reading could disagree with the engine that produced the rarity numbers.

## Decision
- `giftindex/bake.py` stores this engine's own longitudes for the Sun, Moon, true Node and eight planets as
  Chebyshev pieces in `web/data/ephem.bin` (about 790 KB, 1 Sep 1925 to 1 Jan 2031). Pieces that miss their limit
  are halved, down to 22.5 minutes (needed for a few hours when a planet passes behind the Sun).
- The page (`web/engine/ephem.js`, `sky.js`) evaluates those pieces. It uses no astronomy library.
- Limits: 0.003 arcsecond per body; 0.12 for the true Node, which is only smooth to about 0.05 in the engine itself.
- The chart logic and the report are written twice (Python and JavaScript) and compared by test on 1,500 random
  moments (positions) and 129 full reports. Measured: 38,998 of 39,000 placements identical down to the Base; the
  other two sit within 0.002 arcsecond of a Base edge.
- The page covers births 1926 through 2030. The birth-year ("born within two years") view exists only for
  1926 to 2026, the years the count covers.

## Consequences
One engine, never forked: the page cannot drift from the count. Our reading is that no Swiss Ephemeris licence duty reaches the page,
because the baked numbers are output data, not its code; this is not legal advice and should be confirmed before a
public launch. The page is about 1.5 MB. After any change to `positions.py`, re-run `giftindex.bake` and
`giftindex.webref`; tests fail if the baked table, `ref.json` or the fixtures are stale. Births outside the baked
span need a re-bake with a wider span.
