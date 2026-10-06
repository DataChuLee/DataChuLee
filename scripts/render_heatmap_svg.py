from pathlib import Path
from datetime import date, timedelta
import json

IN = Path("assets/contributions.json")
OUT = Path("assets/contribution.svg")
items = json.loads(IN.read_text(encoding="utf-8")) if IN.exists() else []
by_date = {x["date"]: x for x in items}

today = date.today()
start = today - timedelta(days=371)
start -= timedelta(days=(start.weekday()+1) % 7)
weeks = 53

W, H = 920, 250
left, top = 65, 92
cell, gap = 12, 4
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

total = sum(x.get("count", 0) for x in items)
best_streak = 0
running = 0
for d in sorted(by_date):
    if by_date[d].get("count", 0) > 0:
        running += 1
        best_streak = max(best_streak, running)
    else:
        running = 0

current_streak = 0
d = today
while by_date.get(d.isoformat(), {}).get("count", 0) > 0:
    current_streak += 1
    d -= timedelta(days=1)

rects = []
for w in range(weeks):
    for day in range(7):
        dt = start + timedelta(days=w*7+day)
        if dt > today:
            continue
        item = by_date.get(dt.isoformat(), {"level":0, "count":0})
        level = max(0, min(4, int(item.get("level", 0))))
        x = left + w*(cell+gap)
        y = top + day*(cell+gap)
        delay = (w*7+day)*0.002
        rects.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{palette[level]}" class="day" style="animation-delay:{delay:.3f}s">'
            f'<title>{dt.isoformat()}: {item.get("count",0)} contributions</title></rect>'
        )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .panel {{ fill:#0d1117; stroke:#30363d; stroke-width:2; }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .title {{ fill:#7ee787; font-size:20px; font-weight:700; }}
  .sub {{ fill:#8b949e; font-size:13px; }}
  .stat {{ fill:#c9d1d9; font-size:14px; }}
  .day {{ opacity:0; animation:pop .24s ease forwards; transform-box:fill-box; transform-origin:center; }}
  @keyframes pop {{ from {{opacity:0; transform:scale(.65)}} to {{opacity:1; transform:scale(1)}} }}
</style>
<rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/>
<text x="34" y="42" class="title">$ ./contributions.sh</text>
<text x="34" y="68" class="sub">53-week GitHub activity · auto-refreshed daily</text>
<text x="610" y="42" class="stat">Total {total} · Current {current_streak}d · Best {best_streak}d</text>
{''.join(rects)}
<text x="34" y="226" class="sub">less</text>
<rect x="72" y="215" width="10" height="10" rx="2" fill="{palette[0]}"/>
<rect x="88" y="215" width="10" height="10" rx="2" fill="{palette[1]}"/>
<rect x="104" y="215" width="10" height="10" rx="2" fill="{palette[2]}"/>
<rect x="120" y="215" width="10" height="10" rx="2" fill="{palette[3]}"/>
<rect x="136" y="215" width="10" height="10" rx="2" fill="{palette[4]}"/>
<text x="153" y="226" class="sub">more</text>
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT}")
