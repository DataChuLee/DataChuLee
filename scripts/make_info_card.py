from pathlib import Path
from html import escape

OUT = Path("assets/info-card.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

rows = [
    ("USER", "DataChuLee"),
    ("ROLE", "AI Engineer"),
    ("FOCUS", "AI Agent · RAG · LangGraph"),
    ("STACK", "Python · FastAPI · Redis · FAISS"),
    ("EVAL", "Hit@K · MRR · Latency · Regression"),
    ("NOW", "Building reliable agentic AI systems"),
]

W, H = 720, 520
lines = []
for i, (k, v) in enumerate(rows):
    y = 160 + i * 54
    delay = 0.35 + i * 0.13
    lines.append(
        f'<text x="54" y="{y}" class="row" style="animation-delay:{delay:.2f}s">'
        f'<tspan class="label">{escape(k):<6}</tspan>'
        f'<tspan dx="20" class="value">{escape(v)}</tspan></text>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .panel {{ fill:#0d1117; stroke:#30363d; stroke-width:2; }}
  .bar {{ fill:#161b22; }}
  .dot1 {{ fill:#ff5f56; }} .dot2 {{ fill:#ffbd2e; }} .dot3 {{ fill:#27c93f; }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .title {{ fill:#7ee787; font-size:23px; font-weight:700; }}
  .sub {{ fill:#8b949e; font-size:15px; }}
  .row {{ fill:#c9d1d9; font-size:18px; opacity:0; animation:reveal .45s ease forwards; }}
  .label {{ fill:#58a6ff; font-weight:700; }}
  .value {{ fill:#c9d1d9; }}
  .cursor {{ fill:#7ee787; animation:blink 1s steps(1) infinite; }}
  @keyframes reveal {{ from {{opacity:0; transform:translateY(8px)}} to {{opacity:1; transform:translateY(0)}} }}
  @keyframes blink {{ 50% {{opacity:0}} }}
</style>
<rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/>
<rect class="bar" x="2" y="2" width="{W-4}" height="62" rx="17"/>
<circle class="dot1" cx="32" cy="32" r="8"/><circle class="dot2" cx="58" cy="32" r="8"/><circle class="dot3" cx="84" cy="32" r="8"/>
<text x="120" y="39" class="sub">datachulee@github — whoami</text>
<text x="54" y="112" class="title">$ ./developer_info.sh</text>
{''.join(lines)}
<text x="54" y="480" class="sub">datachulee@github:~$</text>
<rect x="278" y="463" width="12" height="21" class="cursor"/>
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT}")
