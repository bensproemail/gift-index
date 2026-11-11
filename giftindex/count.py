# Counts everything in the sample of charts and writes the result tables (results.json).
"""Usage: python3 -m giftindex.count data/living.npz data/alltime.npz data/shift.npz data/results.json
'Living people' = births 1926..2026 weighted by an approximate 2025 world age mix."""
import json
import sys

import numpy as np

from . import chart
from .tables import (ANGLES, AUTHORITIES, CENTER_NAMES, CHANNEL_KEYS, CIRCUITS, DEFINITIONS, FAMILIES,
                     FAMILY_NAMES, FAMILY_OF_CHANNEL, PROFILES, TYPES, WHEEL)

# Approximate world population by 5-year age group, 2025, in millions (UN World Population Prospects style
# figures recalled by Claude, not downloaded). Ages 0-4, 5-9, ... 95-99, 100+.
AGE_GROUP_MILLIONS = [646, 677, 687, 663, 623, 600, 607, 590, 529, 487, 465, 425, 361, 296, 228, 152, 93, 51, 21, 6, 0.7]
NOW_YEAR = 2026
PROFILE_INDEX = {p: i for i, p in enumerate(PROFILES)}
_PROFILE_LUT = np.full((7, 7), -1, dtype=np.int8)
for _p, _i in PROFILE_INDEX.items():
    _PROFILE_LUT[int(_p[0]), int(_p[2])] = _i


