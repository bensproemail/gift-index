#!/usr/bin/env node
// Builds web/data/cities.json: a compact birthplace list (city, region, country -> time zone) for the lookup page.
// Source: the MIT-licensed city-timezones package. Usage: node scripts/build-cities.mjs
import { writeFileSync } from 'node:fs';
import cityTimezones from 'city-timezones';

const known = new Set(Intl.supportedValuesOf('timeZone'));
const canonical = (zone) => {
  try {
    return new Intl.DateTimeFormat('en-US', { timeZone: zone }).resolvedOptions().timeZone;
  } catch {
    return null;
  }
};
const SHORT = { 'United States of America': 'United States' };
const zones = [];
const countries = [];
const index = (list, value) => {
  let i = list.indexOf(value);
  if (i < 0) i = list.push(value) - 1;
  return i;
};
const seen = new Set();
const rows = [];
let dropped = 0;
for (const c of [...cityTimezones.cityMapping].sort((a, b) => (b.pop || 0) - (a.pop || 0))) {
  const zone = c.timezone && canonical(c.timezone);
  if (!zone || !c.city) { dropped++; continue; }
  const key = `${c.city}|${c.province}|${c.iso2}`;
  if (seen.has(key)) continue;
  seen.add(key);
  // [city, plain-letters spelling if different, region, country index, zone index]
  rows.push([c.city, c.city_ascii && c.city_ascii !== c.city ? c.city_ascii : 0, c.province || '', index(countries, SHORT[c.country] || c.country), index(zones, zone)]);
}
writeFileSync('web/data/cities.json', `${JSON.stringify({ zones, countries, cities: rows })}\n`);
console.log(`cities.json: ${rows.length} places, ${zones.length} zones, ${dropped} dropped (no usable zone); browser knows ${known.size} zones`);
