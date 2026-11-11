// Planet positions for a birth moment: 13 Personality + 13 Design placements as wheel units.
// Mirrors giftindex/positions.py. Design = the moment the Sun stood exactly 88 degrees earlier.
import { lon } from './ephem.js';

const START_DEG = 302;
const UNITS_PER_DEG = 192;
const TOTAL_UNITS = 69120;
// BODIES order: Sun, Earth, NorthNode, SouthNode, Moon, Mercury ... Pluto. null = opposite the one before.
const ORDER = ['Sun', null, 'NorthNode', null, 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'];

export function jdFromMs(ms) {
  return ms / 86400000 + 2440587.5;
}

export function msFromJd(jd) {
  return (jd - 2440587.5) * 86400000;
}

/** 13 longitudes (degrees) in BODIES order. */
export function longitudes(table, jd) {
  const out = [];
  for (const name of ORDER) {
    out.push(name === null ? (out[out.length - 1] + 180) % 360 : lon(table, name, jd));
  }
  return out;
}

/** Julian day when the Sun was exactly 88 degrees of longitude before its birth position. */
export function designJd(table, jd) {
  const target = (((lon(table, 'Sun', jd) - 88) % 360) + 360) % 360;
  let t = jd - 88 / 0.98565;
  const h = 1 / 1024;
  for (let i = 0; i < 30; i++) {
    const diff = ((((lon(table, 'Sun', t) - target + 180) % 360) + 360) % 360) - 180;
    if (Math.abs(diff) < 1e-9) break;
    const speed = (((((lon(table, 'Sun', t + h) - lon(table, 'Sun', t - h) + 180) % 360) + 360) % 360) - 180) / (2 * h);
    t -= diff / speed;
  }
  return t;
}

/** Longitude -> wheel unit 0..69119 (gate, line, color, tone, base packed together). */
export function toUnit(longitude) {
  const u = Math.floor(((((longitude - START_DEG) % 360) + 360) % 360) * UNITS_PER_DEG);
  return u < TOTAL_UNITS ? u : TOTAL_UNITS - 1;
}

/** 26 wheel units: Personality (13) then Design (13). */
export function chartUnits(table, jd) {
  return [...longitudes(table, jd).map(toUnit), ...longitudes(table, designJd(table, jd)).map(toUnit)];
}
