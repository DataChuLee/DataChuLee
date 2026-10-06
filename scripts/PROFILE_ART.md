# Animated profile art

The profile consists of three independent SVG images: the contribution calendar,
the current GitHub avatar converted to ASCII, and the activity statistics card.
The layout follows the terminal-style approach described by
[Avi Vashishta](https://www.avivashishta.com/blog/build-animated-github-profile-readme).
The generators here are written for DataChuLee's profile.

## Regenerate

From the repository root:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
python scripts/make_ascii_svg.py
```

The workflow performs these steps daily at 09:15 Asia/Seoul, on relevant pushes,
or through its Run workflow button. Scheduled jobs can run later than their
scheduled time. No personal access token is needed to retrieve public data.
GitHub's built-in Actions token commits the generated files.

The portrait is downloaded from the current GitHub avatar each time. A local
photo can be supplied with `python scripts/make_ascii_svg.py /path/to/photo.png`.
The input photo is not stored in this repository. For a frozen SVG preview,
set `STATIC=1` before running either renderer.

Contribution counts are read from the tooltips in GitHub's public calendar,
with support for older markup containing `data-count`. Missing counts,
incomplete calendars, or inconsistent levels stop the job before overwriting
the previous data. All figures refer to the returned public calendar. Current
streak includes yesterday when today has no contributions yet; month totals
can include a partial month.

The former combined terminal SVG and its generator remain available for
reference; the README and daily workflow now use the three new panels.
