from pathlib import Path
from io import BytesIO
from html import escape
import requests
from PIL import Image, ImageOps, ImageEnhance

USERNAME = "DataChuLee"
OUT = Path("assets/ascii-profile.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

url = f"https://github.com/{USERNAME}.png?size=460"
resp = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
resp.raise_for_status()

img = Image.open(BytesIO(resp.content)).convert("L")
img = ImageOps.autocontrast(img)
img = ImageEnhance.Contrast(img).enhance(1.35)

cols, rows = 54, 30
img = ImageOps.fit(img, (cols, rows), method=Image.Resampling.LANCZOS)

chars = " .`:-=+*#%@"
pixels = list(img.getdata())
lines = []
for y in range(rows):
    row = pixels[y*cols:(y+1)*cols]
    txt = "".join(chars[min(len(chars)-1, p * len(chars) // 256)] for p in row)
    lines.append(txt)

W, H = 620, 520
line_h = 13
start_y = 105
tspans = []
for i, line in enumerate(lines):
    delay = i * 0.035
    tspans.append(
        f'<text x="34" y="{start_y + i*line_h}" class="ascii" '
        f'style="animation-delay:{delay:.3f}s">{escape(line)}</text>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .panel {{ fill:#0d1117; stroke:#30363d; stroke-width:2; }}
  .bar {{ fill:#161b22; }}
  .dot1 {{ fill:#ff5f56; }} .dot2 {{ fill:#ffbd2e; }} .dot3 {{ fill:#27c93f; }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .head {{ fill:#8b949e; font-size:15px; }}
  .ascii {{ fill:#7ee787; font-size:12px; opacity:0; animation:appear .18s linear forwards; white-space:pre; }}
  .caption {{ fill:#58a6ff; font-size:16px; }}
  @keyframes appear {{ to {{opacity:1}} }}
</style>
<rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/>
<rect class="bar" x="2" y="2" width="{W-4}" height="62" rx="17"/>
<circle class="dot1" cx="32" cy="32" r="8"/><circle class="dot2" cx="58" cy="32" r="8"/><circle class="dot3" cx="84" cy="32" r="8"/>
<text x="120" y="39" class="head">profile — ascii render</text>
{''.join(tspans)}
<text x="34" y="490" class="caption">$ echo "AI Engineer / Agentic AI / RAG"</text>
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT}")
