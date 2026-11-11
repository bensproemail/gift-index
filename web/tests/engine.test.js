// The web engine must reproduce the Python engine: positions, chart facts, the full report and the clock.
import { readFileSync } from 'node:fs';
import { describe as group, expect, it } from 'vitest';
import { localToUtc } from '../engine/clock.js';
import { decodeEphem } from '../engine/ephem.js';
import { report } from '../engine/report.js';
import { chartUnits, jdFromMs } from '../engine/sky.js';
import { renderText } from '../engine/text.js';

const here = new URL('.', import.meta.url);
const ref = JSON.parse(readFileSync(new URL('../data/ref.json', here), 'utf8'));
const table = decodeEphem(new Uint8Array(readFileSync(new URL('../data/ephem.bin', here))));
const fx = JSON.parse(readFileSync(new URL('./fixtures.json', here), 'utf8'));

group('positions from the baked table', () => {
  it('match the Python engine on 1,500 random moments', () => {
    let placements = 0;
    let exact = 0;
    let toneLevel = 0;
    let worst = 0;
    for (const [ms, ...want] of fx.units) {
      const got = chartUnits(table, jdFromMs(ms));
      for (let i = 0; i < 26; i++) {
        placements++;
        const gap = Math.min(Math.abs(got[i] - want[i]), 69120 - Math.abs(got[i] - want[i]));
        worst = Math.max(worst, gap);
        if (gap === 0) exact++;
        if (Math.floor(got[i] / 5) === Math.floor(want[i] / 5)) toneLevel++;
      }
    }
    expect(worst).toBeLessThanOrEqual(1); // never more than one Base step apart
    expect(exact / placements).toBeGreaterThan(0.999); // Base level
    expect(toneLevel / placements).toBeGreaterThan(0.9999); // gate, line, Color and Tone
  });
});

group('the full report', () => {
  const strip = (r) => {
    const copy = structuredClone(r);
    delete copy.moment.design_ms;
    delete copy.moment.design_utc;
    for (const side of ['personality', 'design']) for (const p of Object.values(copy.chart[side])) delete p.base;
    return copy;
  };
  it('matches the Python engine field by field', () => {
    expect(fx.reports.length).toBeGreaterThan(100);
    for (const { ms, report: want } of fx.reports) {
      const got = report(ref, table, ms);
      expect(Math.abs(got.moment.design_ms - want.moment.design_ms)).toBeLessThan(500);
      expect(strip(got)).toEqual(strip(want));
    }
  });

  it('gives the Field Guide worked example for the Sample Reader', () => {
    const r = report(ref, table, fx.sample_reader_ms);
    expect(r.headline.label).toBe('Generator · Emotional · Single · 3/6');
    expect([r.headline.living_one_in, r.headline.tier, r.headline.cohort_one_in]).toEqual([1206, 'Rare', 943]);
    expect(r.chart.personality.Sun).toEqual({ gate: 63, line: 3, color: 6, tone: 5, base: 2 });
    expect(r.families[0]).toMatchObject({ family: 'Caretaker', score: 2, lead: true });
    expect(r.gene_keys.map((k) => `${k.gate} ${k.gift}`)).toEqual(['63 Inquiry', '64 Imagination', '5 Patience', '35 Adventure']);
  });

  it('writes the same copy-as-text lines as the Python command', () => {
    const lines = renderText(report(ref, table, fx.sample_reader_ms), 'RECEIPT', ref.claims.arrow_names);
    expect(lines.slice(1)).toEqual(fx.sample_text);
  });

  it('still gives a chart, without the birth-year view, for births after the counted years', () => {
    const late = fx.reports.filter((x) => x.report.moment.birth_year > 2026);
    expect(late.length).toBeGreaterThan(3);
    for (const { ms } of late) expect(report(ref, table, ms).headline.cohort_share).toBeNull();
  });
});

group('the clock', () => {
  it('agrees with the Python time-zone database on every case', () => {
    for (const { input, expect: want } of fx.clocks) {
      const got = localToUtc(...input);
      expect({ input, status: got.status, ms: got.ms, ms_second: got.ms_second, offset_minutes: got.offset_minutes })
        .toEqual({ input, ...want });
    }
  });
});
