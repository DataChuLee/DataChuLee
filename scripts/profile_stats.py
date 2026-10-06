"""Six animated activity tiles and a growing monthly chart for the profile."""
from collections import defaultdict
from datetime import date, timedelta
from html import escape

from profile_common import BORDER, DIM, STATIC, label, panel, today, write_svg

INK = "#e6edf3"
ACCENT = "#39d353"
BAR = "#26a641"


def short_date(value):
    return f"{value.strftime('%b')} {value.day}"


def date_span(start, end):
    return f"{short_date(start)} – {short_date(end)}" if start and end else "—"


def streak_dates(days, current):
    by_date = {item["date"]: item["count"] for item in days}
    end = today()
    if not by_date.get(end.isoformat(), 0):
        end -= timedelta(days=1)
    current_caption = date_span(end-timedelta(days=current-1), end) if current else "—"
    run = longest = 0
    run_start = longest_start = longest_end = None
    for item in days:
        day = date.fromisoformat(item["date"])
        if item["count"]:
            if not run:
                run_start = day
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, run_start, day
        else:
            run = 0
    return current_caption, date_span(longest_start, longest_end)


def format_number(value, decimal):
    return f"{value:,.1f}" if decimal else f"{round(value):,}"


def number_text(x, y, value, suffix, accent, extra="", animations=""):
    return (f'<text x="{x}" y="{y}" font-size="54" font-weight="700" fill="{accent}" {extra}>'
            f'{value}<tspan dx="8" font-size="24" font-weight="400" fill="{DIM}">{escape(suffix.strip())}</tspan>'
            f'{animations}</text>')


def count_up(x, y, value, suffix, accent, start):
    decimal = isinstance(value, float)
    final = format_number(value, decimal)
    if STATIC:
        return [number_text(x, y, final, suffix, accent, 'class="number-static"')]
    parts = [number_text(x, y, final, suffix, accent, 'class="number-final"')]
    for frame in range(1, 17):
        progress = frame/16
        number = value*(1-(1-progress)**3)
        begin = start+1.2*(frame-1)/16
        end = start+1.2*frame/16
        animations = f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
        if frame < 16:
            animations += f'<set attributeName="opacity" to="0" begin="{end:.3f}s"/>'
        parts.append(number_text(x, y, format_number(number, decimal), suffix, accent,
                                 f'class="number-frame" data-frame="{frame}" opacity="0"', animations))
    return parts


def render_stats_card(days, counts):
    total, current, longest = counts
    active = sum(item["count"] > 0 for item in days)
    best_day = max(days, key=lambda item: item["count"])
    current_span, longest_span = streak_dates(days, current)
    tiles = [
        ("current streak", current, " day" if current == 1 else " days", current_span, ACCENT),
        ("longest streak", longest, " day" if longest == 1 else " days", longest_span, INK),
        ("contributions", total, "", "in the last year", INK),
        ("active days", active, f" / {len(days)}", f"{active/len(days):.0%} of the calendar", INK),
        ("best day", best_day["count"], "", short_date(date.fromisoformat(best_day["date"])), INK),
        ("avg / active day", round(total/active, 1) if active else 0.0, "", "contributions", INK),
    ]
    parts = panel(840, 880, "datachulee@github: ~$ ./stats.sh",
                  "DataChuLee's GitHub activity statistics",
                  f"{total:,} contributions; current streak {current}; longest streak {longest}; "
                  f"{active} active days; best day {best_day['count']} contributions. All values use the public calendar.")
    if not STATIC:
        parts.append('<style>\n'
                     '.tile{opacity:0;animation:enter .45s ease-out both}\n'
                     '@keyframes enter{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}\n'
                     '.bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .6s ease-out both}\n'
                     '@keyframes grow{to{transform:scaleY(1)}}\n'
                     '.number-final{display:none}\n'
                     '@media(prefers-reduced-motion:reduce){.tile,.bar{opacity:1!important;transform:none!important;animation:none!important}'
                     '.number-frame{display:none!important}.number-final{display:inline!important}}\n'
                     '</style>')
    for index, (name, value, suffix, caption, accent) in enumerate(tiles):
        x = 20+(index%2)*408
        y = 54+(index//2)*166
        delay = index*.15
        parts.append(f'<g class="tile" data-stat="{name}" style="animation-delay:{delay:.2f}s">')
        parts += [f'<rect x="{x}" y="{y}" width="392" height="150" rx="10" fill="#161b22" stroke="{BORDER}"/>',
                  label(x+24, y+40, "$ "+name, 22, DIM)]
        parts += count_up(x+24, y+100, value, suffix, accent, delay+.27)
        parts += [label(x+24, y+132, caption, 20, DIM), '</g>']

    monthly = defaultdict(int)
    for item in days:
        monthly[item["date"][:7]] += item["count"]
    months = sorted(monthly)
    peak = max(monthly.values()) or 1
    parts += ['<g class="tile" style="animation-delay:1s">',
              f'<rect x="20" y="552" width="800" height="308" rx="10" fill="#161b22" stroke="{BORDER}"/>',
              label(44, 592, "$ contributions / month", 22, DIM), '</g>']
    slot = 752/len(months)
    bar_width = slot*.62
    for index, month in enumerate(months):
        value = monthly[month]
        # Zero months have a subtle 2px baseline, as in the reference chart.
        height = max(2, 204*value/peak)
        x = 44+index*slot+(slot-bar_width)/2
        delay = 1.3+index*.06
        color = ACCENT if value == peak else BAR
        parts.append(f'<rect class="bar" data-month="{month}" data-count="{value}" '
                     f'x="{x:.1f}" y="{820-height:.1f}" width="{bar_width:.1f}" height="{height:.1f}" '
                     f'rx="3" fill="{color}" style="animation-delay:{delay:.2f}s">'
                     f'<title>{month}: {value} contributions</title></rect>')
        mon = date.fromisoformat(month+"-01").strftime("%b")[0]
        parts.append(label(round(x+bar_width/2, 1), 848, mon, 18, DIM, 'text-anchor="middle"'))
        if value == peak:
            parts.append(label(round(x+bar_width/2, 1), round(810-height, 1), f"{value:,}", 18, INK,
                               f'class="tile" style="animation-delay:{delay+.6:.2f}s" text-anchor="middle"'))
    write_svg("stats.svg", parts)
