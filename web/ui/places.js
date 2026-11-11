// Birthplace search: finds towns in the built-in list (web/data/cities.json) and gives their time zone.

const plain = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

/** Build a searcher over the city list. search('rac') -> up to `limit` {label, city, where, zone}. */
export function placeSearch(data) {
  let keys = null; // made on first use
  const prepare = () => {
    keys = data.cities.map((c) => [plain(c[0]), c[1] ? plain(c[1]) : '', plain(`${c[2]} ${data.countries[c[3]]}`)]);
  };
  const entry = (c) => {
    const where = [c[2], data.countries[c[3]]].filter(Boolean).join(', ');
    return { label: `${c[0]}, ${where}`, city: c[0], where, zone: data.zones[c[4]] };
  };
  return function search(query, limit = 8) {
    if (!keys) prepare();
    const [cityPart, ...rest] = plain(query).split(',');
    const city = cityPart.trim();
    const region = rest.join(' ').trim();
    if (city.length < 2) return [];
    const starts = [];
    const inside = [];
    for (let i = 0; i < keys.length && starts.length < limit; i++) {
      const [name, ascii, where] = keys[i];
      if (region && !where.includes(region)) continue;
      if (name.startsWith(city) || ascii.startsWith(city)) starts.push(entry(data.cities[i]));
      else if (inside.length < limit && (name.includes(city) || ascii.includes(city))) inside.push(entry(data.cities[i]));
    }
    return [...starts, ...inside].slice(0, limit);
  };
}

/** Every zone name the browser knows (falls back to the zones in the city list). */
export function zoneNames(data) {
  try {
    return Intl.supportedValuesOf('timeZone');
  } catch {
    return [...data.zones].sort();
  }
}
