// Builds the reading on the page from one report (see web/engine/report.js for the report's fields).
import { commas, oneInText, pct } from '../engine/text.js';
import { chip, h } from './dom.js';
import { wheelFigure } from './wheel.js';

const TIER_LEVEL = { Common: 1, Uncommon: 2, Rare: 3, 'Very rare': 4, 'Not seen': 4 };
const TIER_RANGE = {
  Common: 'more than 1 in 100', Uncommon: '1 in 100 to 1 in 1,000', Rare: '1 in 1,000 to 1 in 10,000',
  'Very rare': 'under 1 in 10,000', 'Not seen': 'not in the count',
};
const CHECK_NAMES = {
  type: 'Type', authority: 'Authority', definition: 'Definition', profile: 'Profile', channels: 'Channels',
  gates: 'Gates', sun_color: "Sun's Color", sun_tone: "Sun's Tone", arrows: 'Arrows',
};
const BODY_NAMES = { NorthNode: 'North Node', SouthNode: 'South Node' };

function card(title, sub, ...kids) {
  return h('section', { class: 'card' }, h('h2', null, title, sub ? h('small', null, sub) : null), ...kids);
}

function cohortBlock(hd) {
  if (!hd.cohort_years) {
    return h('div', { class: 'second' }, h('span', { class: 'kicker' }, 'Born within two years'),
      h('p', { class: 'hint' }, 'No birth-year view for this date: the count covers births from 1926 to 2026.'));
  }
  const span = `among people born ${hd.cohort_years[0]} to ${hd.cohort_years[1]}`;
  const basis = `${commas(hd.cohort_hits)} of ${commas(hd.cohort_charts)} counted charts`;
  return h('div', { class: 'second' }, h('span', { class: 'kicker' }, 'Born within two years'),
    h('strong', null, hd.cohort_hits > 0 ? oneInText(hd.cohort_one_in) : 'None counted'),
    h('span', null, `${span} (${basis}).`),
    hd.cohort_hits < 10 ? h('span', { class: 'hint' }, 'Treat this one as rough: it rests on very few charts.') : null);
}

function headlineCard(ref, rep) {
  const hd = rep.headline;
  const level = TIER_LEVEL[hd.tier];
  const seen = hd.living_share > 0;
  return h('section', { class: 'card headline' },
    h('div', { class: 'top' },
      h('div', { class: 'figure' },
        h('span', { class: 'kicker' }, 'Headline rarity ', chip('COUNT')),
        h('p', { class: 'big' }, seen ? oneInText(hd.living_one_in) : 'Not seen',
          h('small', null, seen ? 'among all living people' : `in ${commas(ref.source.n_charts)} counted charts`)),
        h('p', { class: 'tier' }, h('i', { 'aria-hidden': 'true' }, [1, 2, 3, 4].map((n) => h('span', { class: n <= level ? 'on' : '' }))),
          `${hd.tier}: ${TIER_RANGE[hd.tier]}`),
        h('p', { class: 'setup' }, hd.label),
        h('p', { class: 'hint' }, `Type, authority, definition and profile, counted together. The typical setup is shared by about 1 person in ${commas(ref.count.typical_one_in)}.`)),
      wheelFigure(ref, rep)),
    cohortBlock(hd));
}

function fact(label, value, note) {
  return h('div', null, h('dt', null, label), h('dd', null, value, note ? h('small', null, note) : null));
}

function factsCard(ref, rep) {
  const c = rep.chart;
  const shares = ref.count.shares;
  const of = (kind, key) => `${pct(shares[kind][key])} of living people`;
  const arrows = ref.claims.arrow_names.map((n, i) => `${n.split(' (')[0]} ${c.arrows[i] === 'R' ? 'right' : 'left'}`);
  return card('The chart', 'calculated from the birth moment',
    h('dl', { class: 'facts' },
      fact('Type', c.type, of('type', c.type)),
      fact('Authority', c.authority, of('authority', c.authority)),
      fact('Definition', c.definition, of('definition', c.definition)),
      fact('Profile', c.profile, of('profile', c.profile)),
      fact('Cross angle', c.angle, of('angle', c.angle)),
      fact('Defined centers', c.centers.length ? c.centers.join(', ').replace('SolarPlexus', 'Solar Plexus') : 'None'),
      fact('Gates and channels', `${rep.n_gates} different gates`, `${rep.n_channels} defined ${rep.n_channels === 1 ? 'channel' : 'channels'}`),
      fact('Arrows', arrows.slice(0, 2).join(', '), arrows.slice(2).join(', '))),
    h('p', { class: 'hint' }, 'Shares are our own count of living people ', chip('COUNT'), ' Arrow names follow common teaching ', chip('TEACHER')));
}

