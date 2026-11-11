# The full Gift Index report for one birth moment: the reading plus claims, tier, and the birth-time check.
"""This is the one structure the lookup tool shows. The web page builds the same structure in JavaScript
(web/engine/report.js) and a test compares the two field by field, so keep them in step."""
from datetime import datetime, timedelta, timezone

from . import chart, positions
from .claims import CHANNEL_CLAIM_LABEL, CHANNEL_CLAIMS, FAMILY_CLAIMS, GK_SPHERES
from .reading import GK_GIFT, reading
from .tables import FAMILIES

SHIFT_MINUTES = [5, 15, 30, 60]
TIERS = [(1e-2, 'Common'), (1e-3, 'Uncommon'), (1e-4, 'Rare'), (0.0, 'Very rare')]


def tier(share):
    """Headline tier from the share of living people (the Field Guide's four bands)."""
    if share <= 0:
        return 'Not seen'
    return next(name for floor, name in TIERS if share >= floor)


def _facts(units):
    """The chart facts the birth-time check watches."""
    c = chart.describe(units)
    sun = c['personality']['Sun']
    gates = sorted({p['gate'] for side in ('personality', 'design') for p in c[side].values()})
    return dict(type=c['type'], authority=c['authority'], definition=c['definition'], profile=c['profile'],
                channels=c['channels'], gates=gates, sun_color=[sun['gate'], sun['line'], sun['color']],
                sun_tone=[sun['gate'], sun['line'], sun['color'], sun['tone']], arrows=c['arrows'])


def sensitivity(jd, units_at=positions.chart_units):
    """For each watched fact: the smallest birth-time error (minutes, either direction) that changes it, or None."""
    base = _facts(units_at(jd))
    out = {k: None for k in base}
    for minutes in SHIFT_MINUTES:
        for sign in (-1, 1):
            other = _facts(units_at(jd + sign * minutes / 1440.0))
            for k in base:
                if out[k] is None and other[k] != base[k]:
                    out[k] = minutes
    return out


def _iso(jd):
    """Julian day -> 'YYYY-MM-DDTHH:MMZ' (rounded down to the minute)."""
    dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=round((jd - 2440587.5) * 86400.0, 3))
    return dt.strftime('%Y-%m-%dT%H:%MZ')


def report(unix_ms, ref, units_at=positions.chart_units, design_jd=positions.design_jd):
    """Everything the lookup tool shows for one moment (milliseconds since 1970, UTC)."""
    jd = unix_ms / 86400000.0 + 2440587.5
    year = (datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=unix_ms)).year
    r = reading(jd, year, ref, units=units_at(jd))
    dj = design_jd(jd)
    lead_share = r['families'][0]['top_share']
    families = []
    for f in r['families']:
        claim, downside, label = FAMILY_CLAIMS[f['family']]
        families.append(dict(f, lead=bool(f['score'] > 0 and f['top_share'] == lead_share), claim=claim,
                             downside=downside, label=label, circuit=dict(FAMILIES)[f['family']]))
    channels = []
    for c in r['channels']:
        claim, off, page = CHANNEL_CLAIMS[c['channel']]
        channels.append(dict(c, claim=claim, off_course=off, page=page, label=CHANNEL_CLAIM_LABEL))
    me = r['chart']
    keys = [dict(sphere=sphere, source='%s %s' % (side.capitalize(), body), gate=me[side][body]['gate'],
                 gift=GK_GIFT[me[side][body]['gate']]) for sphere, side, body in GK_SPHERES]
    return dict(
        moment=dict(utc=_iso(jd), design_utc=_iso(dj), design_ms=int(round((dj - 2440587.5) * 86400000.0)), birth_year=year),
        chart=me, n_gates=r['n_gates'], n_channels=r['n_channels'],
        headline=dict(label=r['headline'], living_share=r['headline_living'], living_one_in=r['headline_living_one_in'],
                      tier=tier(r['headline_living']), cohort_share=r['headline_cohort'],
                      cohort_one_in=r['headline_cohort_one_in'], cohort_hits=r['headline_cohort_hits'],
                      cohort_charts=r['headline_cohort_charts'], cohort_years=r['cohort_years']),
        channels=channels, families=families, gene_keys=keys, sensitivity=sensitivity(jd, units_at))
