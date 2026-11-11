// Turns a birth date, clock time and time zone into the one true moment (UTC), and names the clock rule used.
// Uses the browser's own time-zone database. Mirrors giftindex/clock.py; a test makes the two agree.

const DAY = 86400000;
const formatters = new Map();

function formatter(zone) {
  if (!formatters.has(zone)) {
    formatters.set(zone, new Intl.DateTimeFormat('en-US', {
      timeZone: zone, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric',
      hour: 'numeric', minute: 'numeric', second: 'numeric', era: 'short',
    }));
  }
  return formatters.get(zone);
}

/** Minutes the zone's clocks are ahead of UTC at a UTC moment. */
export function offsetMinutesAt(zone, utcMs) {
  const p = Object.fromEntries(formatter(zone).formatToParts(new Date(utcMs)).map((x) => [x.type, x.value]));
  const year = p.era === 'BC' ? 1 - Number(p.year) : Number(p.year);
  const wall = Date.UTC(year, Number(p.month) - 1, Number(p.day), Number(p.hour), Number(p.minute), Number(p.second));
  return Math.round((wall - Math.floor(utcMs / 1000) * 1000) / 60000);
}

function zoneLongName(zone, utcMs) {
  try {
    const parts = new Intl.DateTimeFormat('en-US', { timeZone: zone, timeZoneName: 'long' }).formatToParts(new Date(utcMs));
    return parts.find((x) => x.type === 'timeZoneName')?.value ?? '';
  } catch {
    return '';
  }
}

/** The zone's own name for the rule in force, e.g. "Central Standard Time (UTC-06:00)". */
export function ruleText(zone, utcMs) {
  const off = offsetMinutesAt(zone, utcMs);
  const a = Math.abs(off);
  const utc = `UTC${off < 0 ? '-' : '+'}${String(Math.floor(a / 60)).padStart(2, '0')}:${String(a % 60).padStart(2, '0')}`;
  const name = zoneLongName(zone, utcMs);
  return name && !/^GMT|^UTC/.test(name) ? `${name} (${utc})` : utc;
}

/** True when the browser knows this IANA zone name. */
export function zoneKnown(zone) {
  try {
    formatter(zone);
    return true;
  } catch {
    return false;
  }
}

/**
 * Local clock time -> UTC. Returns {status, ms, ms_second, offset_minutes, rule}.
 * status 'ok'; 'gap' = that clock time never happened (clocks jumped forward);
 * 'twice' = it happened twice (clocks went back): ms is the first pass, ms_second the second.
 */
export function localToUtc(year, month, day, hour, minute, zone) {
  const wall = Date.UTC(year, month - 1, day, hour, minute);
  const tries = [...new Set([offsetMinutesAt(zone, wall - DAY), offsetMinutesAt(zone, wall + DAY)])];
  const hits = tries.map((o) => wall - o * 60000).filter((ms) => offsetMinutesAt(zone, ms) * 60000 === wall - ms).sort((x, y) => x - y);
  if (hits.length === 0) return { status: 'gap', ms: null, ms_second: null, offset_minutes: null, rule: null };
  return {
    status: hits.length > 1 ? 'twice' : 'ok',
    ms: hits[0],
    ms_second: hits.length > 1 ? hits[1] : null,
    offset_minutes: offsetMinutesAt(zone, hits[0]),
    rule: ruleText(zone, hits[0]),
  };
}