def year_weight(years):
    age = np.clip(NOW_YEAR - years, 0, 100)
    group = np.minimum(age // 5, 20)
    return np.array(AGE_GROUP_MILLIONS)[group] / 5.0


def compact(units, step=200_000):
    """Derive charts in chunks and keep only small per-chart arrays."""
    keep = {}
    for i in range(0, len(units), step):
        d = chart.derive(units[i:i + step])
        d['split_width'] = chart.split_width(d)
        d['hang_defined'], d['hang_open'] = chart.hanging_gates(d)
        d['profile'] = _PROFILE_LUT[d['p_line'], d['d_line']]
        u = units[i:i + step]
        part = dict(type=d['type'], authority=d['authority'], definition=d['definition'], profile=d['profile'],
                    angle=d['angle'], arrows=d['arrows'], n_channels=d['n_channels'], n_centers=d['n_centers'],
                    n_gates=d['n_gates'], chan_kind=d['chan_kind'], defined=d['defined'], act=d['act'][:, 1:],
                    split_width=d['split_width'], hang_defined=d['hang_defined'].astype(np.int8),
                    hang_open=d['hang_open'].astype(np.int8), p_sun=u[:, 0], d_sun=u[:, 13],
                    p_node_tone=d['tone'][:, 2].astype(np.int8), d_node_tone=d['tone'][:, 15].astype(np.int8),
                    p_sun_gate=d['gate'][:, 0].astype(np.int8),
                    gate_center_open=_open_center_gates(d))
        for k, v in part.items():
            keep.setdefault(k, []).append(v)
    return {k: np.concatenate(v) for k, v in keep.items()}


def _open_center_gates(d):
    """(N,9) number of active gates sitting in each center (to tell 'open with gates' from 'fully open')."""
    from .tables import CENTERS
    out = np.zeros((d['act'].shape[0], 9), dtype=np.int8)
    for ci, c in enumerate(CENTER_NAMES):
        out[:, ci] = d['act'][:, CENTERS[c]].sum(axis=1)
    return out


def share(codes, w, n):
    return (np.bincount(codes, weights=w, minlength=n) / w.sum()).tolist()


def pct(x, digits=2):
    return round(100 * float(x), digits)


def family_scores(c):
    """(N,7) raw gift-family score: 2 per defined channel, 1 per half channel (one of its two gates active)."""
    from .tables import CHANNELS
    n = len(c['type'])
    act = c['act']
    scores = np.zeros((n, 7), dtype=np.int8)
    chans = np.zeros((n, 7), dtype=np.int8)
    for k, key in enumerate(CHANNEL_KEYS):
        f = FAMILY_NAMES.index(FAMILY_OF_CHANNEL[key])
        a, b = CHANNELS[k]
        both = c['chan_kind'][:, k] > 0
        one = act[:, a - 1] ^ act[:, b - 1]
        scores[:, f] += (2 * both + one).astype(np.int8)
        chans[:, f] += both
    return scores, chans


def living_tables(z):
    years, units = z['year'].astype(np.int32), z['units']
    c = compact(units)
    w = year_weight(years)
    W = w.sum()
    R = {'n_charts': int(len(years)), 'years': [int(years.min()), int(years.max())],
         'effective_n': int(W ** 2 / (w ** 2).sum())}

    # ---- layer 1
    R['type'] = dict(zip(TYPES, map(pct, share(c['type'], w, 5))))
    R['authority'] = dict(zip(AUTHORITIES, map(pct, share(c['authority'], w, 8))))
    R['definition'] = dict(zip(DEFINITIONS, map(pct, share(c['definition'], w, 5))))
    R['profile'] = dict(zip(PROFILES, map(pct, share(c['profile'], w, 12))))
    R['angle'] = dict(zip(ANGLES, map(pct, share(c['angle'], w, 3))))
    R['type_unweighted'] = dict(zip(TYPES, map(pct, share(c['type'], np.ones(len(w)), 5))))
    m = (years >= 1945) & (years <= 2015)
    ones = np.ones(int(m.sum()))
    R['compare_1945_2015'] = {
        'type': dict(zip(TYPES, map(pct, share(c['type'][m], ones, 5)))),
        'authority': dict(zip(AUTHORITIES, map(pct, share(c['authority'][m], ones, 8)))),
        'angle': dict(zip(ANGLES, map(pct, share(c['angle'][m], ones, 3))))}
    ta = np.bincount(c['type'] * 8 + c['authority'], weights=w, minlength=40).reshape(5, 8) / W
    R['type_by_authority'] = {TYPES[t]: {AUTHORITIES[a]: pct(ta[t, a], 3) for a in range(8) if ta[t, a] > 0} for t in range(5)}
    td = np.bincount(c['type'] * 5 + c['definition'], weights=w, minlength=25).reshape(5, 5) / W
    R['type_by_definition'] = {TYPES[t]: {DEFINITIONS[a]: pct(td[t, a], 3) for a in range(5) if td[t, a] > 0} for t in range(5)}

    joint = ((c['type'].astype(np.int64) * 8 + c['authority']) * 5 + c['definition']) * 12 + c['profile']
    jf = np.bincount(joint, weights=w, minlength=5 * 8 * 5 * 12) / W
    present = np.nonzero(jf)[0]
    order = present[np.argsort(-jf[present])]

    def label(code):
        p = code % 12; d = (code // 12) % 5; a = (code // 60) % 8; t = code // 480
        return '%s · %s · %s · %s' % (TYPES[t], AUTHORITIES[a], DEFINITIONS[d], PROFILES[p])
    R['headline_combos'] = {'count_seen': int(len(present)),
                            'most_common': [[label(k), pct(jf[k], 3), round(1 / jf[k])] for k in order[:12]],
                            'examples_rare': [[label(k), pct(jf[k], 5), round(1 / jf[k])] for k in order[-400::80]]}
    f_chart = jf[joint]
    tiers = [('Common (more than 1 in 100)', 1e-2, 2), ('Uncommon (1 in 100 to 1 in 1,000)', 1e-3, 1e-2),
             ('Rare (1 in 1,000 to 1 in 10,000)', 1e-4, 1e-3), ('Very rare (under 1 in 10,000)', 0, 1e-4)]
    R['headline_tiers'] = {name: pct(w[(f_chart >= lo) & (f_chart < hi)].sum() / W) for name, lo, hi in tiers}
    qs = _wquantile(f_chart, w, [0.1, 0.25, 0.5, 0.75, 0.9, 0.99])
    R['headline_one_in_x_percentiles'] = {str(q): round(1 / v) for q, v in zip([10, 25, 50, 75, 90, 99], qs)}
    R['_joint'] = {label(k): float(jf[k]) for k in present}
    ys_ = np.arange(years.min(), years.max() + 1)
    R['_joint_by_year'] = np.stack([np.bincount(joint[years == y], minlength=2400) for y in ys_]).astype(np.int32)

    # ---- layer 2: centers
    cen = {}
    for i, name in enumerate(CENTER_NAMES):
        d_ = c['defined'][:, i]
        gates_in = c['gate_center_open'][:, i] > 0
        cen[name] = {'defined': pct(w[d_].sum() / W), 'open_with_gates': pct(w[~d_ & gates_in].sum() / W),
                     'fully_open': pct(w[~d_ & ~gates_in].sum() / W)}
    R['centers'] = cen
    R['n_centers'] = {str(k): pct(v, 3) for k, v in enumerate(share(c['n_centers'], w, 10))}
    nc = share(c['n_channels'], w, 20)
    R['n_channels'] = {str(k): pct(v, 3) for k, v in enumerate(nc) if v > 0}
    R['n_channels_mean'] = round(float((c['n_channels'] * w).sum() / W), 3)
    ng = share(c['n_gates'], w, 27)
    R['n_gates'] = {str(k): pct(v, 3) for k, v in enumerate(ng) if v > 0}
    R['n_gates_mean'] = round(float((c['n_gates'] * w).sum() / W), 2)
    R['hanging_gates_mean'] = {'in_defined_centers': round(float((c['hang_defined'] * w).sum() / W), 2),
                               'in_open_centers': round(float((c['hang_open'] * w).sum() / W), 2)}
    sp = c['definition'] == 2
    R['split_width'] = {'small (one gate bridges it)': pct(w[c['split_width'] == 1].sum() / w[sp].sum()),
                        'wide': pct(w[c['split_width'] == 2].sum() / w[sp].sum())}

    # ---- layer 2: channels, with the birth-year (cohort) range
    ys = np.arange(years.min(), years.max() + 1)
    per_year = len(years) // len(ys)
    ck = c['chan_kind'].reshape(len(ys), per_year, 36)               # sample is sorted by year, equal size
    year_share = (ck > 0).mean(axis=1)                                 # (years, 36)
    win = np.stack([year_share[max(0, i - 2):i + 3].mean(axis=0) for i in range(len(ys))])
    chans = {}
    for k, key in enumerate(CHANNEL_KEYS):
        defd = c['chan_kind'][:, k] > 0
        tot = w[defd].sum()
        kinds = [w[c['chan_kind'][:, k] == j].sum() / tot for j in (1, 2, 3)]
        lo, hi = int(win[:, k].argmin()), int(win[:, k].argmax())
        chans[key] = {'share': pct(tot / W), 'family': FAMILY_OF_CHANNEL[key],
                      'conscious': pct(kinds[0], 1), 'unconscious': pct(kinds[1], 1), 'mixed': pct(kinds[2], 1),
                      'cohort_low': [pct(win[lo, k]), int(ys[lo])], 'cohort_high': [pct(win[hi, k]), int(ys[hi])]}
    R['channels'] = chans
    R['channel_by_year'] = {key: [pct(v, 2) for v in win[:, k]] for k, key in enumerate(CHANNEL_KEYS)}
    R['year_axis'] = [int(y) for y in ys]

    # ---- gates
    gate_share = (c['act'] * w[:, None]).sum(axis=0) / W
    act_y = c['act'].reshape(len(ys), per_year, 64).mean(axis=1)
    gwin = np.stack([act_y[max(0, i - 2):i + 3].mean(axis=0) for i in range(len(ys))])
    R['gates'] = {str(g): {'share': pct(gate_share[g - 1]), 'cohort_low': pct(gwin[:, g - 1].min()),
                           'cohort_high': pct(gwin[:, g - 1].max())} for g in range(1, 65)}
    sun = np.bincount(c['p_sun_gate'], weights=w, minlength=65)[1:] / W
    R['sun_gate'] = {'min': [pct(sun.min(), 3), int(sun.argmin() + 1)], 'max': [pct(sun.max(), 3), int(sun.argmax() + 1)],
                     'ratio': round(float(sun.max() / sun.min()), 4)}

    # ---- crosses: Sun gate x angle (192)
    cross = np.bincount(c['p_sun_gate'].astype(np.int64) * 3 + c['angle'], weights=w, minlength=65 * 3).reshape(65, 3)[1:] / W
    R['crosses'] = {ANGLES[a]: {'mean': pct(cross[:, a].mean(), 4), 'min': pct(cross[:, a].min(), 4),
                                'max': pct(cross[:, a].max(), 4)} for a in range(3)}

    # ---- type by decade
    dec = {}
    for d0 in range(1930, 2030, 10):
        mm = (years >= d0) & (years < d0 + 10)
        if mm.any():
            dec[str(d0) + 's'] = dict(zip(TYPES, map(pct, share(c['type'][mm], np.ones(int(mm.sum())), 5))))
    R['type_by_decade'] = dec

    # ---- layer 3
    ps, ds = c['p_sun'].astype(np.int64) % 1080, c['d_sun'].astype(np.int64) % 1080
    p_col, d_col = (ps % 180) // 30, (ds % 180) // 30
    p_tone, d_tone = (ps % 30) // 5, (ds % 30) // 5
    p_base, d_base = ps % 5, ds % 5
    R['substructure'] = {
        'sun_color_share_range': [pct(np.bincount(p_col, minlength=6).min() / len(ps)), pct(np.bincount(p_col, minlength=6).max() / len(ps))],
        'sun_tone_share_range': [pct(np.bincount(p_tone, minlength=6).min() / len(ps)), pct(np.bincount(p_tone, minlength=6).max() / len(ps))],
        'sun_base_share_range': [pct(np.bincount(p_base, minlength=5).min() / len(ps)), pct(np.bincount(p_base, minlength=5).max() / len(ps))],
        'design_color_minus_personality': {str(k): pct(v) for k, v in enumerate(np.bincount((d_col - p_col) % 6, minlength=6) / len(ps)) if v > 0},
        'design_tone_minus_personality': {str(k): pct(v) for k, v in enumerate(np.bincount((d_tone - p_tone) % 6, minlength=6) / len(ps)) if v > 0},
        'design_base_minus_personality': {str(k): pct(v) for k, v in enumerate(np.bincount((d_base - p_base) % 5, minlength=5) / len(ps)) if v > 0},
    }
    arrows = share(c['arrows'], w, 16)
    name = lambda a: 'P' + ''.join('R' if a & b else 'L' for b in (8, 4)) + ' D' + ''.join('R' if a & b else 'L' for b in (2, 1))
    R['arrows'] = {name(a): pct(arrows[a]) for a in range(16)}
    R['arrow_left_share'] = {'Personality Sun (Motivation)': pct(w[(c['arrows'] & 8) == 0].sum() / W),
                             'Personality Nodes (Perspective)': pct(w[(c['arrows'] & 4) == 0].sum() / W),
                             'Design Sun (Determination)': pct(w[(c['arrows'] & 2) == 0].sum() / W),
                             'Design Nodes (Environment)': pct(w[(c['arrows'] & 1) == 0].sum() / W)}

    # ---- gift families
    scores, chans_n = family_scores(c)
    fam = {}
    pctile = np.zeros(scores.shape, dtype=np.float32)
    for f, (fname, circ) in enumerate(FAMILIES):
        dist = np.bincount(scores[:, f], weights=w, minlength=20) / W
        cum_below = np.concatenate([[0], np.cumsum(dist)[:-1]])
        mid = cum_below + dist / 2
        pctile[:, f] = mid[scores[:, f]]
        top = 1 - cum_below                                          # share with this score or higher
        cd = np.bincount(chans_n[:, f], weights=w, minlength=10) / W
        fam[fname] = {'circuit': circ, 'channels': CIRCUITS[circ], 'max_score': 2 * len(CIRCUITS[circ]),
                      'mean_score': round(float((scores[:, f] * w).sum() / W), 2),
                      'score_top_share': {str(s): pct(top[s], 2) for s in range(20) if dist[s] > 0},
                      'channels_defined': {str(k): pct(v, 2) for k, v in enumerate(cd) if v > 0}}
    best = pctile.max(axis=1, keepdims=True)
    lead = (pctile >= best - 1e-6)
    lead_w = lead / lead.sum(axis=1, keepdims=True)
    R['families'] = fam
    R['family_lead_share'] = {FAMILY_NAMES[f]: pct((lead_w[:, f] * w).sum() / W) for f in range(7)}
    R['families_with_channel'] = {str(k): pct(v, 2) for k, v in enumerate(np.bincount((chans_n > 0).sum(axis=1), weights=w, minlength=8) / W)}
    return R, c, w, years


def _wquantile(x, w, qs):
    order = np.argsort(x)
    cw = np.cumsum(w[order]) / w.sum()
    return [float(x[order][min(np.searchsorted(cw, 1 - q), len(x) - 1)]) for q in qs]


def alltime_tables(z):
    c = compact(z['units'])
    ones = np.ones(len(c['type']))
    return {'n_charts': int(len(ones)), 'type': dict(zip(TYPES, map(pct, share(c['type'], ones, 5)))),
            'authority': dict(zip(AUTHORITIES, map(pct, share(c['authority'], ones, 8)))),
            'definition': dict(zip(DEFINITIONS, map(pct, share(c['definition'], ones, 5)))),
            'head_defined': pct(c['defined'][:, 0].mean()), 'five_channels': pct((c['n_channels'] == 5).mean()),
            'manifestor_with_3_channels': pct(((c['type'] == 3) & (c['n_channels'] == 3)).mean()),
            'arrows_PLL_DLL': pct((c['arrows'] == 0).mean())}


def shift_tables(z):
    layers = z['units']                                  # (1+S, N, 26)
    base = chart.derive(layers[0])
    out = {}
    for s, minutes in enumerate(z['minutes'].tolist(), start=1):
        d = chart.derive(layers[s])
        u0, u1 = layers[0].astype(np.int64), layers[s].astype(np.int64)
        prof = (base['p_line'] != d['p_line']) | (base['d_line'] != d['d_line'])
        out[str(minutes)] = {
            'type': pct((base['type'] != d['type']).mean()), 'authority': pct((base['authority'] != d['authority']).mean()),
            'definition': pct((base['definition'] != d['definition']).mean()), 'profile': pct(prof.mean()),
            'any_channel': pct((base['chan'] != d['chan']).any(axis=1).mean()),
            'any_gate': pct((base['act'] != d['act']).any(axis=1).mean()),
            'any_line': pct(((u0 // 180) != (u1 // 180)).any(axis=1).mean()),
            'sun_color': pct(((u0[:, 0] // 30) != (u1[:, 0] // 30)).mean()),
            'sun_tone': pct(((u0[:, 0] // 5) != (u1[:, 0] // 5)).mean()),
            'sun_base': pct((u0[:, 0] != u1[:, 0]).mean()),
            'design_sun_tone': pct(((u0[:, 13] // 5) != (u1[:, 13] // 5)).mean()),
            'node_tone': pct(((u0[:, 2] // 5) != (u1[:, 2] // 5)).mean()),
            'any_arrow': pct((base['arrows'] != d['arrows']).mean()),
            'moon_line': pct(((u0[:, 4] // 180) != (u1[:, 4] // 180)).mean()),
        }
    return {'n_charts': int(layers.shape[1]), 'by_minutes': out}


if __name__ == '__main__':
    living_path, alltime_path, shift_path, out_path = sys.argv[1:5]
    R, _, _, _ = living_tables(np.load(living_path))
    R['alltime_1781_2030'] = alltime_tables(np.load(alltime_path))
    R['birth_time_error'] = shift_tables(np.load(shift_path))
    R['wheel_order'] = WHEEL
    np.save(out_path.replace('.json', '_joint_by_year.npy'), R.pop('_joint_by_year'))
    with open(out_path, 'w') as fh:
        json.dump(R, fh, indent=1)
    print('wrote', out_path)
