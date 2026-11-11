# Bakes the planet positions into one compact table so the web lookup tool gives the same answers as this engine.
"""Usage: python3 -m giftindex.bake web/data/ephem.bin

Why: the lookup page runs in a browser, where Swiss Ephemeris is not available. Instead of using a second
astronomy library (which disagrees by a few arcseconds), we store THIS engine's positions as short polynomial
pieces (Chebyshev series). The page reads the pieces back, so both sides agree to a few thousandths of an
arcsecond. See docs/decisions/0004.

File layout (all numbers are unsigned "varints", 7 bits per byte, low bits first):
  magic 'GIE1' (4 bytes), then: q_inverse, jd0 * 2, body count, then per body:
  name length, name bytes, segment count, then per segment:
  length in 1/1024 day, coefficient count, coefficients (zigzag-coded integers, unit = 1/q_inverse degree).
Segments of one body follow each other without gaps, starting at jd0. Longitudes are unwrapped inside a
segment; take the result modulo 360."""
import sys

import numpy as np
import swisseph as swe

from .positions import FLAGS

MAGIC = b'GIE1'
Q_INV = 10_000_000                      # coefficient unit = 1e-7 degree (0.00036 arcsecond)
TICKS = 1024                            # segment lengths are stored in 1/1024 day
JD0 = swe.julday(1925, 9, 1, 0.0)       # covers the Design moment of anyone born from 1 Jan 1926
JD1 = swe.julday(2031, 1, 1, 0.0)
MIN_TICKS = 16                          # shortest piece: 1/64 day (22.5 minutes)

# body name -> (Swiss Ephemeris id, base piece length in days, polynomial degree, allowed error in arcseconds)
# The true node is itself only smooth to about 0.05 arcsecond in Swiss Ephemeris, so it gets a looser limit.
# A piece that still misses its limit is cut in half, down to 22.5 minutes (this happens for a few hours when a
# planet passes behind the Sun and the engine bends its light).
BODIES = [
    ('Sun', swe.SUN, 32, 16, 0.003), ('NorthNode', swe.TRUE_NODE, 16, 30, 0.12), ('Moon', swe.MOON, 16, 28, 0.003),
    ('Mercury', swe.MERCURY, 32, 26, 0.003), ('Venus', swe.VENUS, 32, 16, 0.003), ('Mars', swe.MARS, 32, 14, 0.003),
    ('Jupiter', swe.JUPITER, 64, 16, 0.003), ('Saturn', swe.SATURN, 64, 16, 0.003),
    ('Uranus', swe.URANUS, 64, 16, 0.003), ('Neptune', swe.NEPTUNE, 64, 16, 0.003), ('Pluto', swe.PLUTO, 64, 16, 0.003),
]


def _lons(body, jds):
    return np.array([swe.calc_ut(float(j), body, FLAGS)[0][0] for j in jds])


def _fit(body, a, days, deg):
    """Least-squares Chebyshev fit of the unwrapped longitude over [a, a+days]. Returns integer coefficients."""
    m = 3 * (deg + 1)
    k = np.arange(m)
    theta = np.pi * (k + 0.5) / m
    y = np.degrees(np.unwrap(np.radians(_lons(body, a + (np.cos(theta) + 1) * days / 2))))
    j = np.arange(deg + 1)[:, None]
    c = (2.0 / m) * (y[None, :] * np.cos(j * theta[None, :])).sum(axis=1)
    c[0] /= 2
    c[0] %= 360.0
    return np.round(c * Q_INV).astype(np.int64)


def _error(body, a, days, coef, rng):
    """Worst gap (arcseconds) between the fitted piece and the engine at random test moments."""
    u = rng.uniform(-1, 1, 2 * len(coef) + 6)
    fit = np.polynomial.chebyshev.chebval(u, coef / Q_INV)
    real = _lons(body, a + (u + 1) * days / 2)
    return float(np.abs(((fit - real + 180.0) % 360.0) - 180.0).max() * 3600)


