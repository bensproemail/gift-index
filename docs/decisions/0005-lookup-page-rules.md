# 0005 Lookup page: one file, explicit fields, a receipt, nothing stored

- **Status:** Accepted
- **Date:** 2026-11-11

## Context
A wrong reading most often starts with wrong input (AM/PM, the daylight-time flip, the wrong town of the same
name), not with wrong astronomy. The page is also the first Gift Index surface a reader touches, and it handles
birth details.

## Decision
- Input is explicit fields (month, day, year, hour, minute, AM/PM, birthplace). The page reads back the weekday
  and the clock rule in force (for example "Central Standard Time (UTC-06:00)") before anything is calculated.
- Every reading starts with a "Read from:" receipt: what was typed, the place, the clock rule and the UTC moment.
- A clock time that never happened (clocks jumped forward) is refused. One that happened twice asks which pass.
- Local time becomes UTC with the browser's own time-zone database (`web/engine/clock.js`); the Python side uses
  `zoneinfo`. A test makes the two agree on 22 cases back to 1933.
- Birthplaces come from a built-in list of 7,280 towns (`web/data/cities.json`, from the MIT `city-timezones`
  package). A reader whose town is missing picks the time zone directly.
- The page opens on the made-up Sample Reader, marked as an example.
- Nothing typed is saved or sent: no storage, and no request carries what was typed. The page says so. The only
  outside request is for the font files (Google Fonts).
- Every figure carries its source label; every gift shows its downside; rarity and gifts are never blended.
- Each reading re-runs the chart 5, 15, 30 and 60 minutes earlier and later and says which facts hold.
- The page is built as one self-contained file (`npm run build` -> `dist/index.html`) and published as a Claude
  artifact. Brand name and look are not chosen yet; colors and fonts are tokens at the top of `web/ui/style.css`.

## Consequences
Before 1970 the database only knows each zone's main city, so local daylight-time rules of smaller towns can be
missed; the receipt shows the rule used so a reader can catch it. Adding a town means editing the city list
source, not the page.
