# 0006 Brand: The Spiritual Weather Report

- **Status:** Accepted
- **Date:** 2026-11-11

## Context
The brand name and look for the Gift Index were open. Three options were on the table: Jennie Marie / her
private-practice brand, The Spiritual Weather Report, or a new brand of its own. Ben chose The Spiritual Weather
Report (Nov 11 2026).

## Decision
- The Gift Index is published under The Spiritual Weather Report's name and look. Its name stays "The Gift Index".
- The look is copied from that site's theme (its decision 0036), read from the `spiritual-weather-report` repo:
  deep plum `#2b0b45`, royal purple `#4b1a78`, orchid `#c0399b`, bright gold `#ffc62e` / `#ffe27a`, lavender paper
  `#f8f2fb`; Playfair Display headlines, Jost labels, Inter body; the sun-over-water mark and the masthead lockup;
  white cards with a 14px radius; pill buttons; dark cards with a thin gold frame.
- On charts, the Design (unconscious) side is drawn in orchid, which replaces red in this brand.
- One theme: the site has no dark mode, so the lookup page keeps the brand colors in every viewer theme.
- The site's naming rules apply to anything a reader sees: always "Jennie Marie"; never name her other business.
  `web/tests/brand.test.js` enforces this on the page.
- The code stays standalone in this repo. Nothing is imported from the site's repo; the tokens are copied values.

## Consequences
The look lives in the token block at the top of `web/ui/style.css`; if the site's theme changes, copy the new
values here. OPEN (Ben to decide): the site never shows book names, page numbers or system words and speaks in
Jennie Marie's voice, while the Gift Index labels every claim with its source (BOOK, RA, GK ...) and uses the
system's own terms. Until Ben decides, the Gift Index keeps its own labeling rules under the brand's look.
