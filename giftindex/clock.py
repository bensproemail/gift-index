# Turns a birth date, clock time and time zone into the one true moment (UTC), and says which clock rule applied.
"""Uses the IANA time-zone database through Python's zoneinfo. The web page does the same job with the browser's
own copy of that database (web/engine/clock.js); a test makes the two agree."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def _ms(dt):
    return int(round(dt.timestamp() * 1000))


def local_to_utc(year, month, day, hour, minute, zone):
    """Returns dict(status, ms, ms_second, offset_minutes, rule).
    status: 'ok'; 'gap' = that clock time never happened (clocks jumped forward), ms is None;
    'twice' = it happened twice (clocks went back): ms is the first time, ms_second the second."""
    tz = ZoneInfo(zone)
    first = datetime(year, month, day, hour, minute, tzinfo=tz, fold=0)
    second = first.replace(fold=1)
    back = first.astimezone(UTC).astimezone(tz)
    if (back.year, back.month, back.day, back.hour, back.minute) != (year, month, day, hour, minute):
        return dict(status='gap', ms=None, ms_second=None, offset_minutes=None, rule=None)
    out = dict(status='ok', ms=_ms(first), ms_second=None,
               offset_minutes=int(first.utcoffset().total_seconds() // 60), rule=rule_text(first))
    if first.utcoffset() != second.utcoffset():
        out.update(status='twice', ms_second=_ms(second))
    return out


def rule_text(dt):
    """Plain words for the clock rule in force, e.g. 'CST (UTC-06:00), daylight time off'."""
    off = dt.utcoffset().total_seconds()
    sign = '-' if off < 0 else '+'
    off = abs(int(off))
    daylight = bool(dt.dst())
    return '%s (UTC%s%02d:%02d), daylight time %s' % (dt.tzname(), sign, off // 3600, off % 3600 // 60,
                                                    'on' if daylight else 'off')
