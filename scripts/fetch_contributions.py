"""Read real counts from GitHub calendar tooltips, without a personal token."""
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.request import Request, urlopen

from profile_common import ASSETS, USERNAME, today


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = {}
        self.tooltips = {}
        self.active_tip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-date" in attrs and "data-level" in attrs:
            self.cells[attrs.get("id", attrs["data-date"])] = attrs
        if tag == "tool-tip":
            self.active_tip = attrs.get("for")
            if self.active_tip:
                self.tooltips[self.active_tip] = ""

    def handle_data(self, data):
        if self.active_tip:
            self.tooltips[self.active_tip] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.active_tip = None


def parse_days(html, end_date):
    parser = CalendarParser()
    parser.feed(html)
    days = {}
    for cell_id, attrs in parser.cells.items():
        day = date.fromisoformat(attrs["data-date"])
        if day > end_date:
            continue
        level = int(attrs["data-level"])
        text = parser.tooltips.get(cell_id, "").strip()
        raw = attrs.get("data-count", "")
        if raw.isdigit():
            count = int(raw)
        elif re.match(r"No contributions\b", text, flags=re.I):
            count = 0
        else:
            match = re.match(r"([\d,]+) contributions?\b", text, flags=re.I)
            if not match:
                raise ValueError(f"Missing contribution count for {day}; keeping the previous assets.")
            count = int(match[1].replace(",", ""))
        if (count == 0) != (level == 0):
            raise ValueError(f"Inconsistent count/level for {day}")
        days[day.isoformat()] = {"date": day.isoformat(), "level": level, "count": count}
    if len(days) < 350:
        raise ValueError(f"Incomplete calendar ({len(days)} days); keeping the previous assets.")
    ordered = sorted(days.values(), key=lambda item: item["date"])
    for before, after in zip(ordered, ordered[1:]):
        if date.fromisoformat(after["date"]) - date.fromisoformat(before["date"]) != timedelta(days=1):
            raise ValueError("Calendar has missing dates")
    if date.fromisoformat(ordered[-1]["date"]) < end_date - timedelta(days=1):
        raise ValueError("Calendar is stale")
    return ordered


if __name__ == "__main__":
    if len(sys.argv) > 1:
        html = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        request = Request(f"https://github.com/users/{USERNAME}/contributions",
                          headers={"User-Agent": "profile-art/1.0"})
        with urlopen(request, timeout=45) as response:
            html = response.read().decode("utf-8")
    days = parse_days(html, today())
    output = ASSETS / "contributions.json"
    output.write_text(json.dumps(days, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days, {sum(day['count'] for day in days):,} contributions")
