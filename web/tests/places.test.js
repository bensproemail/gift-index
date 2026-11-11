// The birthplace search must find towns by their first letters and give the right time zone.
import { readFileSync } from 'node:fs';
import { expect, it } from 'vitest';
import { zoneKnown } from '../engine/clock.js';
import { placeSearch } from '../ui/places.js';

const data = JSON.parse(readFileSync(new URL('../data/cities.json', import.meta.url), 'utf8'));
const search = placeSearch(data);

it('finds the Sample Reader town and its zone', () => {
  expect(search('racine')[0]).toMatchObject({ label: 'Racine, Wisconsin, United States', zone: 'America/Chicago' });
});

it('narrows same-named towns by the region typed after a comma', () => {
  expect(search('springfield').length).toBeGreaterThan(3);
  expect(search('springfield, ill').map((x) => x.label)).toEqual(['Springfield, Illinois, United States']);
});

it('ignores accents and needs at least two letters', () => {
  expect(search('s')).toEqual([]);
  expect(search('sao paulo')[0].zone).toBe('America/Sao_Paulo');
});

it('only lists zones the time-zone database knows', () => {
  expect(data.zones.filter((z) => !zoneKnown(z))).toEqual([]);
});
