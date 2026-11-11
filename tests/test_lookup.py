# Tests for the lookup tool: the clock, the full report, the baked planet table and the web reference files.
import json
from pathlib import Path

import numpy as np
import pytest
import swisseph as swe

from giftindex import bake, clock, lookup, positions, webref
from giftindex.reading import load_reference
from giftindex.report import report, tier

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = webref.SAMPLE_READER          # the made-up Sample Reader: 4 Mar 1980, 7:42 am, Racine (Central time)


@pytest.fixture(scope='module')
def ref():
    return load_reference(ROOT / 'data')


def test_clock_ordinary_gap_and_twice():
    t = clock.local_to_utc(*SAMPLE)
    assert (t['status'], t['offset_minutes']) == ('ok', -360) and 'daylight time off' in t['rule']
    assert clock.local_to_utc(1980, 7, 4, 12, 0, 'America/Chicago')['offset_minutes'] == -300
    assert clock.local_to_utc(2015, 3, 8, 2, 30, 'America/New_York')['status'] == 'gap'
    twice = clock.local_to_utc(2015, 11, 1, 1, 30, 'America/New_York')
    assert twice['status'] == 'twice' and twice['ms_second'] - twice['ms'] == 3600000
    assert clock.local_to_utc(1990, 10, 10, 10, 10, 'Asia/Kathmandu')['offset_minutes'] == 345


def test_report_matches_the_field_guide_worked_example(ref):
    r = report(clock.local_to_utc(*SAMPLE)['ms'], ref)
    h = r['headline']
    assert h['label'] == 'Generator · Emotional · Single · 3/6'
    assert (h['living_one_in'], h['tier'], h['cohort_one_in'], h['cohort_years']) == (1206, 'Rare', 943, [1978, 1982])
    assert r['chart']['personality']['Sun'] == dict(gate=63, line=3, color=6, tone=5, base=2)
    assert [(c['channel'], c['made'], c['living'], c['cohort']) for c in r['channels']] == [('6-59', 'mixed', 9.33, 25.79)]
    lead = r['families'][0]
    assert (lead['family'], lead['score'], lead['max'], lead['lead']) == ('Caretaker', 2, 4, True)
    assert [f['family'] for f in r['families'] if f['score'] == 0] == ['Spiritual', 'Presence']
    assert not any(f['lead'] for f in r['families'][1:])
    assert ['%d %s' % (k['gate'], k['gift']) for k in r['gene_keys']] == ['63 Inquiry', '64 Imagination', '5 Patience', '35 Adventure']
    assert r['sensitivity']['type'] is None and r['sensitivity']['sun_tone'] == 15


def test_every_gift_line_carries_a_label_and_a_downside(ref):
    r = report(clock.local_to_utc(*SAMPLE)['ms'], ref)
    assert all(f['label'] and f['downside'] and f['claim'] for f in r['families'])
    assert all(c['label'] == 'BOOK' and c['off_course'] and c['page'] for c in r['channels'])
    text = '\n'.join(lookup.render(r, 'RECEIPT'))
    assert 'not proven' in text and 'COUNT' in text and 'GK' in text


def test_tiers_and_births_outside_the_counted_years(ref):
    assert [tier(x) for x in (0.02, 0.01, 0.005, 0.0005, 0.00005, 0.0)] == ['Common', 'Common', 'Uncommon', 'Rare', 'Very rare', 'Not seen']
    late = report(int((swe.julday(2028, 6, 1, 12.0) - 2440587.5) * 86400000), ref)
    assert late['headline']['cohort_share'] is None and late['headline']['cohort_years'] is None
    assert all(c['cohort'] is None for c in late['channels'])
    assert late['headline']['tier'] in ('Common', 'Uncommon', 'Rare', 'Very rare', 'Not seen')


def test_baked_table_matches_the_engine():
    """The web page reads web/data/ephem.bin. It must give this engine's positions (limits from bake.BODIES)."""
    table = bake.Table(ROOT / 'web' / 'data' / 'ephem.bin')
    rng = np.random.default_rng(3)
    lo, hi = swe.julday(1926, 1, 1, 0.0) - 95, swe.julday(2030, 12, 31, 0.0)
    assert table.jd0 <= lo and table.jd1 >= hi
    worst = {}
    for jd in rng.uniform(lo, hi, 400):
        for name, body, _, _, _ in bake.BODIES:
            gap = abs(((table.lon(name, jd) - swe.calc_ut(jd, body, positions.FLAGS)[0][0] + 180) % 360) - 180) * 3600
            worst[name] = max(worst.get(name, 0.0), gap)
    for name, _, _, _, tol in bake.BODIES:
        assert worst[name] < max(2 * tol, 0.01), (name, worst[name])


def test_web_reference_file_is_built_from_the_current_count():
    """web/data/ref.json must be exactly what giftindex.webref makes from data/results.json today."""
    saved = json.loads((ROOT / 'web' / 'data' / 'ref.json').read_text())
    fresh = json.loads(json.dumps(webref.build_ref(ROOT / 'data')))
    assert saved == fresh, 'run: python3 -m giftindex.webref web/data/ref.json web/tests/fixtures.json'


def test_web_fixtures_are_current(ref):
    """The JavaScript tests compare against web/tests/fixtures.json, so it must hold this engine's answers."""
    fx = json.loads((ROOT / 'web' / 'tests' / 'fixtures.json').read_text())
    for row in fx['units'][::150]:
        assert positions.chart_units(row[0] / 86400000.0 + 2440587.5) == row[1:]
    first = fx['reports'][0]
    assert first['ms'] == fx['sample_reader_ms'] == clock.local_to_utc(*SAMPLE)['ms']
    assert json.loads(json.dumps(report(first['ms'], ref))) == first['report']
    assert fx['sample_text'] == lookup.render(report(first['ms'], ref), 'RECEIPT')[1:]
