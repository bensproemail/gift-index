// Reads the baked planet table (web/data/ephem.bin) and returns each body's longitude at any moment.
// The table is made by giftindex/bake.py from the Python engine, so both sides give the same positions.

const MAGIC = 'GIE1';
const TICKS = 1024; // piece lengths are stored in 1/1024 day

/** Decode the binary table. `bytes` is a Uint8Array. */
export function decodeEphem(bytes) {
  let i = 4;
  if (String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]) !== MAGIC) throw new Error('not a Gift Index ephemeris file');
  const read = () => {
    let n = 0;
    let mult = 1;
    for (;;) {
      const b = bytes[i++];
      n += (b & 0x7f) * mult;
      mult *= 128;
      if (b < 0x80) return n;
    }
  };
  const qInv = read();
  const jd0 = read() / 2;
  const bodies = {};
  let endTicks = 0;
  for (let nb = read(); nb > 0; nb--) {
    let name = '';
    for (let k = read(); k > 0; k--) name += String.fromCharCode(bytes[i++]);
    const count = read();
    const starts = new Float64Array(count);
    const lens = new Float64Array(count);
    const offs = new Int32Array(count + 1);
    const coefs = [];
    let t = 0;
    for (let s = 0; s < count; s++) {
      starts[s] = t;
      lens[s] = read();
      offs[s] = coefs.length;
      for (let k = read(); k > 0; k--) {
        const r = read();
        coefs.push((r % 2 === 0 ? r / 2 : -(r + 1) / 2) / qInv);
      }
      t += lens[s];
    }
    offs[count] = coefs.length;
    bodies[name] = { starts, lens, offs, coefs: Float64Array.from(coefs) };
    endTicks = t;
  }
  return { jd0, jd1: jd0 + endTicks / TICKS, bodies };
}

/** True when the moment (Julian day, UT) is inside the table. */
export function covers(table, jd) {
  return jd >= table.jd0 && jd <= table.jd1;
}

/** Ecliptic longitude in degrees (0 to 360) of one body at a Julian day (UT). */
export function lon(table, name, jd) {
  const b = table.bodies[name];
  const t = (jd - table.jd0) * TICKS;
  const n = b.starts.length;
  if (!(t >= 0) || t > b.starts[n - 1] + b.lens[n - 1]) throw new RangeError('moment outside the baked range');
  let lo = 0;
  let hi = n - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (b.starts[mid] <= t) lo = mid;
    else hi = mid - 1;
  }
  const u = (2 * (t - b.starts[lo])) / b.lens[lo] - 1;
  // Clenshaw sum of the Chebyshev series
  let b1 = 0;
  let b2 = 0;
  for (let k = b.offs[lo + 1] - 1; k > b.offs[lo]; k--) {
    const tmp = 2 * u * b1 - b2 + b.coefs[k];
    b2 = b1;
    b1 = tmp;
  }
  const v = u * b1 - b2 + b.coefs[b.offs[lo]];
  return ((v % 360) + 360) % 360;
}
