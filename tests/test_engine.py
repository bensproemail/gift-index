# Tests for the chart counter: fixed tables, chart logic on hand-built charts, and the astronomy.
import json
from pathlib import Path

import numpy as np
import pytest
import swisseph as swe

from giftindex import chart, positions
from giftindex.tables import (CENTERS, CHANNEL_KEYS, CHANNELS, CIRCUITS, FAMILY_OF_CHANNEL, UNITS_PER_GATE, WHEEL)


def units_for(gates):
    """A hand-built chart whose 26 placements cycle through the given gates (line 1)."""
    return [WHEEL.index(gates[i % len(gates)]) * UNITS_PER_GATE for i in range(26)]


def facts(gates):
    return chart.describe(units_for(gates))


def test_tables_are_complete():
    assert sorted(WHEEL) == list(range(1, 65))
    assert sorted(g for gs in CENTERS.values() for g in gs) == list(range(1, 65))
    assert len(CHANNELS) == 36 and len(set(CHANNELS)) == 36
    assert sorted(k for ks in CIRCUITS.values() for k in ks) == sorted(CHANNEL_KEYS)
    assert set(FAMILY_OF_CHANNEL) == set(CHANNEL_KEYS)


def test_exactly_three_channels_join_opposite_gates():
    opposite = {WHEEL[i]: WHEEL[(i + 32) % 64] for i in range(64)}
    assert sorted(k for k, (a, b) in zip(CHANNEL_KEYS, CHANNELS) if opposite[a] == b) == ['20-34', '23-43', '37-40']


@pytest.mark.parametrize('gates,ctype,authority,definition', [
    ([1], 'Reflector', 'Lunar', 'None'),
    ([20, 34], 'Manifesting Generator', 'Sacral', 'Single'),
    ([59, 6], 'Generator', 'Emotional', 'Single'),
    ([5, 15], 'Generator', 'Sacral', 'Single'),
    ([21, 45], 'Manifestor', 'Ego Manifested', 'Single'),
    ([25, 51], 'Projector', 'Ego Projected', 'Single'),
    ([25, 51, 1, 8], 'Manifestor', 'Ego Manifested', 'Single'),
    ([1, 8], 'Projector', 'Self-Projected', 'Single'),
    ([64, 47], 'Projector', 'Mental', 'Single'),
    ([16, 48], 'Projector', 'Splenic', 'Single'),
    ([35, 36], 'Manifestor', 'Emotional', 'Single'),
    ([64, 47, 59, 6], 'Generator', 'Emotional', 'Split'),
    ([64, 47, 59, 6, 21, 45], 'Manifesting Generator', 'Emotional', 'Triple Split'),
    ([64, 47, 59, 6, 21, 45, 18, 58], 'Manifesting Generator', 'Emotional', 'Quadruple Split'),
])
def test_type_authority_definition(gates, ctype, authority, definition):
    f = facts(gates)
    assert (f['type'], f['authority'], f['definition']) == (ctype, authority, definition)


def test_split_width():
    no_bridge = chart.derive([units_for([64, 47, 59, 6, 11])])     # two islands with no channel running between them
    wide = chart.derive([units_for([64, 47, 53, 42])])
    one_gate_short = chart.derive([units_for([1, 8, 59, 6, 5])])   # gate 5 (Sacral) reaches toward gate 15 (G)
    single = chart.derive([units_for([20, 34])])
    assert chart.split_width(no_bridge)[0] == 2
    assert chart.split_width(wide)[0] == 2
    assert chart.split_width(one_gate_short)[0] == 1
    assert chart.split_width(single)[0] == 0


def test_sun_position_and_design_moment():
    jd = 2451545.0                                                # 1 Jan 2000, 12:00 TT ~ UT
    sun = positions.longitudes(jd)[0]
    assert abs(sun - 280.37) < 0.02
    dj = positions.design_jd(jd)
    assert 86 < jd - dj < 91
    dsun = swe.calc_ut(dj, swe.SUN, positions.FLAGS)[0][0]
    assert abs(((sun - dsun) % 360) - 88) < 1e-6


def test_sun_and_earth_sit_opposite_and_profiles_are_valid():
    rng = np.random.default_rng(1)
    units = np.array([positions.chart_units(j) for j in rng.uniform(2430000, 2461000, 300)])
    d = chart.derive(units)
    opposite = {WHEEL[i]: WHEEL[(i + 32) % 64] for i in range(64)}
    assert all(opposite[int(a)] == int(b) for a, b in zip(d['gate'][:, 0], d['gate'][:, 1]))
    assert all(opposite[int(a)] == int(b) for a, b in zip(d['gate'][:, 2], d['gate'][:, 3]))
    valid = {'1/3', '1/4', '2/4', '2/5', '3/5', '3/6', '4/6', '4/1', '5/1', '5/2', '6/2', '6/3'}
    assert {'%d/%d' % (p, q) for p, q in zip(d['p_line'], d['d_line'])} <= valid
    # Design Sun base is always exactly one base behind the Personality Sun base (88 deg = 16896 bases)
    assert np.all((d['base'][:, 13] - d['base'][:, 0]) % 5 == 4)


def test_count_matches_published_figures():
    path = Path(__file__).resolve().parents[1] / 'data' / 'results.json'
    if not path.exists():
        pytest.skip('count has not been run')
    r = json.loads(path.read_text())
    assert abs(r['angle']['Juxtaposition'] - 2.22) < 0.1                 # theory: 2.22%
    assert all(abs(r['profile'][p] - 14.44) < 0.2 for p in ['1/3', '2/4', '3/5', '4/6', '5/1', '6/2'])
    a = r['alltime_1781_2030']                                           # Rave Statistics 1781-2027 (IHDS, 2009)
    assert abs(a['type']['Generator'] - 32.8) < 0.5 and abs(a['type']['Reflector'] - 1.2) < 0.15
    assert abs(a['definition']['Split'] - 46.9) < 0.5 and abs(a['five_channels'] - 13.3) < 0.4
    assert abs(a['manifestor_with_3_channels'] - 3.7) < 0.3 and abs(a['arrows_PLL_DLL'] - 7.5) < 0.3
