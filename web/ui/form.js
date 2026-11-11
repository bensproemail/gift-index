// The birth-details form: explicit fields, a live read-back of what was typed, and the clock rule that applies.
import { localToUtc, ruleText } from '../engine/clock.js';
import { byId, h } from './dom.js';
import { placeSearch, zoneNames } from './places.js';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const pad = (n) => String(n).padStart(2, '0');

function whole(id, lo, hi) {
  const raw = byId(id).value.trim();
  const n = Number(raw);
  return raw !== '' && Number.isInteger(n) && n >= lo && n <= hi ? n : null;
}

/** Read the typed fields. Returns {error} or {year, month, day, hour, minute, zone, place, text}. */
function readFields(state, years) {
  const month = Number(byId('f-month').value);
  const day = whole('f-day', 1, 31);
  const year = whole('f-year', years[0], years[1]);
  const h12 = whole('f-hour', 1, 12);
  const minute = whole('f-minute', 0, 59);
  const pm = byId('f-pm').checked;
  if (byId('f-year').value.trim() !== '' && year === null) return { error: `The year must be between ${years[0]} and ${years[1]}. That is the span this tool covers.` };
  if (day === null || year === null) return { error: 'Enter the day and the year.' };
  const check = new Date(Date.UTC(year, month - 1, day));
  if (check.getUTCMonth() !== month - 1) return { error: `${MONTHS[month - 1]} ${year} has no day ${day}.` };
  if (h12 === null || minute === null) return { error: 'Enter the hour (1 to 12) and the minute (0 to 59).' };
  if (!byId('f-am').checked && !pm) return { error: 'Choose AM or PM.' };
  if (!state.zone) return { error: 'Choose the birthplace from the list, or pick a time zone.' };
  const hour = (h12 % 12) + (pm ? 12 : 0);
  const text = `${DAYS[check.getUTCDay()]}, ${MONTHS[month - 1]} ${day}, ${year} at ${h12}:${pad(minute)} ${pm ? 'PM' : 'AM'}`;
  return { year, month, day, hour, minute, zone: state.zone, place: state.place, text };
}

/** Typed fields -> the moment. Returns {error} or {ms, receipt, readback, twice}. */
function resolve(state, years) {
  const f = readFields(state, years);
  if (f.error) return f;
  const t = localToUtc(f.year, f.month, f.day, f.hour, f.minute, f.zone);
  if (t.status === 'gap') return { error: `${f.text} never happened in ${f.place}: the clocks jumped forward past it. Check the time.` };
  const second = t.status === 'twice' && byId('f-pass2').checked;
  const ms = second ? t.ms_second : t.ms;
  const rule = ruleText(f.zone, ms);
  const utc = new Date(ms).toISOString().slice(0, 16).replace('T', ' ');
  return {
    ms, twice: t.status === 'twice' ? [ruleText(f.zone, t.ms), ruleText(f.zone, t.ms_second)] : null,
    readback: [h('b', null, f.text), h('br'), `${f.place} · ${rule}`],
    receipt: `${f.text} · ${f.place} · clock rule: ${rule} · UTC ${utc}`,
  };
}

function setupPlace(state, cities, refresh) {
  const input = byId('f-place');
  const list = byId('place-list');
  const search = placeSearch(cities);
  let options = [];
  let active = -1;
  const close = () => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); active = -1; };
  const choose = (o) => {
    state.zone = o.zone;
    state.place = o.label;
    input.value = o.label;
    byId('place-chosen').textContent = `Time zone: ${o.zone}`;
    close();
    refresh();
  };
  const paint = () => {
    list.replaceChildren(...options.map((o, i) => {
      const li = h('li', { role: 'option', id: `place-opt-${i}`, 'aria-selected': i === active ? 'true' : 'false' }, o.city, h('small', null, o.where));
      li.addEventListener('pointerdown', (e) => { e.preventDefault(); choose(o); });
      return li;
    }));
    list.hidden = options.length === 0;
    input.setAttribute('aria-expanded', String(options.length > 0));
  };
  input.addEventListener('input', () => {
    state.zone = null;
    state.place = null;
    byId('place-chosen').textContent = '';
    options = search(input.value);
    active = -1;
    paint();
    refresh();
  });
  input.addEventListener('keydown', (e) => {
    if (list.hidden) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      active = (active + (e.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
      paint();
    } else if (e.key === 'Enter' && options.length) {
      e.preventDefault();
      choose(options[Math.max(active, 0)]);
    } else if (e.key === 'Escape') close();
  });
  input.addEventListener('blur', () => setTimeout(close, 150));
  return choose;
}

function setupZone(state, cities, refresh) {
  const select = byId('f-zone');
  select.append(h('option', { value: '' }, 'Choose a time zone'), ...zoneNames(cities).map((z) => h('option', { value: z }, z.replaceAll('_', ' '))));
  byId('zone-toggle').addEventListener('click', () => {
    byId('zone-field').hidden = !byId('zone-field').hidden;
  });
  select.addEventListener('change', () => {
    if (!select.value) return;
    state.zone = select.value;
    state.place = `time zone ${select.value.replaceAll('_', ' ')}`;
    byId('f-place').value = '';
    byId('place-chosen').textContent = `Using the time zone you picked: ${select.value.replaceAll('_', ' ')}`;
    refresh();
  });
}

/**
 * Wire up the form. `sample` = {year, month, day, hour12, minute, pm, place, zone} fills the first view.
 * `onRead(ms, receipt, isExample)` is called on submit and once at start for the example.
 */
export function setupForm({ cities, years, sample, onRead }) {
  const state = { zone: null, place: null };
  let example = true;
  byId('f-month').append(...MONTHS.map((m, i) => h('option', { value: i + 1 }, m)));
  const refresh = () => {
    const r = resolve(state, years);
    const box = byId('readback');
    box.className = r.error ? 'readback bad' : 'readback';
    box.replaceChildren(...(r.error ? [r.error] : r.readback));
    byId('twice').hidden = !r.twice;
    if (r.twice) {
      byId('pass1-label').textContent = `First: ${r.twice[0]}`;
      byId('pass2-label').textContent = `Second: ${r.twice[1]}`;
    }
    byId('go').disabled = Boolean(r.error);
    return r;
  };
  const choose = setupPlace(state, cities, () => { example = false; refresh(); });
  setupZone(state, cities, () => { example = false; refresh(); });
  byId('f-month').value = sample.month;
  byId('f-day').value = sample.day;
  byId('f-year').value = sample.year;
  byId('f-hour').value = sample.hour12;
  byId('f-minute').value = pad(sample.minute);
  byId(sample.pm ? 'f-pm' : 'f-am').checked = true;
  choose({ label: sample.place, zone: sample.zone });
  example = true;
  for (const id of ['f-month', 'f-day', 'f-year', 'f-hour', 'f-minute', 'f-am', 'f-pm', 'f-pass1', 'f-pass2']) {
    byId(id).addEventListener('input', () => { example = false; refresh(); });
  }
  byId('entry').addEventListener('submit', (e) => {
    e.preventDefault();
    const r = refresh();
    if (!r.error) onRead(r.ms, r.receipt, example, true);
  });
  const first = refresh();
  if (!first.error) onRead(first.ms, first.receipt, true, false);
}
