// Cross-check helper: runs an independent Human Design engine (astronomy-engine based) on a list of UTC moments.
// Usage: node js_charts.cjs <path/to/hd-engine.js> < moments.json > charts.json
const fs = require('fs');
const Astronomy = require('astronomy-engine');
const mod = { exports: {} };
new Function('Astronomy', 'module', 'require', fs.readFileSync(process.argv[2], 'utf8'))(Astronomy, mod, require);
const HD = mod.exports;
const moments = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = moments.map((iso) => {
  const c = HD.chart(new Date(iso));
  const side = (s) => HD.BODIES.map((b) => [s[b].gate, s[b].line, s[b].color, s[b].tone, +s[b].lon.toFixed(5)]);
  return { utc: iso, type: c.type, authority: c.authority, definition: c.definition, profile: c.profile, angle: c.angle,
    designUTC: c.designDate.toISOString(), p: side(c.personality), d: side(c.design) };
});
process.stdout.write(JSON.stringify(out));
