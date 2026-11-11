# Turns wheel units into chart facts (gates, channels, centers, type, authority, ...), many charts at once.
"""Vectorised with numpy so a million charts take seconds. Works for one chart too."""
import numpy as np

from .tables import (CENTER_INDEX, CENTER_NAMES, CENTER_OF, CHANNELS, UNITS_PER_GATE, WHEEL)

_WHEEL = np.array(WHEEL, dtype=np.int16)
_CH_A = np.array([a for a, _ in CHANNELS])
_CH_B = np.array([b for _, b in CHANNELS])
_CH_CA = np.array([CENTER_INDEX[CENTER_OF[a]] for a, _ in CHANNELS])
_CH_CB = np.array([CENTER_INDEX[CENTER_OF[b]] for _, b in CHANNELS])
_GATE_CENTER = np.zeros(65, dtype=np.int8)
for _g, _c in CENTER_OF.items():
    _GATE_CENTER[_g] = CENTER_INDEX[_c]
HEAD, AJNA, THROAT, G, HEART, SACRAL, SOLAR, SPLEEN, ROOT = range(9)
P_SUN, P_NODE, D_SUN, D_NODE = 0, 2, 13, 15


def split_units(units):
    """units (N,26) -> gate, line, color, tone, base arrays, each (N,26)."""
    u = np.asarray(units, dtype=np.int64)
    gate = _WHEEL[u // UNITS_PER_GATE]
    r = u % UNITS_PER_GATE
    return gate, r // 180 + 1, (r % 180) // 30 + 1, (r % 30) // 5 + 1, r % 5 + 1


def _active(gate):
    n = gate.shape[0]
    act = np.zeros((n, 65), dtype=bool)
    act[np.arange(n)[:, None], gate] = True
    return act


def derive(units):
    """All chart facts for units (N,26). Returns a dict of numpy arrays."""
    units = np.atleast_2d(np.asarray(units))
    gate, line, color, tone, base = split_units(units)
    n = gate.shape[0]
    act = _active(gate)
    act_p = _active(gate[:, :13])
    act_d = _active(gate[:, 13:])
    chan = act[:, _CH_A] & act[:, _CH_B]                               # (N,36)
    # how each defined channel is made: 1 conscious only, 2 unconscious only, 3 mixed
    chan_p = act_p[:, _CH_A] & act_p[:, _CH_B]
    chan_d = act_d[:, _CH_A] & act_d[:, _CH_B]
    chan_kind = np.where(~chan, 0, np.where(chan_p & ~chan_d, 1, np.where(chan_d & ~chan_p, 2, 3))).astype(np.int8)

    defined = np.zeros((n, 9), dtype=bool)
    for k in range(36):
        defined[:, _CH_CA[k]] |= chan[:, k]
        defined[:, _CH_CB[k]] |= chan[:, k]

    # connected groups of defined centers (label = lowest center index in the group)
    labels = np.where(defined, np.arange(9)[None, :], 99).astype(np.int8)
    for _ in range(8):
        for k in range(36):
            m = chan[:, k]
            ca, cb = _CH_CA[k], _CH_CB[k]
            mn = np.minimum(labels[:, ca], labels[:, cb])
            labels[:, ca] = np.where(m, mn, labels[:, ca])
            labels[:, cb] = np.where(m, mn, labels[:, cb])
    groups = (defined & (labels == np.arange(9)[None, :])).sum(axis=1)

    def linked(c):
        return defined[:, c] & defined[:, THROAT] & (labels[:, c] == labels[:, THROAT])
    motor_throat = linked(HEART) | linked(SOLAR) | linked(ROOT) | linked(SACRAL)
    any_def = defined.any(axis=1)
    ctype = np.full(n, 2, dtype=np.int8)                               # Projector
    ctype[~defined[:, SACRAL] & motor_throat] = 3                      # Manifestor
    ctype[defined[:, SACRAL]] = 0                                      # Generator
    ctype[defined[:, SACRAL] & motor_throat] = 1                       # Manifesting Generator
    ctype[~any_def] = 4                                                # Reflector

    auth = np.full(n, 6, dtype=np.int8)                                # Mental
    auth[defined[:, G]] = 5                                            # Self-Projected
    auth[defined[:, HEART]] = 4                                        # Ego Projected
    auth[defined[:, HEART] & (ctype == 3)] = 3                         # Ego Manifested
    auth[defined[:, SPLEEN]] = 2
    auth[defined[:, SACRAL]] = 1
    auth[defined[:, SOLAR]] = 0
    auth[~any_def] = 7                                                 # Lunar

    pl, dl = line[:, P_SUN], line[:, D_SUN]
    angle = np.where((pl == 4) & (dl == 1), 1, np.where(pl >= 5, 2, 0)).astype(np.int8)
    # four arrows: tone 1-3 = left (0), 4-6 = right (1); order P-Sun, P-Node, D-Sun, D-Node
    arrows = ((tone[:, [P_SUN, P_NODE, D_SUN, D_NODE]] >= 4) * np.array([8, 4, 2, 1])).sum(axis=1).astype(np.int8)

    return dict(gate=gate, line=line, color=color, tone=tone, base=base, act=act, act_p=act_p, act_d=act_d,
                chan=chan, chan_kind=chan_kind, defined=defined, labels=labels, groups=groups.astype(np.int8),
                type=ctype, authority=auth, definition=np.minimum(groups, 4).astype(np.int8),
                p_line=pl.astype(np.int8), d_line=dl.astype(np.int8), angle=angle, arrows=arrows,
                n_channels=chan.sum(axis=1).astype(np.int8), n_centers=defined.sum(axis=1).astype(np.int8),
                n_gates=act.sum(axis=1).astype(np.int8))


def split_width(d):
    """For Split Definition charts: 1 = a single gate bridges the two halves (small split), 2 = wide. 0 otherwise."""
    chan, act, labels, defined = d['chan'], d['act'], d['labels'], d['defined']
    is_split = d['groups'] == 2
    small = np.zeros(len(is_split), dtype=bool)
    for k in range(36):
        ca, cb = _CH_CA[k], _CH_CB[k]
        across = defined[:, ca] & defined[:, cb] & (labels[:, ca] != labels[:, cb])
        one_gate = act[:, _CH_A[k]] ^ act[:, _CH_B[k]]
        small |= across & one_gate & ~chan[:, k]
    return np.where(is_split, np.where(small, 1, 2), 0).astype(np.int8)


def hanging_gates(d):
    """Count of active gates whose channel partner is missing, split into: in a defined center / in an open center."""
    act, chan, defined = d['act'], d['chan'], d['defined']
    n = act.shape[0]
    in_chan = np.zeros((n, 65), dtype=bool)
    for k in range(36):
        in_chan[:, _CH_A[k]] |= chan[:, k]
        in_chan[:, _CH_B[k]] |= chan[:, k]
    lone = act & ~in_chan
    lone[:, 0] = False
    center_def = defined[:, _GATE_CENTER]            # (N,65): is that gate's center defined
    return (lone & center_def).sum(axis=1), (lone & ~center_def).sum(axis=1)


def describe(units):
    """Plain dict for ONE chart (used by tests and the worked example)."""
    from .tables import ANGLES, AUTHORITIES, BODIES, CHANNEL_KEYS, DEFINITIONS, TYPES
    d = derive([units])
    place = lambda i: dict(gate=int(d['gate'][0, i]), line=int(d['line'][0, i]), color=int(d['color'][0, i]),
                           tone=int(d['tone'][0, i]), base=int(d['base'][0, i]))
    return dict(
        type=TYPES[d['type'][0]], authority=AUTHORITIES[d['authority'][0]], definition=DEFINITIONS[d['definition'][0]],
        profile='%d/%d' % (d['p_line'][0], d['d_line'][0]), angle=ANGLES[d['angle'][0]],
        centers=[CENTER_NAMES[i] for i in range(9) if d['defined'][0, i]],
        channels=[CHANNEL_KEYS[k] for k in range(36) if d['chan'][0, k]],
        channel_kind={CHANNEL_KEYS[k]: int(d['chan_kind'][0, k]) for k in range(36) if d['chan'][0, k]},
        arrows=''.join('R' if d['arrows'][0] & b else 'L' for b in (8, 4, 2, 1)),
        personality={b: place(i) for i, b in enumerate(BODIES)},
        design={b: place(13 + i) for i, b in enumerate(BODIES)},
    )
