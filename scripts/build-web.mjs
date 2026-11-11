#!/usr/bin/env node
// Builds the lookup page as ONE self-contained file: dist/index.html (code, styles and data all inside).
// Usage: npm run build
import { build } from 'esbuild';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';

const read = (p) => readFileSync(new URL(`../${p}`, import.meta.url));
const inlineJson = (p) => JSON.stringify(JSON.parse(read(p).toString('utf8'))).replace(/</g, '\\u003c');

const bundle = await build({ entryPoints: ['web/ui/app.js'], bundle: true, minify: true, format: 'iife', target: 'es2020', write: false });
const js = bundle.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
const parts = {
  '/*__CSS__*/': read('web/ui/style.css').toString('utf8'),
  __REF_JSON__: inlineJson('web/data/ref.json'),
  __CITIES_JSON__: inlineJson('web/data/cities.json'),
  __EPHEM_B64__: read('web/data/ephem.bin').toString('base64'),
  __APP_JS__: js,
};
let html = read('web/ui/page.html').toString('utf8');
for (const [mark, value] of Object.entries(parts)) {
  if (!html.includes(mark)) throw new Error(`page.html is missing the ${mark} marker`);
  html = html.replace(mark, () => value);
}
mkdirSync(new URL('../dist/', import.meta.url), { recursive: true });
writeFileSync(new URL('../dist/index.html', import.meta.url), html);
console.log(`dist/index.html written (${(html.length / 1024).toFixed(0)} KB)`);
