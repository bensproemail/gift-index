# Exports what the web lookup page needs: the tables, the claims and the counted numbers, plus test fixtures.
"""Usage: python3 -m giftindex.webref web/data/ref.json web/tests/fixtures.json

ref.json is built only from giftindex/tables.py, giftindex/claims.py and data/results.json (+ the per-year
count), so the page can never show a number that is not in the published count.
fixtures.json holds this engine's answers for seeded random moments; the JavaScript tests must reproduce them."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import clock, positions, tables
from .claims import ARROW_NAMES, CHANNEL_CLAIM_LABEL, CHANNEL_CLAIMS, FAMILY_CLAIMS, GK_SPHERES
from .count import PROFILE_INDEX
from .reading import GK_GIFT, load_reference
from .report import SHIFT_MINUTES, TIERS, report

SEED = 20261111
SAMPLE_READER = (1980, 3, 4, 7, 42, 'America/Chicago')      # the made-up Sample Reader (CLAUDE.md)
N_UNITS, N_REPORTS = 1500, 120

# Clock cases for the time-zone test: ordinary, daylight, half-hour and 45-minute zones, a jump forward,
# a fall back, and old dates. None is anyone's birth moment.
CLOCK_CASES = [
    SAMPLE_READER, (1980, 7, 4, 12, 0, 'America/Chicago'), (1999, 12, 31, 23, 59, 'America/Los_Angeles'),
    (2015, 3, 8, 2, 30, 'America/New_York'), (2015, 11, 1, 1, 30, 'America/New_York'),
    (1944, 6, 6, 9, 0, 'America/Chicago'), (1955, 8, 15, 14, 20, 'America/Denver'),
    (1961, 1, 20, 12, 0, 'America/New_York'), (1972, 5, 9, 6, 5, 'Europe/London'), (1968, 12, 1, 8, 0, 'Europe/London'),
    (1988, 2, 29, 18, 45, 'Asia/Kolkata'), (1990, 10, 10, 10, 10, 'Asia/Kathmandu'), (2001, 1, 1, 0, 0, 'Australia/Sydney'),
    (1975, 9, 30, 22, 15, 'America/Sao_Paulo'), (2020, 2, 2, 20, 20, 'Asia/Tokyo'), (1933, 3, 3, 3, 33, 'Europe/Berlin'),
    (2010, 6, 15, 12, 0, 'Africa/Johannesburg'), (1996, 4, 7, 2, 30, 'America/Chicago'), (2026, 11, 1, 1, 15, 'America/Chicago'),
    (1950, 5, 5, 5, 55, 'America/Costa_Rica'), (1983, 7, 7, 7, 7, 'Pacific/Honolulu'), (1947, 8, 15, 0, 0, 'Asia/Kolkata'),
]


def build_ref(data_dir='data'):
    r = load_reference(data_dir)
    jby = r['_joint_by_year']
    labels = {}
    for t, tn in enumerate(tables.TYPES):
        for a, an in enumerate(tables.AUTHORITIES):
            for d, dn in enumerate(tables.DEFINITIONS):
                for p, pn in enumerate(tables.PROFILES):
                    labels['%s · %s · %s · %s' % (tn, an, dn, pn)] = ((t * 8 + a) * 5 + d) * 12 + p
    joint = {str(labels[k]): v for k, v in r['_joint'].items()}
    by_year = []
    for row in jby:
        nz = np.nonzero(row)[0]
        by_year.append([int(x) for pair in zip(nz, row[nz]) for x in pair])
    src = hashlib.sha256(Path(data_dir, 'results.json').read_bytes()).hexdigest()[:16]
    return {
        'source': {'results_sha': src, 'n_charts': r['n_charts'], 'years': r['years']},
        'tables': {
            'wheel': tables.WHEEL, 'start_deg': tables.START_DEG, 'center_names': tables.CENTER_NAMES,
            'centers': tables.CENTERS, 'channels': [list(c) for c in tables.CHANNELS],
            'channel_names': tables.CHANNEL_NAMES, 'families': [list(f) for f in tables.FAMILIES],
            'circuits': tables.CIRCUITS, 'bodies': tables.BODIES, 'types': tables.TYPES,
            'authorities': tables.AUTHORITIES, 'definitions': tables.DEFINITIONS, 'profiles': tables.PROFILES,
            'profile_index': PROFILE_INDEX, 'angles': tables.ANGLES,
        },
        'claims': {
            'family': {k: list(v) for k, v in FAMILY_CLAIMS.items()},
            'channel': {k: list(v) for k, v in CHANNEL_CLAIMS.items()}, 'channel_label': CHANNEL_CLAIM_LABEL,
            'gk_gift': {str(k): v for k, v in GK_GIFT.items()}, 'gk_spheres': [list(s) for s in GK_SPHERES],
            'arrow_names': ARROW_NAMES,
        },
        'count': {
            'year_axis': r['year_axis'], 'joint': joint, 'joint_by_year': by_year,
            'channels': {k: {'share': v['share'], 'by_year': r['channel_by_year'][k]} for k, v in r['channels'].items()},
            'families': {k: {'max_score': v['max_score'], 'score_top_share': v['score_top_share']} for k, v in r['families'].items()},
            'shares': {k: r[k] for k in ('type', 'authority', 'definition', 'profile', 'angle')},
            'typical_one_in': r['headline_one_in_x_percentiles']['50'],
            'birth_time_error': r['birth_time_error']['by_minutes'],
        },
        'rules': {'tiers': [[floor, name] for floor, name in TIERS], 'shift_minutes': SHIFT_MINUTES},
    }


def build_fixtures(ref):
    rng = np.random.default_rng(SEED)
    lo = datetime(1926, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
    hi = datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
    stamps = [int(x) for x in rng.uniform(lo, hi, N_UNITS)]
    late_lo, late_hi = hi, datetime(2030, 12, 1, tzinfo=timezone.utc).timestamp() * 1000
    late = [int(x) for x in rng.uniform(late_lo, late_hi, 6)]
    sample = clock.local_to_utc(*SAMPLE_READER)['ms']
    edges = [int(lo) + 60000, int(hi) - 60000]
    units = [[ms] + positions.chart_units(ms / 86400000.0 + 2440587.5) for ms in stamps]
    reports = [dict(ms=ms, report=report(ms, ref)) for ms in [sample] + edges + late + stamps[:N_REPORTS]]
    clocks = [dict(input=list(c), expect={k: v for k, v in clock.local_to_utc(*c).items() if k != 'rule'}) for c in CLOCK_CASES]
    from .lookup import render
    text = render(reports[0]['report'], 'RECEIPT')[1:]          # the copy-as-text lines, minus the receipt
    return dict(sample_reader_ms=sample, sample_text=text, units=units, reports=reports, clocks=clocks)


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, separators=(',', ':'), ensure_ascii=False) + '\n')


if __name__ == '__main__':
    ref = build_ref()
    write_json(sys.argv[1], ref)
    print('wrote', sys.argv[1])
    if len(sys.argv) > 2:
        write_json(sys.argv[2], build_fixtures(load_reference()))
        print('wrote', sys.argv[2])
