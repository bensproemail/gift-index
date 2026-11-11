# One person's Gift Index reading: chart facts, rarity (all living people + born within 2 years), gift scores.
"""Needs the count output (data/results.json and data/results_joint_by_year.npy)."""
import json
import math
from pathlib import Path

import numpy as np

from . import chart, positions
from .count import PROFILE_INDEX
from .tables import (AUTHORITIES, CHANNEL_KEYS, CHANNEL_NAMES, CHANNELS, DEFINITIONS, FAMILIES, FAMILY_NAMES,
                     FAMILY_OF_CHANNEL, TYPES)

# Gene Keys "Gift" word for each of the 64 keys (Richard Rudd's Spectrum of Consciousness). A separate system.
GK_GIFT = dict(enumerate([
    'Freshness', 'Orientation', 'Innovation', 'Understanding', 'Patience', 'Diplomacy', 'Guidance', 'Style',
    'Determination', 'Naturalness', 'Idealism', 'Discrimination', 'Discernment', 'Competence', 'Magnetism',
    'Versatility', 'Far-Sightedness', 'Integrity', 'Sensitivity', 'Self-Assurance', 'Authority', 'Graciousness',
    'Simplicity', 'Invention', 'Acceptance', 'Artfulness', 'Altruism', 'Totality', 'Commitment', 'Lightness',
    'Leadership', 'Preservation', 'Mindfulness', 'Strength', 'Adventure', 'Humanity', 'Equality', 'Perseverance',
    'Dynamism', 'Resolve', 'Anticipation', 'Detachment', 'Insight', 'Teamwork', 'Synergy', 'Delight',
    'Transmutation', 'Resourcefulness', 'Revolution', 'Equilibrium', 'Initiative', 'Restraint', 'Expansion',
    'Aspiration', 'Freedom', 'Enrichment', 'Intuition', 'Vitality', 'Intimacy', 'Realism', 'Inspiration',
    'Precision', 'Inquiry', 'Imagination'], start=1))


def load_reference(data_dir='data'):
    d = Path(data_dir)
    ref = json.loads((d / 'results.json').read_text())
    ref['_joint_by_year'] = np.load(d / 'results_joint_by_year.npy')
    return ref


def one_in(share):
    # half always rounds up (plain round() would send 312.5 to 312; the web page's Math.round gives 313)
    return None if share <= 0 else int(math.floor(1 / share + 0.5))


def reading(jd, birth_year, ref, units=None):
    units = positions.chart_units(jd) if units is None else units
    me = chart.describe(units)
    d = chart.derive([units])
    code = ((TYPES.index(me['type']) * 8 + AUTHORITIES.index(me['authority'])) * 5
            + DEFINITIONS.index(me['definition'])) * 12 + PROFILE_INDEX[me['profile']]
    label = '%s · %s · %s · %s' % (me['type'], me['authority'], me['definition'], me['profile'])
    living = ref['_joint'].get(label, 0.0)
    years = ref['year_axis']
    yi = years.index(birth_year) if birth_year in years else None      # births outside the counted years: no cohort
    cohort = cohort_hits = cohort_charts = cohort_years = None
    if yi is not None:
        window = ref['_joint_by_year'][max(0, yi - 2):yi + 3]
        cohort_hits, cohort_charts = int(window[:, code].sum()), int(window.sum())
        cohort = float(cohort_hits / cohort_charts)
        cohort_years = [years[max(0, yi - 2)], years[min(len(years) - 1, yi + 2)]]

    channels = []
    for k, key in enumerate(CHANNEL_KEYS):
        if d['chan'][0, k]:
            channels.append(dict(channel=key, name=CHANNEL_NAMES[key], family=FAMILY_OF_CHANNEL[key],
                                 living=ref['channels'][key]['share'],
                                 cohort=None if yi is None else ref['channel_by_year'][key][yi],
                                 made=['', 'conscious', 'unconscious', 'mixed'][int(d['chan_kind'][0, k])]))

    act = d['act'][0]
    fam = []
    for fname, _circ in FAMILIES:
        score = 0
        for k, key in enumerate(CHANNEL_KEYS):
            if FAMILY_OF_CHANNEL[key] == fname:
                a, b = CHANNELS[k]
                score += 2 if (act[a] and act[b]) else (1 if (act[a] or act[b]) else 0)
        top = ref['families'][fname]['score_top_share'].get(str(score))
        fam.append(dict(family=fname, score=score, max=ref['families'][fname]['max_score'], top_share=top))
    fam.sort(key=lambda f: f['top_share'])

    primes = {'Personality Sun': me['personality']['Sun'], 'Personality Earth': me['personality']['Earth'],
              'Design Sun': me['design']['Sun'], 'Design Earth': me['design']['Earth']}
    return dict(chart=me, headline=label, headline_living=living, headline_living_one_in=one_in(living),
                headline_cohort=cohort, headline_cohort_one_in=None if cohort is None else one_in(cohort),
                headline_cohort_hits=cohort_hits, headline_cohort_charts=cohort_charts, cohort_years=cohort_years,
                channels=channels, families=fam,
                n_gates=int(d['n_gates'][0]), n_channels=int(d['n_channels'][0]),
                gene_keys={k: '%d %s' % (v['gate'], GK_GIFT[v['gate']]) for k, v in primes.items()})


assert set(FAMILY_NAMES) == {f for f, _ in FAMILIES}
