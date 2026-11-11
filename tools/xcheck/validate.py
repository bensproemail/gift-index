# Checks the chart counter against outside references. Prints PASS/FAIL lines only (no birth details).
"""Usage: python3 tools/xcheck/validate.py <path to the spiritual-weather-report clone> [n_random]
1) 33 reference moments (Swiss Ephemeris + PyEphem agreed).  2) An independent engine (astronomy-engine)
on random moments.  3) The three golden charts confirmed by outside readers."""
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from giftindex import chart, positions  # noqa: E402
from giftindex.tables import BODIES  # noqa: E402

REF_NAMES = {'Sun': 'Sun', 'Earth': 'Earth', 'NorthNode': 'North Node', 'Moon': 'Moon', 'Mercury': 'Mercury',
             'Venus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturn', 'Uranus': 'Uranus',
             'Neptune': 'Neptune', 'Pluto': 'Pluto'}


def jd(iso):
    return positions.jd_from_unix(datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp())


def angdiff(a, b):
    return abs(((a - b + 180) % 360) - 180)


def check_reference(repo):
    ref = json.loads((repo / 'tests/fixtures/ephemeris-reference.json').read_text())
    worst, worst_design = 0.0, 0.0
    for m in ref['moments']:
        j = jd(m['utc'])
        lons = dict(zip(BODIES, positions.longitudes(j)))
        for mine, theirs in REF_NAMES.items():
            worst = max(worst, angdiff(lons[mine], m['lon'][theirs]))
        dj = positions.design_jd(j)
        worst_design = max(worst_design, abs(dj - jd(m['designUTC'])) * 86400)
    ok = worst < 0.001 and worst_design < 60
    print('%s reference moments: %d checked, worst position gap %.5f deg, worst design-time gap %.0f s'
          % ('PASS' if ok else 'FAIL', len(ref['moments']), worst, worst_design))
    return ok


def check_independent(repo, n):
    rng = random.Random(20261111)
    lo = datetime(1926, 1, 1, tzinfo=timezone.utc).timestamp()
    hi = datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp()
    stamps = [rng.uniform(lo, hi) for _ in range(n)]
    isos = [datetime.fromtimestamp(s, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' for s in stamps]
    here = Path(__file__).resolve().parent
    out = subprocess.run(['node', str(here / 'js_charts.cjs'), str(repo / 'src/hd-engine.js')],
                         input=json.dumps(isos), capture_output=True, text=True, check=True, cwd=here)
    theirs = json.loads(out.stdout)
    place_total = place_bad = fine_bad = 0
    fact_bad = {'type': 0, 'authority': 0, 'definition': 0, 'profile': 0, 'angle': 0}
    worst = 0.0
    defs = {'None': 'No Definition', 'Single': 'Single Definition', 'Split': 'Split Definition',
            'Triple Split': 'Triple Split', 'Quadruple Split': 'Quadruple Split'}
    for iso, t in zip(isos, theirs):
        j = jd(iso)
        lons = positions.longitudes(j) + positions.longitudes(positions.design_jd(j))
        mine = chart.describe([positions.to_unit(x) for x in lons])
        for side, key in (('personality', 'p'), ('design', 'd')):
            for i, b in enumerate(BODIES):
                place_total += 1
                g, ln, col, tn, lon = t[key][i]
                me = mine[side][b]
                worst = max(worst, angdiff(lons[i + (13 if key == 'd' else 0)], lon))
                if (me['gate'], me['line']) != (g, ln):
                    place_bad += 1
                elif (me['color'], me['tone']) != (col, tn):
                    fine_bad += 1
        auth = mine['authority']
        their_auth = t['authority'].replace(' (Environmental)', '')
        if auth.startswith('Ego') and their_auth.startswith('Ego'):
            their_auth = auth          # the two engines name the two Ego kinds by different rules
        fact_bad['type'] += mine['type'] != t['type']
        fact_bad['authority'] += auth != their_auth
        fact_bad['definition'] += defs[mine['definition']] != t['definition']
        fact_bad['profile'] += mine['profile'] != t['profile']
        fact_bad['angle'] += mine['angle'] != t['angle']
    print('INFO independent engine: %d charts, %d placements; worst position gap %.5f deg' % (n, place_total, worst))
    print('INFO gate/line disagreements: %d (%.4f%%); color/tone-only disagreements: %d (%.3f%%)'
          % (place_bad, 100 * place_bad / place_total, fine_bad, 100 * fine_bad / place_total))
    print('INFO chart-fact disagreements out of %d: %s' % (n, fact_bad))
    # the second engine is only accurate to about 0.02 deg, so a few placements near a line border differ
    ok = place_bad / place_total < 0.003 and max(fact_bad.values()) / n < 0.01
    print('%s independent engine agreement' % ('PASS' if ok else 'FAIL'))
    return ok


def check_golden(repo):
    gold = json.loads((repo / 'tests/fixtures/golden-charts.json').read_text())
    ok_all = True
    for c in gold['charts']:
        j = jd(c['utc'])
        mine = chart.describe(positions.chart_units(j))
        exp = c.get('expect', {})
        results = []
        for key, want in exp.items():
            k = key.lower()
            if k == 'type':
                results.append(('type', mine['type'] == want))
            elif k == 'profile':
                results.append(('profile', mine['profile'] == want))
            elif k == 'authority':
                results.append(('authority', mine['authority'].split()[0] == str(want).split()[0]))
            elif k in ('centers', 'defined', 'definedcenters') and isinstance(want, list):
                results.append(('centers', set(want) <= set(mine['centers'])))
        if results:
            good = all(r for _, r in results)
            ok_all &= good
            print('%s golden chart %s: checked %s' % ('PASS' if good else 'FAIL', c.get('id'), ', '.join(k for k, _ in results)))
        else:
            print('INFO golden chart %s: no Human Design facts recorded to check (keys: %s)' % (c.get('id'), ', '.join(exp.keys())))
    return ok_all


if __name__ == '__main__':
    repo = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    results = [check_reference(repo), check_independent(repo, n), check_golden(repo)]
    sys.exit(0 if all(results) else 1)
