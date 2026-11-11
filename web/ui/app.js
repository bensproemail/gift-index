// Starts the lookup page: unpacks the built-in data, wires the form, and shows the reading.
import { decodeEphem } from '../engine/ephem.js';
import { report } from '../engine/report.js';
import { renderText } from '../engine/text.js';
import { byId, chip, h } from './dom.js';
import { setupForm } from './form.js';
import { resultNodes } from './view.js';

const LEGEND = [
  ['COUNT', 'Our own count of calculated charts, made for this study'],
  ['RA', 'Ra Uru Hu, Jovian Archive or IHDS original teaching'],
  ['BOOK', 'A published book'],
  ['TEACHER', 'Later teachers, blogs and podcasts'],
  ['GK', 'Gene Keys by Richard Rudd, a separate system'],
  ['MINE', 'Claude’s own arithmetic or proposal'],
];
// The made-up Sample Reader from the Field Guide. Not a real person.
const SAMPLE = { year: 1980, month: 3, day: 4, hour12: 7, minute: 42, pm: false, place: 'Racine, Wisconsin, United States', zone: 'America/Chicago' };

function bytesFromBase64(text) {
  const bin = atob(text.trim());
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function copyButton(lines) {
  const button = h('button', { type: 'button', class: 'copy' }, 'Copy this reading as text');
  const wrap = h('div', { class: 'copywrap' }, button);
  button.addEventListener('click', async () => {
    const text = lines.join('\n');
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = 'Copied';
    } catch {
      const box = h('textarea', { class: 'copytext', readonly: true, 'aria-label': 'The reading as text' });
      box.value = text;
      wrap.replaceChildren(h('p', { class: 'hint' }, 'Copying is blocked here. Select the text below and copy it.'), box);
      box.select();
    }
  });
  return wrap;
}

function start() {
  const ref = JSON.parse(byId('data-ref').textContent);
  const cities = JSON.parse(byId('data-cities').textContent);
  const table = decodeEphem(bytesFromBase64(byId('data-ephem').textContent));
  byId('legend').append(...LEGEND.flatMap(([k, v]) => [h('dt', null, chip(k)), h('dd', null, v)]));
  byId('source-line').textContent = `Counted charts: ${ref.source.n_charts.toLocaleString('en-US')}, births ${ref.source.years[0]} to ${ref.source.years[1]}. `
    + `Planet positions: Swiss Ephemeris, baked into this page. Data stamp ${ref.source.results_sha}.`;
  const show = (ms, receipt, isExample, scroll) => {
    const result = byId('result');
    try {
      const rep = report(ref, table, ms);
      result.replaceChildren(...resultNodes(ref, rep, receipt, isExample).filter(Boolean),
        copyButton(renderText(rep, receipt, ref.claims.arrow_names)));
    } catch (err) {
      console.error(err);
      result.replaceChildren(h('p', { class: 'card' }, 'This birth moment is outside what the tool covers (births from 1926 through 2030).'));
    }
    if (scroll) result.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  };
  setupForm({ cities, years: [1926, 2030], sample: SAMPLE, onRead: show });
}

start();
