# Gift Index — Handoff (Nov 11 2026, after the lookup build)

Paste this into a new chat in the "The Simulation Skin" Claude Project, or say "read HANDOFF.md in bensproemail/gift-index".

## What this is
1. The Gift Index is Ben's Human Design study, branded as The Spiritual Weather Report: how rare each chart is, and which gifts the tradition ties to it.
2. The code stands alone. It is not part of The Simulation or the Spiritual Weather Report site's code.

## Where everything lives
0. The lookup tool: "Gift Index Lookup" — https://claude.ai/artifact/BpvikbU1oSaX5d5dmYq3KQ (private to Ben until he shares it).
1. The study: "The Gift Index — Field Guide (v1)" — https://claude.ai/artifact/EXdKGWA7MsZGnWYKx4KqQL
2. The code: GitHub repo bensproemail/gift-index (created public; Ben is switching it to private).
3. Research notes: Claude Project "The Simulation Skin" docs "Gift Index — Research Base (v2, Nov 11)" and "Gift Index — Build Status (Nov 11)".
4. Dashboard: Rode Command Center, project card "gift-index".
5. Gemini's review: https://share.gemini.google/x1s5he1IrFNW

## Decisions Ben made
1. Count our own charts.
2. Go all the way down to Color, Tone and Base.
3. Ra's teaching first, later teachers labeled, Gene Keys as its own labeled layer.
4. All 7 gift types, equal weight.
5. Use the 2009 Rave Statistics book later as a cross-check, if a legal copy turns up.
6. Brand: The Spiritual Weather Report (name and look). Applied to the lookup tool.
7. Wording under that brand: keep the study's source labels and Human Design terms. Do not switch to the site's plain voice.

## What's done
1. Chart counter built and tested five ways. All checks pass.
2. 2,020,000 random birth times counted (1926–2026, weighted to people alive today).
3. Matches all seven figures seen from the 2009 Rave Statistics book.
4. Field Guide v1 written: rarity tables, 7 gift families, scoring method, worked example, gaps, sources.
5. Dev harness installed (one check command, code map, decision records).
6. Lookup tool v1 built and published: type a birth date, time and town, get the reading. It reproduces the Field Guide's worked example exactly.
7. The lookup page uses this engine's own planet positions (baked in), so it matches the counter: 38,998 of 39,000 test placements identical, the other two on a Base edge.

## Top findings
1. The typical chart setup is shared by about 1 person in 165.
2. Birth years change rarity a lot: channel 24-61 runs from 3% to 49% depending on birth year.
3. Rarest channels: 21-45 (Money) and 42-53, each 7.1%.
4. A 15-minute birth-time error changes the Sun's Tone in 40% of charts.

## Waiting on Ben
1. Try the lookup tool on a phone and say what to change.
2. Read the Field Guide and say what to change.
3. Switch the GitHub repo to private (Settings, Danger Zone, Change visibility). It was created public.

## Next steps for Claude
1. Apply Ben's changes to the lookup tool.
2. Load real UN world age figures to replace the recalled ones (redo the count, the page numbers and the Field Guide together).
3. Add exalted and detriment planets (needs the Rave I'Ching in hand).
4. Add Ra's channel keynotes beside the Parkyn wording.
5. Attach the 192 cross names (then show the cross name in the lookup).
6. Check the remaining 34 Gene Keys Gift words against the book.
7. Decide whether type, lines and centers enter the gift scores.
8. Before the lookup goes public: confirm the licence reading in decision 0004 and the use of the short Parkyn and Gene Keys wording.

## How to run the code
1. `pip install -r requirements.txt --break-system-packages` and `npm ci`
2. `npm run check` — every lint and test. Must pass before a commit.
3. `python3 -m giftindex.lookup 1980-03-04 07:42 America/Chicago` — the lookup as text (the made-up Sample Reader).
4. `npm run build` — builds the lookup page into `dist/index.html`; publish that file over the artifact above.
5. Rebuilding the count or the page data: see the commands in CLAUDE.md.

## Rules
1. Never type or invent a real person's birth details. Examples use the made-up Sample Reader.
2. Every number must come from data/results.json or a labeled source.
3. Never present a gift claim as proven.
4. Never multiply percentages across linked traits.
