# Draws random birth moments and computes their charts (the raw material for every count).
"""Usage:
  python3 -m giftindex.sample living <per_year> <out.npz>      # births 1926..2026, same number each year
  python3 -m giftindex.sample span <n> <out.npz> <jd0> <jd1>   # uniform over any span
  python3 -m giftindex.sample shift <n> <out.npz>              # birth-time error test
Results are seeded, so a rerun gives the same charts."""
import sys
from multiprocessing import Pool

import numpy as np
import swisseph as swe

from .positions import chart_units

SEED = 20261111
FIRST_YEAR, LAST_YEAR = 1926, 2026
SHIFT_MINUTES = [5, 15, 30, 60, 120]


def _chunk(args):
    tag, jd0, jd1, n = args
    rng = np.random.default_rng([SEED, tag])
    jds = rng.uniform(jd0, jd1, n)
    units = np.array([chart_units(j) for j in jds], dtype=np.int32)
    return tag, jds, units


def _run(jobs):
    out = {}
    with Pool(2) as pool:
        for tag, jds, units in pool.imap_unordered(_chunk, jobs):
            out[tag] = (jds, units)
    tags = sorted(out)
    return (np.concatenate([np.full(len(out[t][0]), t, dtype=np.int32) for t in tags]),
            np.concatenate([out[t][0] for t in tags]), np.concatenate([out[t][1] for t in tags]))


def living(per_year, path):
    jobs = [(y, swe.julday(y, 1, 1, 0.0), swe.julday(y + 1, 1, 1, 0.0), per_year) for y in range(FIRST_YEAR, LAST_YEAR + 1)]
    year, jd, units = _run(jobs)
    np.savez_compressed(path, year=year.astype(np.int16), jd=jd, units=units)


def span(n, path, jd0, jd1):
    parts = 40
    edges = np.linspace(jd0, jd1, parts + 1)
    jobs = [(i, edges[i], edges[i + 1], n // parts) for i in range(parts)]
    _, jd, units = _run(jobs)
    np.savez_compressed(path, jd=jd, units=units)


def _shift_chunk(args):
    tag, jd0, jd1, n = args
    rng = np.random.default_rng([SEED, 999, tag])
    jds = rng.uniform(jd0, jd1, n)
    sign = rng.choice([-1.0, 1.0], n)
    layers = [np.array([chart_units(j) for j in jds], dtype=np.int32)]
    for minutes in SHIFT_MINUTES:
        layers.append(np.array([chart_units(j + s * minutes / 1440.0) for j, s in zip(jds, sign)], dtype=np.int32))
    return tag, jds, np.stack(layers)


def shift(n, path):
    jd0, jd1 = swe.julday(1940, 1, 1, 0.0), swe.julday(2026, 1, 1, 0.0)
    jobs = [(i, jd0, jd1, n // 8) for i in range(8)]
    with Pool(2) as pool:
        res = sorted(pool.imap_unordered(_shift_chunk, jobs), key=lambda r: r[0])
    np.savez_compressed(path, jd=np.concatenate([r[1] for r in res]), units=np.concatenate([r[2] for r in res], axis=1),
                        minutes=np.array(SHIFT_MINUTES))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'living':
        living(int(sys.argv[2]), sys.argv[3])
    elif mode == 'span':
        span(int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), float(sys.argv[5]))
    elif mode == 'shift':
        shift(int(sys.argv[2]), sys.argv[3])
    print('done', mode)
