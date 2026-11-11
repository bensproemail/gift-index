// Draws the gate wheel: all 64 gates in wheel order, this chart's active gates, and its defined channels.
import { h, s } from './dom.js';

const SIZE = 372;
const MID = SIZE / 2;
const STEP = 360 / 64;

function point(index, radius) {
  const a = ((-90 - (index + 0.5) * STEP) * Math.PI) / 180; // counter-clockwise from the top
  return [MID + radius * Math.cos(a), MID + radius * Math.sin(a)];
}

function tick(index, r1, r2, attrs) {
  const [x1, y1] = point(index, r1);
  const [x2, y2] = point(index, r2);
  return s('line', { x1: x1.toFixed(1), y1: y1.toFixed(1), x2: x2.toFixed(1), y2: y2.toFixed(1), 'stroke-linecap': 'round', ...attrs });
}

function chord(wheel, key, kind) {
  const [a, b] = key.split('-').map(Number);
  const [x1, y1] = point(wheel.indexOf(a), 100);
  const [x2, y2] = point(wheel.indexOf(b), 100);
  const line = (attrs) => s('line', { x1: x1.toFixed(1), y1: y1.toFixed(1), x2: x2.toFixed(1), y2: y2.toFixed(1), 'stroke-width': 2, 'stroke-linecap': 'round', ...attrs });
  if (kind === 1) return [line({ stroke: 'var(--ink)' })];
  if (kind === 2) return [line({ stroke: 'var(--design)' })];
  return [line({ stroke: 'var(--ink)' }), line({ stroke: 'var(--design)', 'stroke-dasharray': '5 7' })];
}

/** The wheel figure for one report. */
export function wheelFigure(ref, rep) {
  const wheel = ref.tables.wheel;
  const c = rep.chart;
  const gatesOf = (side) => new Set(Object.values(c[side]).map((p) => p.gate));
  const pers = gatesOf('personality');
  const des = gatesOf('design');
  const svg = s('svg', { viewBox: `0 0 ${SIZE} ${SIZE}`, role: 'img',
    'aria-label': `Gate wheel: ${rep.n_gates} active gates and ${rep.n_channels} defined channels` });
  svg.append(s('circle', { cx: MID, cy: MID, r: 100, fill: 'none', stroke: 'var(--line)', 'stroke-width': 1 }));
  let wasActive = false;
  let far = false;
  wheel.forEach((gate, i) => {
    svg.append(tick(i, 122, 128, { stroke: 'var(--line)', 'stroke-width': 1.5 }));
    if (des.has(gate)) svg.append(tick(i, 106, 120, { stroke: 'var(--design)', 'stroke-width': 5 }));
    if (pers.has(gate)) svg.append(tick(i, 130, 144, { stroke: 'var(--ink)', 'stroke-width': 5 }));
    if (pers.has(gate) || des.has(gate)) {
      // neighbours that are both active get their numbers on alternating rings so they never collide
      far = far === false && wasActive;
      const [x, y] = point(i, far ? 171 : 157);
      svg.append(s('text', { x: x.toFixed(1), y: (y + 3.5).toFixed(1), 'text-anchor': 'middle', 'font-size': 11,
        'font-family': 'var(--cond)', fill: 'var(--ink)' }, gate));
      wasActive = true;
    } else {
      wasActive = false;
      far = false;
    }
  });
  for (const key of c.channels) svg.append(...chord(wheel, key, c.channel_kind[key]));
  svg.append(
    s('circle', { cx: MID, cy: MID, r: 46, fill: 'var(--card)' }),
    s('text', { x: MID, y: MID + 6, 'text-anchor': 'middle', 'font-size': 44, 'font-weight': 800, 'font-family': 'var(--head)', fill: 'var(--ink)' }, c.profile),
    s('text', { x: MID, y: MID + 28, 'text-anchor': 'middle', 'font-size': 11, 'font-family': 'var(--cond)', fill: 'var(--muted)', 'letter-spacing': 1.6 }, c.type.toUpperCase()));
  const sun = (side, r, color) => {
    const [x, y] = point(wheel.indexOf(c[side].Sun.gate), r);
    return s('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 4.5, fill: 'var(--card)', stroke: color, 'stroke-width': 2.5 });
  };
  svg.append(sun('design', 113, 'var(--design)'), sun('personality', 137, 'var(--ink)'));
  return h('figure', { class: 'wheel' }, svg,
    h('figcaption', null,
      h('span', null, 'Personality (conscious)'), h('span', { class: 'd' }, 'Design (unconscious)'),
      h('span', { class: 'c' }, 'Defined channel'), 'Rings mark the two Suns.'));
}
