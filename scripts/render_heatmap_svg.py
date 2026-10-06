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
    by_date = {item["date"]: item for item in days}
    start = date.fromisoformat(days[0]["date"])
    start -= timedelta(days=(start.weekday()+1) % 7)
    end = date.fromisoformat(days[-1]["date"])
    weeks = (end-start).days//7+1
    width, height = 1720, 340
    cell, gap = 22, 7
    left, top = 80, 104
    parts = panel(width, height, "datachulee@github: ~$ ./contributions.sh",
                  "DataChuLee's GitHub contributions", f"{total:,} contributions from {days[0]['date']} to {days[-1]['date']}.")
    parts.append(label(30, 76, "GitHub contribution activity", 22, TEXT))
    month = None
    for week in range(weeks):
        day = start + timedelta(days=week*7)
        if day.month != month:
            parts.append(label(left+week*(cell+gap), 92, day.strftime("%b"), 15, DIM))
            month = day.month
    for row, name in [(1,"Mon"), (3,"Wed"), (5,"Fri")]:
        parts.append(label(27, top+row*(cell+gap)+17, name, 14, DIM))
    for item in days:
        day = date.fromisoformat(item["date"])
        offset = (day-start).days
        week, row = divmod(offset, 7)
        color = PALETTE[min(4, max(0, item["level"]))]
        delay = week*.022 + row*.018
        animate = "" if STATIC else (f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".3s" fill="freeze"/>')
        opacity = 1 if STATIC else 0
        parts.append(f'<rect x="{left+week*(cell+gap)}" y="{top+row*(cell+gap)}" width="{cell}" height="{cell}" '
                     f'rx="4" fill="{color}" opacity="{opacity}"><title>{item["date"]}: {item["count"]} contributions</title>{animate}</rect>')
    parts.append(label(30, 321, f"{total:,} contributions · {days[0]['date']} — {days[-1]['date']}", 17, DIM))
    parts.append(label(1450, 321, "Less", 15, DIM))
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{1497+i*25}" y="306" width="19" height="19" rx="3" fill="{color}"/>')
    parts.append(label(1630, 321, "More", 15, DIM))
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
