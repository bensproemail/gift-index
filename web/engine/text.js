// The report as plain text lines (for the Copy button). Mirrors render() in giftindex/lookup.py line for line.

const NAMES = {
  type: 'Type', authority: 'Authority', definition: 'Definition', profile: 'Profile', channels: 'Channels',
  gates: 'Gates', sun_color: "Sun's Color", sun_tone: "Sun's Tone", arrows: 'Arrows',
};

export function pct(x) {
  return `${x.toFixed(x >= 1 ? 1 : 2)}%`;
}

export function commas(n) {
  return n.toLocaleString('en-US');
}

export function oneInText(n) {
  return n === null ? 'not seen in the count' : `1 in ${commas(n)}`;
}

function rarityLines(rep) {
  const h = rep.headline;
  const out = ['', 'RARITY (COUNT: our own count of 2,020,000 charts)', `  Headline setup: ${h.label}`,
    `  Among all living people: ${h.living_share > 0 ? oneInText(h.living_one_in) : 'not seen in the count'} (${h.tier})`];
  out.push(h.cohort_years
    ? `  Among people born ${h.cohort_years[0]} to ${h.cohort_years[1]}: ${oneInText(h.cohort_one_in)} (${h.cohort_hits} of ${commas(h.cohort_charts)} charts)`
    : '  Among people born near the same year: not counted (the count covers births 1926 to 2026)');
  for (const ch of rep.channels) {
    const near = ch.cohort === null ? '' : `, ${pct(ch.cohort)} of people born near the same year`;
    out.push(`  Channel ${ch.channel} ${ch.name} (${ch.made}): ${pct(ch.living)} of living people${near}`);
  }
  return out;
}

function giftLines(rep) {
  const out = ['', 'GIFT SCORES (claims of the tradition, not proven; family names are our labels, MINE)'];
  for (const f of rep.families) {
    const standing = f.score === 0 ? 'no score' : `top ${pct(f.top_share)} of living people`;
    out.push(`  ${f.family.padEnd(16)} ${String(f.score).padStart(2)} of ${String(f.max).padEnd(2)}  ${standing}${f.lead ? '  <- lead gift' : ''}`);
    if (f.score > 0) out.push(`      Claim (${f.label}): ${f.claim}  Downside: ${f.downside}`);
  }
  for (const ch of rep.channels) {
    out.push(`  ${ch.channel} ${ch.name} (${ch.label}, p.${ch.page}): ${ch.claim}  Off course: ${ch.off_course}`);
  }
  return out;
}

/** All lines. `arrowNames` is ref.claims.arrow_names. */
export function renderText(rep, receipt, arrowNames) {
  const c = rep.chart;
  const sun = c.personality.Sun;
  const arrows = arrowNames.map((n, i) => `${n} ${c.arrows[i] === 'R' ? 'right' : 'left'}`).join(', ');
  return [
    `READ FROM: ${receipt}`, `Design moment (UTC): ${rep.moment.design_utc}`, '',
    'CHART (calculated)',
    `  Type: ${c.type}   Authority: ${c.authority}   Definition: ${c.definition}`,
    `  Profile: ${c.profile}, ${c.angle} cross`,
    `  Defined centers: ${c.centers.join(', ') || 'none'}`,
    `  Different gates: ${rep.n_gates}   Channels: ${rep.n_channels}`,
    `  Arrows: ${arrows}`,
    `  Personality Sun: gate ${sun.gate}, line ${sun.line}, Color ${sun.color}, Tone ${sun.tone}, Base ${sun.base}`,
    ...rarityLines(rep),
    ...giftLines(rep),
    '', 'GENE KEYS LAYER (GK: a separate system by Richard Rudd)',
    ...rep.gene_keys.map((k) => `  ${k.sphere} (${k.source}): ${k.gate} ${k.gift}`),
    '', 'IF THE BIRTH TIME IS OFF (smallest error that changes each fact, checked up to 60 minutes)',
    ...Object.entries(rep.sensitivity).map(([k, v]) => `  ${NAMES[k].padEnd(12)} ${v === null ? 'holds' : `changes within ${v} minutes`}`),
  ];
}
