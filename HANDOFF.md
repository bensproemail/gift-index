# Gift Index — Handoff (Nov 11 2026)

Paste this into a new chat in the "The Simulation Skin" Claude Project, or say "read HANDOFF.md in bensproemail/gift-index".

## What this is
1. The Gift Index is Ben's branded Human Design study: how rare each chart is, and which gifts the tradition ties to it.
2. It stands alone. It is not part of The Simulation or the Spiritual Weather Report site.

## Where everything lives
1. The study: "The Gift Index — Field Guide (v1)" — https://claude.ai/artifact/EXdKGWA7MsZGnWYKx4KqQL
2. The code: GitHub repo bensproemail/gift-index (private).
3. Research notes: Claude Project "The Simulation Skin" docs "Gift Index — Research Base (v2, Nov 11)" and "Gift Index — Build Status (Nov 11)".
4. Dashboard: Rode Command Center, project card "gift-index".
5. Gemini's review: https://share.gemini.google/x1s5he1IrFNW

## Decisions Ben made
1. Count our own charts.
2. Go all the way down to Color, Tone and Base.
3. Ra's teaching first, later teachers labeled, Gene Keys as its own labeled layer.
4. All 7 gift types, equal weight.
5. Use the 2009 Rave Statistics book later as a cross-check, if a legal copy turns up.

## What's done
1. Chart counter built and tested five ways. All checks pass.
2. 2,020,000 random birth times counted (1926–2026, weighted to people alive today).
3. Matches all seven figures seen from the 2009 Rave Statistics book.
4. Field Guide v1 written: rarity tables, 7 gift families, scoring method, worked example, gaps, sources.

## Top findings
1. The typical chart setup is shared by about 1 person in 165.
2. Birth years change rarity a lot: channel 24-61 runs from 3% to 49% depending on birth year.
3. Rarest channels: 21-45 (Money) and 42-53, each 7.1%.
4. A 15-minute birth-time error changes the Sun's Tone in 40% of charts.

## Waiting on Ben
1. Read the Field Guide and say what to change.
2. Pick the brand name and look.

## Next steps for Claude
1. Install the full dev harness in this repo.
2. Build the lookup tool: type a birth time, get the reading.
3. Load real UN world age figures to replace the recalled ones.
4. Add exalted and detriment planets (needs the Rave I'Ching in hand).
5. Add Ra's channel keynotes beside the Parkyn wording.
6. Attach the 192 cross names.
7. Check the remaining 34 Gene Keys Gift words against the book.
8. Decide whether type, lines and centers enter the gift scores.

## How to run the code
1. `pip install -r requirements.txt --break-system-packages`
2. Draw the samples (about 10 minutes total): see the commands in CLAUDE.md.
3. `python3 -m giftindex.count data/living.npz data/alltime.npz data/shift.npz data/results.json`
4. `python3 -m pytest -q`
5. Outside checks need the spiritual-weather-report repo cloned: `python3 tools/xcheck/validate.py <its path>`

## Rules
1. Never type or invent a real person's birth details. Examples use the made-up Sample Reader.
2. Every number must come from data/results.json or a labeled source.
3. Never present a gift claim as proven.
4. Never multiply percentages across linked traits.