function channelsCard(rep) {
  if (!rep.channels.length) {
    return card('Channels', 'none defined', h('p', null, 'No channel is defined in this chart. That is what makes it a Reflector.'));
  }
  const rows = rep.channels.map((ch) => h('div', { class: 'rowitem' },
    h('div', { class: 'rowhead' }, h('h3', null, h('em', null, ch.channel), ch.name), h('span', { class: `made ${ch.made}` }, ch.made)),
    h('p', { class: 'pair' }, h('span', null, h('b', null, pct(ch.living)), ' of living people'),
      ch.cohort === null ? null : h('span', null, h('b', null, pct(ch.cohort)), ` of people born near ${rep.moment.birth_year}`),
      h('span', null, 'counts toward ', h('b', null, ch.family))),
    h('p', { class: 'claim' }, h('b', null, 'Gift claim: '), `${ch.claim}. `, h('span', { class: 'down' }, h('b', null, 'Off course: '), `${ch.off_course}. `),
      chip(`${ch.label} p.${ch.page}`))));
  return card('Channels', `${rep.channels.length} defined`, h('div', { class: 'rows' }, rows),
    h('p', { class: 'hint' }, 'Conscious = both gates on the Personality side. Unconscious = both on the Design side. Mixed = one of each. Shares ', chip('COUNT')));
}

function familyRow(f) {
  const scored = f.score > 0;
  return h('div', { class: f.lead ? 'rowitem lead' : 'rowitem' },
    h('div', { class: 'rowhead' }, h('h3', null, f.family, f.lead ? [' ', h('span', { class: 'pill' }, 'Lead gift')] : null),
      h('span', { class: 'val' }, scored ? `Top ${pct(f.top_share)}` : 'No score')),
    h('div', { class: 'track', role: 'img', 'aria-label': scored ? `Top ${pct(f.top_share)} of living people` : 'No score' },
      h('span', { style: `width:${scored ? Math.max(2, 100 - f.top_share).toFixed(1) : 0}%` })),
    h('p', { class: 'pair' }, h('span', null, h('b', null, `${f.score} of ${f.max}`), ' points'), h('span', null, f.circuit.replace(' / ', ', '), ' circuit')),
    scored ? h('p', { class: 'claim' }, h('b', null, 'Claim: '), `${f.claim} `, h('span', { class: 'down' }, h('b', null, 'Downside: '), `${f.downside}. `), chip(f.label)) : null);
}

function familiesCard(rep) {
  return card('Seven gift scores', 'claims of the tradition, not proven',
    h('div', { class: 'rows' }, rep.families.map(familyRow)),
    h('p', { class: 'hint' }, 'A defined channel scores 2 points for its family and a half channel scores 1. "Top X%" is the share of living people with that score or higher ',
      chip('COUNT'), ' The family names are our own labels on Ra’s seven circuit groups ', chip('MINE')));
}

function keysCard(rep) {
  return card('Gene Keys layer', 'a separate system by Richard Rudd',
    h('div', { class: 'keys' }, rep.gene_keys.map((k) => h('div', null, h('span', { class: 'n' }, k.gate), h('span', { class: 'g' }, k.gift),
      h('span', { class: 's' }, `${k.sphere} · ${k.source}`)))),
    h('p', { class: 'hint' }, 'Shown beside the reading only. It never changes a rarity figure or a gift score ', chip('GK')));
}

function checkCard(ref, rep) {
  const rows = Object.entries(rep.sensitivity).map(([k, v]) => h('tr', null, h('th', { scope: 'row' }, CHECK_NAMES[k]),
    h('td', { class: v === null ? 'holds' : 'moves' }, v === null ? 'Holds up to 60 min' : `Changes within ${v} min`)));
  const base = ref.count.birth_time_error['5'].sun_base;
  return card('If the birth time is off', 'this chart, re-run at other times',
    h('table', { class: 'check' }, h('tbody', null, rows)),
    h('p', { class: 'hint' }, `We re-ran this chart 5, 15, 30 and 60 minutes earlier and later. Color, Tone and Base need a time right to a few minutes: across all charts a 5-minute error changes the Sun’s Base in ${pct(base)} of them `, chip('COUNT')));
}

function fineCard(ref, rep) {
  const cell = (p, cls) => h('td', { class: cls }, h('b', null, `${p.gate}.${p.line}`), h('small', null, `${p.color} \u00b7 ${p.tone} \u00b7 ${p.base}`));
  const rows = ref.tables.bodies.map((b) => h('tr', null, h('td', null, BODY_NAMES[b] || b),
    cell(rep.chart.personality[b], ''), cell(rep.chart.design[b], 'dside')));
  const head = (t) => h('th', { scope: 'col' }, t, h('small', null, 'gate.line, then Color \u00b7 Tone \u00b7 Base'));
  return card('All 26 placements', 'down to Color, Tone and Base',
    h('table', { class: 'fine' }, h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Body'), head('Personality'), head('Design'))), h('tbody', null, rows)),
    h('p', { class: 'hint' }, 'Color, Tone and Base are spread evenly, so they carry no rarity claim. The two Node rows are the least certain: calculators often disagree on a Node\u2019s Tone.'));
}

/** All result sections for one report. */
export function resultNodes(ref, rep, receipt, isExample) {
  return [
    isExample ? h('p', { class: 'example' }, 'Example reading: the made-up Sample Reader. Change the birth details above to run a real one.') : null,
    h('p', { class: 'receipt' }, h('b', null, 'Read from: '), receipt, h('br'), h('b', null, 'Design moment: '), `${rep.moment.design_utc.replace('T', ' ').replace('Z', '')} UTC`),
    headlineCard(ref, rep), factsCard(ref, rep), channelsCard(rep), familiesCard(rep), keysCard(rep), checkCard(ref, rep), fineCard(ref, rep),
  ];
}
