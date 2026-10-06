"""Generate the contribution heatmap and a matching activity statistics card."""
from collections import defaultdict
from datetime import date, timedelta
import json

from profile_common import ASSETS, BLUE, BORDER, DIM, GREEN, PALETTE, STATIC, TEXT, label, panel, today, write_svg


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
    total, current, best = stats(days)
    active = sum(item["count"] > 0 for item in days)
    best_day = max(item["count"] for item in days)
    width, height = 840, 880
    parts = panel(width, height, "datachulee@github: ~$ ./stats.sh",
                  "DataChuLee's GitHub activity statistics",
                  f"{total:,} contributions, current streak {current} days, longest streak {best} days.")
    if not STATIC:
        parts.append('<style>@keyframes reveal{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}'
                     '.reveal{animation:reveal .5s ease both}@media(prefers-reduced-motion:reduce){.reveal{animation:none}}</style>')
    parts.append('<g class="reveal">')
    parts += [label(42, 94, "DataChuLee@github", 26, GREEN),
              label(42, 121, "ACTIVITY / PUBLIC CONTRIBUTIONS", 14, DIM),
              label(42, 204, f"{total:,}", 70, TEXT),
              label(42, 238, "contributions in the calendar", 20, DIM), '</g>']
    for index, (name, value, detail) in enumerate([
        ("CURRENT STREAK", f"{current} {'day' if current == 1 else 'days'}", "today or yesterday"),
        ("LONGEST STREAK", f"{best} {'day' if best == 1 else 'days'}", "within this calendar"),
        ("ACTIVE DAYS", str(active), "days with contributions"),
    ]):
        x = 42 + index*255
        parts.append(f'<g class="reveal" style="animation-delay:{.2+index*.12:.2f}s">')
        parts += [f'<rect x="{x}" y="280" width="238" height="142" rx="10" fill="#161b22" stroke="{BORDER}"/>',
                  label(x+18, 311, name, 14, BLUE), label(x+18, 365, value, 32, TEXT),
                  label(x+18, 397, detail, 12, DIM), '</g>']
    monthly = defaultdict(int)
    for item in days:
        monthly[item["date"][:7]] += item["count"]
    months = sorted(monthly)[-12:]
    max_value = max((monthly[m] for m in months), default=0) or 1
    parts.append('<g class="reveal" style="animation-delay:.65s">')
    parts += [label(42, 477, "MONTHLY CONTRIBUTIONS", 16, BLUE),
              label(42, 505, "12 calendar months · latest month may be partial", 13, DIM)]
    for i, month in enumerate(months):
        x = 55+i*61
        bar_height = 160*monthly[month]/max_value
        value = monthly[month]
        parts.append(f'<rect x="{x}" y="{710-bar_height:.2f}" width="35" height="{max(bar_height,2):.2f}" rx="4" fill="{GREEN if i==len(months)-1 else '#238636'}"/>')
        parts += [label(x+17.5, 695-bar_height, str(value), 12, DIM, 'text-anchor="middle"'),
                  label(x+17.5, 738, date.fromisoformat(month+"-01").strftime("%b"), 12, DIM, 'text-anchor="middle"')]
    parts += [label(42, 782, f"Best day: {best_day:,} contributions", 16, TEXT),
              label(42, 810, f"Calendar: {days[0]['date']} — {days[-1]['date']}", 14, DIM), '</g>',
              f'<path d="M0 850 H840" stroke="{BORDER}"/>',
              label(20, 870, "Source: GitHub public calendar · refreshed daily", 13, DIM)]
    write_svg("stats.svg", parts)


if __name__ == "__main__":
    days = read_days()
    heatmap(days)
    stats_card(days)
