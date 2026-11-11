// Turns 26 wheel units into chart facts (gates, channels, centers, type, authority, ...) for ONE chart.
// Mirrors giftindex/chart.py describe(). All tables come from ref.json so there is one source of truth.

const UNITS_PER_GATE = 1080;
const P_SUN = 0;
const P_NODE = 2;
const D_SUN = 13;
const D_NODE = 15;

/** One placement: wheel unit -> gate, line, color, tone, base. */
export function place(T, unit) {
  const r = unit % UNITS_PER_GATE;
  return {
    gate: T.wheel[Math.floor(unit / UNITS_PER_GATE)],
    line: Math.floor(r / 180) + 1,
    color: Math.floor((r % 180) / 30) + 1,
    tone: Math.floor((r % 30) / 5) + 1,
    base: (r % 5) + 1,
  };
}

function centerIndexOfGate(T) {
  const out = {};
  T.center_names.forEach((c, i) => T.centers[c].forEach((g) => { out[g] = i; }));
  return out;
}

/** Connected groups among defined centers. Returns a label per center (lowest center index in its group). */
function groupLabels(defined, links) {
  const labels = defined.map((d, i) => (d ? i : 99));
  for (let pass = 0; pass < 8; pass++) {
    for (const [a, b] of links) {
      const mn = Math.min(labels[a], labels[b]);
      labels[a] = mn;
      labels[b] = mn;
    }
  }
  return labels;
}

function typeIndex(defined, labels, C) {
  const linked = (c) => defined[c] && defined[C.Throat] && labels[c] === labels[C.Throat];
  const motorThroat = linked(C.Heart) || linked(C.SolarPlexus) || linked(C.Root) || linked(C.Sacral);
  if (!defined.some(Boolean)) return 4; // Reflector
  if (defined[C.Sacral]) return motorThroat ? 1 : 0; // Manifesting Generator : Generator
  return motorThroat ? 3 : 2; // Manifestor : Projector
}

function authorityIndex(defined, type, C) {
  if (!defined.some(Boolean)) return 7; // Lunar
  if (defined[C.SolarPlexus]) return 0;
  if (defined[C.Sacral]) return 1;
  if (defined[C.Spleen]) return 2;
  if (defined[C.Heart]) return type === 3 ? 3 : 4; // Ego Manifested : Ego Projected
  if (defined[C.G]) return 5;
  return 6; // Mental
}

/** All chart facts for 26 wheel units. `T` is ref.tables. */
export function describe(T, units) {
  const places = units.map((u) => place(T, u));
  const actP = new Set(places.slice(0, 13).map((p) => p.gate));
  const actD = new Set(places.slice(13).map((p) => p.gate));
  const act = new Set([...actP, ...actD]);
  const C = Object.fromEntries(T.center_names.map((c, i) => [c, i]));
  const gateCenter = centerIndexOfGate(T);

  const defined = T.center_names.map(() => false);
  const links = [];
  const channels = [];
  const channelKind = {};
  T.channels.forEach(([a, b]) => {
    if (!(act.has(a) && act.has(b))) return;
    const key = `${a}-${b}`;
    const p = actP.has(a) && actP.has(b);
    const d = actD.has(a) && actD.has(b);
    channels.push(key);
    channelKind[key] = p && !d ? 1 : d && !p ? 2 : 3; // conscious, unconscious, mixed
    defined[gateCenter[a]] = true;
    defined[gateCenter[b]] = true;
    links.push([gateCenter[a], gateCenter[b]]);
  });
  const labels = groupLabels(defined, links);
  const groups = defined.filter((d, i) => d && labels[i] === i).length;
  const type = typeIndex(defined, labels, C);
  const pl = places[P_SUN].line;
  const dl = places[D_SUN].line;
  const angle = pl === 4 && dl === 1 ? 1 : pl >= 5 ? 2 : 0;
  const side = (from) => Object.fromEntries(T.bodies.map((b, i) => [b, places[from + i]]));
  return {
    type: T.types[type],
    authority: T.authorities[authorityIndex(defined, type, C)],
    definition: T.definitions[Math.min(groups, 4)],
    profile: `${pl}/${dl}`,
    angle: T.angles[angle],
    centers: T.center_names.filter((_, i) => defined[i]),
    channels,
    channel_kind: channelKind,
    arrows: [P_SUN, P_NODE, D_SUN, D_NODE].map((i) => (places[i].tone >= 4 ? 'R' : 'L')).join(''),
    personality: side(0),
    design: side(13),
  };
}

/** The set of different active gates in a described chart, sorted. */
export function activeGates(chart) {
  const s = new Set();
  for (const sideName of ['personality', 'design']) for (const p of Object.values(chart[sideName])) s.add(p.gate);
  return [...s].sort((a, b) => a - b);
}
