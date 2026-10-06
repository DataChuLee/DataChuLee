"""Generate the contribution heatmap and a matching activity statistics card."""
from datetime import date, timedelta
import json

from profile_common import ASSETS, PALETTE, STATIC, label, today, write_svg
from profile_stats import render_stats_card


def read_days():
    days = json.loads((ASSETS / "contributions.json").read_text(encoding="utf-8"))
    days = sorted((d for d in days if date.fromisoformat(d["date"]) <= today()), key=lambda d: d["date"])
    if not days:
        raise ValueError("No contribution data")
    return days


def stats(days):
    run = best = 0
    for item in days:
        run = run + 1 if item["count"] > 0 else 0
        best = max(best, run)
    by_date = {item["date"]: item for item in days}
    end = today()
    if by_date.get(end.isoformat(), {}).get("count", 0) == 0:
        end -= timedelta(days=1)
    current = 0
    while by_date.get(end.isoformat(), {}).get("count", 0) > 0:
        current += 1
        end -= timedelta(days=1)
    return sum(item["count"] for item in days), current, best


def heatmap(days):
    total, _, _ = stats(days)
    start = date.fromisoformat(days[0]["date"])
    start -= timedelta(days=(start.weekday()+1) % 7)
    end = date.fromisoformat(days[-1]["date"])
    weeks = (end-start).days//7+1
    # Match the reference's current borderless calendar and pop/flash reveal.
    # Its older render_heatmap_svg.py still draws a terminal window; the live
    # reference profile instead uses scripts/generate_streak_svg.py.
    cell, gap, left, top = 13, 3, 34, 24
    step = cell + gap
    width, height = left + weeks*step + 6, top + 7*step + 22
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
        '<title id="title">DataChuLee\'s GitHub contribution activity</title>',
        f'<desc id="desc">{total:,} contributions from {days[0]["date"]} to {days[-1]["date"]}. '
        'Cells reveal diagonally; active cells briefly brighten.</desc>',
    ]
    if STATIC:
        parts.append('<style>.lbl{fill:#7d8590;font-size:13px;font-weight:600}'
                     '.total{fill:#e6edf3;font-size:15px;font-weight:700}.c{opacity:1}</style>')
    else:
        parts.append('<style>\n'
                     '.lbl{fill:#7d8590;font-size:13px;font-weight:600}\n'
                     '.total{fill:#e6edf3;font-size:15px;font-weight:700}\n'
                     '.c{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .55s ease-out both}\n'
                     '.g{animation:pop .55s ease-out both,flash .7s ease-out both}\n'
                     '@keyframes pop{0%{opacity:0;transform:scale(.2)}60%{opacity:1;transform:scale(1.1)}100%{opacity:1;transform:scale(1)}}\n'
                     '@keyframes flash{0%{filter:brightness(2.4)}45%{filter:brightness(2.4)}100%{filter:brightness(1)}}\n'
                     '@media(prefers-reduced-motion:reduce){.c{opacity:1!important;animation:none!important}}\n'
                     '</style>')
    month = None
    for week in range(weeks):
        day = start + timedelta(days=week*7)
        if day.month != month:
            parts.append(label(left+week*step, 16, day.strftime("%b"), extra='class="lbl"'))
            month = day.month
    for row, name in [(1,"Mon"), (3,"Wed"), (5,"Fri")]:
        parts.append(label(2, top+row*step+cell-2, name, extra='class="lbl"'))
    max_order = max(1, weeks-1+6*.55)
    for item in days:
        day = date.fromisoformat(item["date"])
        offset = (day-start).days
        week, row = divmod(offset, 7)
        level = min(4, max(0, item["level"]))
        delay = (week+row*.55)/max_order*3.6
        cls = "c g" if level else "c e"
        parts.append(f'<rect class="{cls}" x="{left+week*step}" y="{top+row*step}" width="{cell}" height="{cell}" '
                     f'rx="2.5" fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
                     f'<title>{item["date"]}: {item["count"]} contributions</title></rect>')
    parts.append(label(left, height-6, f"{total:,} contributions in the last year", extra='class="total"'))
    write_svg("contribution.svg", parts)


def stats_card(days):
    render_stats_card(days, stats(days))

if __name__ == "__main__":
    days = read_days()
    heatmap(days)
    stats_card(days)
