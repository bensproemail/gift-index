# Planet positions for a birth moment: 13 Personality + 13 Design placements as wheel units.
"""Uses Swiss Ephemeris (Moshier mode, no data files). Tropical zodiac, apparent positions,
TRUE lunar node. Design = the moment the Sun stood exactly 88 degrees earlier."""
import swisseph as swe

from .tables import START_DEG, TOTAL_UNITS, UNITS_PER_DEG

FLAGS = swe.FLG_MOSEPH
_ORDER = [swe.SUN, None, swe.TRUE_NODE, None, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
          swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]


def longitudes(jd):
    """13 ecliptic longitudes (degrees) in BODIES order for a Julian day (UT)."""
    out = []
    for body in _ORDER:
        if body is None:
            out.append((out[-1] + 180.0) % 360.0)   # Earth opposite Sun, South Node opposite North
        else:
            out.append(swe.calc_ut(jd, body, FLAGS)[0][0])
    return out


def design_jd(jd):
    """Julian day when the Sun was exactly 88 degrees of longitude before its birth position."""
    sun = swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]
    target = (sun - 88.0) % 360.0
    t = jd - 88.0 / 0.98565
    for _ in range(30):
        pos = swe.calc_ut(t, swe.SUN, FLAGS | swe.FLG_SPEED)[0]
        diff = ((pos[0] - target + 180.0) % 360.0) - 180.0
        if abs(diff) < 1e-8:
            break
        t -= diff / pos[3]
    return t


def to_unit(lon):
    """Longitude -> wheel unit 0..69119 (gate, line, color, tone, base packed together)."""
    u = int(((lon - START_DEG) % 360.0) * UNITS_PER_DEG)
    return u if u < TOTAL_UNITS else TOTAL_UNITS - 1


def chart_units(jd):
    """26 wheel units: Personality (13) then Design (13)."""
    return [to_unit(x) for x in longitudes(jd)] + [to_unit(x) for x in longitudes(design_jd(jd))]


def jd_from_unix(seconds):
    """Unix seconds (UTC) -> Julian day."""
    return seconds / 86400.0 + 2440587.5
