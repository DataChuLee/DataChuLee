from pathlib import Path
from io import BytesIO
from html import escape
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageEnhance

USERNAME = "DataChuLee"
OUT = Path("assets/terminal-profile.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

r = requests.get(f"https://github.com/{USERNAME}.png?size=460", timeout=30,
                 headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()
img = Image.open(BytesIO(r.content)).convert("L")
img = ImageOps.autocontrast(img)
img = ImageEnhance.Contrast(img).enhance(1.45)
cols, rows = 48, 26
img = ImageOps.fit(img, (cols, rows), method=Image.Resampling.LANCZOS)
chars = " .`:-=+*#%@"
pixels = list(img.getdata())
ascii_lines = []
for y in range(rows):
    row = pixels[y*cols:(y+1)*cols]
    ascii_lines.append("".join(chars[min(len(chars)-1, p*len(chars)//256)] for p in row))

r = requests.get(f"https://github.com/users/{USERNAME}/contributions", timeout=30,
                 headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
by_date = {}
for node in soup.select("[data-date]"):
    d = node.get("data-date")
    level = node.get("data-level")
    count = node.get("data-count")
    if d and level is not None:
        by_date[d] = {
            "level": int(level),
            "count": int(count) if str(count).isdigit() else 0,
        }

W, H = 1100, 780
bg, panel, border = "#0d1117", "#161b22", "#30363d"
green, blue, text, dim = "#7ee787", "#58a6ff", "#c9d1d9", "#8b949e"
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

ascii_svg = []
for i, line in enumerate(ascii_lines):
    y = 145 + i * 15
    delay = 0.25 + i * 0.035
    ascii_svg.append(
        f'<text x="54" y="{y}" class="ascii" style="animation-delay:{delay:.3f}s">{escape(line)}</text>'
    )

info = [
    ("OS", "AI Engineer"),
    ("Host", "GitHub / DataChuLee"),
    ("Kernel", "LangGraph · LangChain"),
    ("Shell", "Python · FastAPI"),
    ("Memory", "FAISS · BM25 · Redis"),
    ("Focus", "AI Agent · RAG · Multi-Agent"),
    ("Eval", "Hit@K · MRR · Latency · Regression"),
]
info_svg = []
for i, (k, v) in enumerate(info):
    y = 180 + i * 42
    delay = 0.55 + i * 0.10
    info_svg.append(
        f'<text x="610" y="{y}" class="info" style="animation-delay:{delay:.2f}s">'
        f'<tspan class="key">{escape(k)}</tspan><tspan dx="18" class="val">{escape(v)}</tspan></text>'
    )

heat = []
today = date.today()
start = today - timedelta(days=371)
start -= timedelta(days=(start.weekday()+1) % 7)
cell, gap = 11, 4
left, top = 82, 585
for w in range(53):
    for day in range(7):
        dt = start + timedelta(days=w*7 + day)
        if dt > today:
            continue
        item = by_date.get(dt.isoformat(), {"level": 0, "count": 0})
        level = max(0, min(4, item["level"]))
        x = left + w*(cell+gap)
        y = top + day*(cell+gap)
        delay = 1.15 + (w*7+day)*0.0015
        heat.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{palette[level]}" '
            f'class="day" style="animation-delay:{delay:.3f}s"><title>{dt}: {item["count"]} contributions</title></rect>'
        )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .frame {{ fill:{bg}; stroke:{border}; stroke-width:2; }}
  .topbar {{ fill:{panel}; }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .muted {{ fill:{dim}; font-size:15px; }}
  .prompt {{ fill:{green}; font-size:20px; font-weight:700; }}
  .ascii {{ fill:{green}; font-size:13px; white-space:pre; opacity:0; animation:fade .18s linear forwards; }}
  .info {{ font-size:17px; opacity:0; animation:slide .35s ease forwards; }}
  .key {{ fill:{blue}; font-weight:700; }}
  .val {{ fill:{text}; }}
  .day {{ opacity:0; transform-box:fill-box; transform-origin:center; animation:pop .18s ease forwards; }}
  .cursor {{ fill:{green}; animation:blink 1s steps(1) infinite; }}
  @keyframes fade {{ to {{opacity:1}} }}
  @keyframes slide {{ from {{opacity:0; transform:translateX(10px)}} to {{opacity:1; transform:translateX(0)}} }}
  @keyframes pop {{ from {{opacity:0; transform:scale(.65)}} to {{opacity:1; transform:scale(1)}} }}
  @keyframes blink {{ 50% {{opacity:0}} }}
</style>
<rect class="frame" x="1" y="1" width="1098" height="778" rx="16"/>
<rect class="topbar" x="2" y="2" width="1096" height="54" rx="15"/>
<circle cx="28" cy="28" r="7" fill="#ff5f56"/><circle cx="52" cy="28" r="7" fill="#ffbd2e"/><circle cx="76" cy="28" r="7" fill="#27c93f"/>
<text x="100" y="34" class="muted">datachulee@github: ~</text>
<text x="42" y="94" class="prompt">datachulee@github:~$ neofetch</text>
{''.join(ascii_svg)}
<text x="610" y="135" class="prompt">DataChuLee@github</text>
<text x="610" y="154" class="muted">------------------------------</text>
{''.join(info_svg)}
<text x="42" y="535" class="prompt">datachulee@github:~$ ./contributions.sh</text>
<text x="42" y="560" class="muted">53-week contribution activity</text>
{''.join(heat)}
<text x="42" y="742" class="prompt">datachulee@github:~$</text>
<rect x="290" y="724" width="11" height="21" class="cursor"/>
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT}")
