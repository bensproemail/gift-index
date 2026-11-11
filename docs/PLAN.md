# Plan

## Goal
A branded Gift Index study with counted rarity numbers and seven gift scores, then a lookup tool built on it.

## Steps
- [x] Chart calculator (positions, gates, lines, color/tone/base, centers, channels, type, authority, definition, profile, arrows)
- [x] Tests: 33 reference moments, independent engine, golden charts, Rave Statistics 2009 figures
- [x] Count 2,020,000 charts (births 1926–2026) + 400,000 (1781–2030) + birth-time error sample
- [x] Seven gift families and scoring; one-person reading
- [x] Study document v1 (Claude doc "The Gift Index — Field Guide (v1)")
- [x] Put this code on GitHub (repo `bensproemail/gift-index`) and install the dev harness (decision 0003)
- [ ] Download real world age figures (UN) to replace the recalled age mix
- [ ] Exalted / detriment planets (needs the Rave I'Ching in hand)
- [ ] Ra's own channel keynotes beside the Parkyn wording
- [ ] Decide whether type, lines and centers enter the gift scores
- [ ] Attach the 192 cross names
- [ ] Verify the remaining Gene Keys Gift words against the book
- [x] Brand name and look: The Spiritual Weather Report (decision 0006), applied to the lookup page
- [x] Wording under that brand: keep the study labels and system terms (Ben, decision 0006)
- [ ] Ben switches the GitHub repo to private (it was created public; settings changes are blocked from Claude's session)
- [x] Lookup tool v1: enter a birth moment, get the reading (decisions 0004, 0005). Command line: `python3 -m giftindex.lookup`. Page: `npm run build`, published as the Claude artifact "Gift Index Lookup"
- [ ] Ben tries the lookup on his phone and says what to change
- [ ] Lookup v2 ideas: cross names once attached; a bodygraph drawing; brand look once chosen; share-safe summary card

## Blocked / notes
- Real UN age figures: changing the age mix changes every "living people" number, so the count, `ref.json`, the page and the Field Guide must all be redone together. Do it as one step, not piecemeal.
- The lookup page carries Swiss Ephemeris positions as baked data. Before the page goes public under a brand, have someone qualified confirm two things: that baked positions carry no Swiss Ephemeris licence duty (our reading in decision 0004, not legal advice), and that the short Parkyn summaries and Gene Keys Gift words are fine to show.
