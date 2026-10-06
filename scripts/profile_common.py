"""Shared style and local paths for the generated GitHub profile art."""
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo
import os

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
USERNAME = "DataChuLee"
STATIC = os.environ.get("STATIC") == "1"
BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
DIM = "#7d8590"
GREEN = "#7ee787"
BLUE = "#58a6ff"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def today():
    return datetime.now(ZoneInfo("Asia/Seoul")).date()


def panel(width, height, command, title, description):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        '<defs><linearGradient id="panel-bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#panel-bg)"/>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{BORDER}"/>',
        f'<path d="M0 30 H{width}" stroke="{BORDER}"/>',
        '<circle cx="20" cy="15" r="5" fill="#ff5f56"/>',
        '<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>',
        '<circle cx="52" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{width/2}" y="19" text-anchor="middle" fill="{DIM}" font-size="12">{escape(command)}</text>',
    ]


def label(x, y, value, size=16, color=TEXT, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'


def write_svg(name, parts):
    output = ASSETS / name
    output.write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}")
