// The full Gift Index report for one birth moment. Mirrors giftindex/report.py + reading.py field by field.
// A test (web/tests/engine.test.js) compares this output with the Python engine's, so keep them in step.
import { activeGates, describe } from './chart.js';
import { chartUnits, designJd, jdFromMs, msFromJd } from './sky.js';

const MADE = ['', 'conscious', 'unconscious', 'mixed'];

function isoMinute(ms) {
  return `${new Date(Math.round(ms)).toISOString().slice(0, 16)}Z`;
}

function oneIn(share) {
  return share > 0 ? Math.round(1 / share) : null;
}

/** Headline tier from the share of living people (the Field Guide's four bands). */
export function tier(ref, share) {
  if (share <= 0) return 'Not seen';
  return ref.rules.tiers.find(([floor]) => share >= floor)[1];
}

/** Counts for people born within two years: {share, hits, charts, years} or nulls outside the counted years. */
function cohort(ref, code, year) {
  const axis = ref.count.year_axis;
  const yi = axis.indexOf(year);
  if (yi < 0) return { yi, share: null, hits: null, charts: null, years: null };
  let hits = 0;
  let charts = 0;
  const from = Math.max(0, yi - 2);
  const to = Math.min(axis.length - 1, yi + 2);
  for (let y = from; y <= to; y++) {
    const row = ref.count.joint_by_year[y];
    for (let k = 0; k < row.length; k += 2) {
      charts += row[k + 1];
      if (row[k] === code) hits += row[k + 1];
    }
  }
  return { yi, share: hits / charts, hits, charts, years: [axis[from], axis[to]] };
}

function headline(ref, chart, year) {
  const T = ref.tables;
  const code = ((T.types.indexOf(chart.type) * 8 + T.authorities.indexOf(chart.authority)) * 5
    + T.definitions.indexOf(chart.definition)) * 12 + T.profile_index[chart.profile];
  const living = ref.count.joint[String(code)] ?? 0;
  const c = cohort(ref, code, year);
  return {
    yi: c.yi,
    headline: {
      label: `${chart.type} · ${chart.authority} · ${chart.definition} · ${chart.profile}`,
      living_share: living,
      living_one_in: oneIn(living),
      tier: tier(ref, living),
      cohort_share: c.share,
      cohort_one_in: c.share === null ? null : oneIn(c.share),
      cohort_hits: c.hits,
      cohort_charts: c.charts,
      cohort_years: c.years,
    },
  };
}

function channelRows(ref, chart, yi) {
  const familyOf = familyOfChannel(ref);
  return chart.channels.map((key) => {
    const [claim, offCourse, page] = ref.claims.channel[key];
    return {
      channel: key,
      name: ref.tables.channel_names[key],
      family: familyOf[key],
      living: ref.count.channels[key].share,
      cohort: yi < 0 ? null : ref.count.channels[key].by_year[yi],
      made: MADE[chart.channel_kind[key]],
      claim,
      off_course: offCourse,
      page,
      label: ref.claims.channel_label,
    };
  });
}

function familyOfChannel(ref) {
  const out = {};
  for (const [family, circuit] of ref.tables.families) for (const key of ref.tables.circuits[circuit]) out[key] = family;
  return out;
}

function familyRows(ref, chart) {
  const act = new Set(activeGates(chart));
  const familyOf = familyOfChannel(ref);
  const rows = ref.tables.families.map(([family, circuit]) => {
    let score = 0;
    for (const [a, b] of ref.tables.channels) {
      if (familyOf[`${a}-${b}`] !== family) continue;
      score += act.has(a) && act.has(b) ? 2 : act.has(a) || act.has(b) ? 1 : 0;
    }
    const counted = ref.count.families[family];
    const [claim, downside, label] = ref.claims.family[family];
    return { family, score, max: counted.max_score, top_share: counted.score_top_share[String(score)], claim, downside, label, circuit };
  });
  rows.sort((x, y) => x.top_share - y.top_share);
  const lead = rows[0].top_share;
  return rows.map((r) => ({
    family: r.family, score: r.score, max: r.max, top_share: r.top_share, lead: r.score > 0 && r.top_share === lead,
    claim: r.claim, downside: r.downside, label: r.label, circuit: r.circuit,
  }));
}

function facts(T, units) {
  const c = describe(T, units);
  const sun = c.personality.Sun;
  return {
    type: c.type, authority: c.authority, definition: c.definition, profile: c.profile, channels: c.channels,
    gates: activeGates(c), sun_color: [sun.gate, sun.line, sun.color], sun_tone: [sun.gate, sun.line, sun.color, sun.tone],
    arrows: c.arrows,
  };
}

/** For each watched fact: the smallest birth-time error (minutes, either way) that changes it, or null. */
export function sensitivity(ref, table, jd) {
  const base = facts(ref.tables, chartUnits(table, jd));
  const out = Object.fromEntries(Object.keys(base).map((k) => [k, null]));
  for (const minutes of ref.rules.shift_minutes) {
    for (const sign of [-1, 1]) {
      const other = facts(ref.tables, chartUnits(table, jd + (sign * minutes) / 1440));
      for (const k of Object.keys(base)) {
        if (out[k] === null && JSON.stringify(other[k]) !== JSON.stringify(base[k])) out[k] = minutes;
      }
    }
  }
  return out;
}

/** Everything the lookup tool shows for one moment (milliseconds since 1970, UTC). */
export function report(ref, table, ms) {
  const jd = jdFromMs(ms);
  const year = new Date(ms).getUTCFullYear();
  const chart = describe(ref.tables, chartUnits(table, jd));
  const designMs = Math.round(msFromJd(designJd(table, jd)));
  const h = headline(ref, chart, year);
  return {
    moment: { utc: isoMinute(ms), design_utc: isoMinute(designMs), design_ms: designMs, birth_year: year },
    chart,
    n_gates: activeGates(chart).length,
    n_channels: chart.channels.length,
    headline: h.headline,
    channels: channelRows(ref, chart, h.yi),
    families: familyRows(ref, chart),
    gene_keys: ref.claims.gk_spheres.map(([sphere, side, body]) => ({
      sphere,
      source: `${side[0].toUpperCase()}${side.slice(1)} ${body}`,
      gate: chart[side][body].gate,
      gift: ref.claims.gk_gift[String(chart[side][body].gate)],
    })),
    sensitivity: sensitivity(ref, table, jd),
  };
}
