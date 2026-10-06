"""Convert the current GitHub avatar into a monochrome, self-typing portrait.

Run normally to download the current avatar, or pass a local photo for previews.
Only this script needs Pillow. The original photo is never committed.
"""
from html import escape
from io import BytesIO
from pathlib import Path
import sys
from urllib.request import Request, urlopen

from PIL import Image, ImageEnhance, ImageOps
from profile_common import ASSETS, BG, BORDER, DIM, STATIC, TEXT, USERNAME, label, panel, write_svg


def make_portrait(image):
    columns, rows = 180, 96
    image = ImageOps.fit(image.convert("RGB"), (800, 800), method=Image.Resampling.LANCZOS)
    image = ImageOps.autocontrast(image.convert("L"), cutoff=0.4)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = image.resize((columns, rows), Image.Resampling.LANCZOS)
    ramp = " .`:-=+*cs#%@"
    pixels = list(image.getdata())
    lines = []
    for y in range(rows):
        chars = []
        for p in pixels[y*columns:(y+1)*columns]:
            luminance = (p / 255) ** 1.08
            index = 0 if luminance >= 0.95 else round((1-luminance)*(len(ramp)-1))
            chars.append(ramp[index])
        lines.append("".join(chars))

    width, height = 840, 880
    cell_width, cell_height = 800/columns, 800/rows
    parts = panel(width, height, "datachulee@github: ~$ ./portrait.sh",
                  "DataChuLee's ASCII portrait", "Current GitHub avatar revealed row by row as monochrome ASCII art.")
    duration = 5.8/rows
    for row, line in enumerate(lines):
        top = 43 + row*cell_height
        delay = row*duration
        content = (f'<text xml:space="preserve" x="20" y="{top+cell_height*.8:.3f}" fill="{TEXT}" '
                   f'font-size="{cell_height*.85:.3f}" textLength="800" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>')
        if STATIC:
            parts.append(content)
        else:
            parts.append(f'<clipPath id="row-{row}"><rect x="20" y="{top:.3f}" width="0" height="{cell_height:.3f}">'
                         f'<animate attributeName="width" from="0" to="800" begin="{delay:.4f}s" '
                         f'dur="{duration:.4f}s" fill="freeze"/></rect></clipPath>')
            parts.append(f'<g clip-path="url(#row-{row})">{content}</g>')
            parts.append(f'<rect y="{top:.3f}" width="{cell_width:.3f}" height="{cell_height:.3f}" fill="{TEXT}" opacity="0">'
                         f'<animate attributeName="x" from="20" to="820" begin="{delay:.4f}s" dur="{duration:.4f}s" fill="freeze"/>'
                         f'<set attributeName="opacity" to=".85" begin="{delay:.4f}s"/>'
                         f'<set attributeName="opacity" to="0" begin="{delay+duration:.4f}s"/></rect>')
    parts += [f'<path d="M0 850 H840" stroke="{BORDER}"/>',
              label(20, 870, "datachulee@github:~$ whoami  DataChuLee", 13, DIM)]
    write_svg("ascii-profile.svg", parts)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        photo = Image.open(Path(sys.argv[1]))
    else:
        request = Request(f"https://github.com/{USERNAME}.png?size=800", headers={"User-Agent": "profile-art/1.0"})
        with urlopen(request, timeout=45) as response:
            photo = Image.open(BytesIO(response.read()))
    make_portrait(photo)
