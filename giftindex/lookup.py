# The lookup tool, command-line version: type a birth moment, get the Gift Index reading as plain text.
"""Usage: python3 -m giftindex.lookup 1980-03-04 07:42 America/Chicago [--json] [--second]
(That example is the made-up Sample Reader. Never commit a real person's birth details: see CLAUDE.md.)
--second picks the second pass of a clock time that happened twice (the hour clocks went back)."""
import json
import sys
from datetime import datetime, timezone

from . import clock
from .claims import ARROW_NAMES
from .reading import load_reference
from .report import report


def _pct(x):
    return '%.1f%%' % x if x >= 1 else '%.2f%%' % x


def _one_in(n):
    return 'not seen in the count' if n is None else '1 in {:,}'.format(n)


def render(rep, receipt):
    """The report as plain text lines. Every figure is labeled with where it comes from."""
    c, h = rep['chart'], rep['headline']
    out = ['READ FROM: ' + receipt, 'Design moment (UTC): ' + rep['moment']['design_utc'], '',
           'CHART (calculated)',
           '  Type: %s   Authority: %s   Definition: %s' % (c['type'], c['authority'], c['definition']),
           '  Profile: %s, %s cross' % (c['profile'], c['angle']),
           '  Defined centers: ' + (', '.join(c['centers']) or 'none'),
           '  Different gates: %d   Channels: %d' % (rep['n_gates'], rep['n_channels']),
           '  Arrows: ' + ', '.join('%s %s' % (n, 'right' if a == 'R' else 'left') for n, a in zip(ARROW_NAMES, c['arrows'])),
           '  Personality Sun: gate {gate}, line {line}, Color {color}, Tone {tone}, Base {base}'.format(**c['personality']['Sun']),
           '', 'RARITY (COUNT: our own count of 2,020,000 charts)',
           '  Headline setup: ' + h['label'],
           '  Among all living people: %s (%s)' % (_one_in(h['living_one_in']) if h['living_share'] > 0 else 'not seen in the count', h['tier'])]
    if h['cohort_years']:
        out.append('  Among people born %d to %d: %s (%d of %s charts)' % (
            h['cohort_years'][0], h['cohort_years'][1], _one_in(h['cohort_one_in']), h['cohort_hits'], '{:,}'.format(h['cohort_charts'])))
    else:
        out.append('  Among people born near the same year: not counted (the count covers births 1926 to 2026)')
    for ch in rep['channels']:
        out.append('  Channel %s %s (%s): %s of living people%s' % (
            ch['channel'], ch['name'], ch['made'], _pct(ch['living']),
            '' if ch['cohort'] is None else ', %s of people born near the same year' % _pct(ch['cohort'])))
    out += ['', 'GIFT SCORES (claims of the tradition, not proven; family names are our labels, MINE)']
    for f in rep['families']:
        standing = 'no score' if f['score'] == 0 else 'top %s of living people' % _pct(f['top_share'])
        out.append('  %-16s %2d of %-2d  %s%s' % (f['family'], f['score'], f['max'], standing, '  <- lead gift' if f['lead'] else ''))
        if f['score'] > 0:
            out.append('      Claim (%s): %s  Downside: %s' % (f['label'], f['claim'], f['downside']))
    for ch in rep['channels']:
        out.append('  %s %s (%s, p.%d): %s  Off course: %s' % (ch['channel'], ch['name'], ch['label'], ch['page'], ch['claim'], ch['off_course']))
    out += ['', 'GENE KEYS LAYER (GK: a separate system by Richard Rudd)']
    out += ['  %s (%s): %d %s' % (k['sphere'], k['source'], k['gate'], k['gift']) for k in rep['gene_keys']]
    out += ['', 'IF THE BIRTH TIME IS OFF (smallest error that changes each fact, checked up to 60 minutes)']
    names = dict(type='Type', authority='Authority', definition='Definition', profile='Profile', channels='Channels',
                 gates='Gates', sun_color="Sun's Color", sun_tone="Sun's Tone", arrows='Arrows')
    out += ['  %-12s %s' % (names[k], 'holds' if v is None else 'changes within %d minutes' % v) for k, v in rep['sensitivity'].items()]
    return out


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if len(args) != 3:
        print(__doc__)
        return 2
    y, m, d = (int(x) for x in args[0].split('-'))
    hh, mm = (int(x) for x in args[1].split(':'))
    t = clock.local_to_utc(y, m, d, hh, mm, args[2])
    if t['status'] == 'gap':
        print('That clock time never happened there: the clocks jumped forward. Check the birth time.')
        return 1
    ms = t['ms_second'] if (t['status'] == 'twice' and '--second' in argv) else t['ms']
    receipt = '%s %s, %s; clock rule %s; UTC %s' % (args[0], args[1], args[2], t['rule'],
                                                  datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M'))
    if t['status'] == 'twice':
        receipt += ' (this clock time happened twice; using the %s pass)' % ('second' if '--second' in argv else 'first')
    rep = report(ms, load_reference())
    print(json.dumps(rep, indent=1) if '--json' in argv else '\n'.join(render(rep, receipt)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