def _pieces(body, a, ticks, deg, tol, rng, out):
    days = ticks / TICKS
    coef = _fit(body, a, days, deg)
    err = _error(body, a, days, coef, rng)
    if err > tol and ticks // 2 >= MIN_TICKS:
        _pieces(body, a, ticks // 2, deg, tol, rng, out)
        _pieces(body, a + days / 2, ticks // 2, deg, tol, rng, out)
    else:
        out.append((ticks, coef, err))


def _varint(n, buf):
    n = int(n)
    while True:
        b = n & 0x7F
        n >>= 7
        buf.append(b | (0x80 if n else 0))
        if not n:
            return


def _zigzag(n):
    n = int(n)
    return n * 2 if n >= 0 else -n * 2 - 1


def bake(path):
    buf = bytearray(MAGIC)
    _varint(Q_INV, buf)
    _varint(int(JD0 * 2), buf)
    _varint(len(BODIES), buf)
    stats = {}
    for tag, (name, body, base_days, deg, tol) in enumerate(BODIES):
        rng = np.random.default_rng([20261111, tag])
        pieces = []
        a = JD0
        while a < JD1:
            _pieces(body, a, base_days * TICKS, deg, tol, rng, pieces)
            a += base_days
        _varint(len(name), buf)
        buf.extend(name.encode())
        _varint(len(pieces), buf)
        for ticks, coef, _ in pieces:
            _varint(ticks, buf)
            _varint(len(coef), buf)
            for c in coef:
                _varint(_zigzag(c), buf)
        stats[name] = dict(pieces=len(pieces), worst_arcsec=round(max(p[2] for p in pieces), 5),
                           shortest_days=min(p[0] for p in pieces) / TICKS)
    with open(path, 'wb') as fh:
        fh.write(buf)
    return stats, len(buf)


class Table:
    """Reads a baked file back (the same steps the web page takes). Used by the tests."""

    def __init__(self, path):
        data = open(path, 'rb').read()
        assert data[:4] == MAGIC, 'not a Gift Index ephemeris file'
        self._d, self._i = data, 4
        self.q_inv = self._read()
        self.jd0 = self._read() / 2.0
        self.bodies = {}
        for _ in range(self._read()):
            n = self._read()
            name = data[self._i:self._i + n].decode()
            self._i += n
            starts, lens, coefs = [], [], []
            t = 0
            for _ in range(self._read()):
                ticks = self._read()
                k = self._read()
                raw = [self._read() for _ in range(k)]
                starts.append(t)
                lens.append(ticks)
                coefs.append(np.array([(r >> 1) if r % 2 == 0 else -((r + 1) >> 1) for r in raw], dtype=np.float64) / self.q_inv)
                t += ticks
            self.bodies[name] = (np.array(starts), np.array(lens), coefs)
        self.jd1 = self.jd0 + t / TICKS

    def _read(self):
        n, shift = 0, 0
        while True:
            b = self._d[self._i]
            self._i += 1
            n |= (b & 0x7F) << shift
            shift += 7
            if b < 0x80:
                return n

    def lon(self, name, jd):
        starts, lens, coefs = self.bodies[name]
        t = (jd - self.jd0) * TICKS
        i = int(np.searchsorted(starts, t, side='right')) - 1
        if i < 0 or t > starts[-1] + lens[-1]:
            raise ValueError('moment outside the baked range')
        u = 2.0 * (t - starts[i]) / lens[i] - 1.0
        return float(np.polynomial.chebyshev.chebval(u, coefs[i]) % 360.0)


if __name__ == '__main__':
    stats, size = bake(sys.argv[1])
    for name, s in stats.items():
        print('%-10s %6d pieces, worst gap %.5f arcsec, shortest piece %.4f days' % (name, s['pieces'], s['worst_arcsec'], s['shortest_days']))
    print('wrote %s (%d bytes)' % (sys.argv[1], size))
