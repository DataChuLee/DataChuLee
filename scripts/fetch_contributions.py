from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup

USERNAME = "DataChuLee"
OUT = Path("assets/contributions.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

url = f"https://github.com/users/{USERNAME}/contributions"
r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")
days = []
for node in soup.select("[data-date]"):
    date = node.get("data-date")
    level = node.get("data-level")
    count = node.get("data-count")
    if not date or level is None:
        continue
    days.append({
        "date": date,
        "level": int(level),
        "count": int(count) if str(count).isdigit() else 0,
    })

dedup = {d["date"]: d for d in days}
data = list(sorted(dedup.values(), key=lambda x: x["date"]))
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {OUT} ({len(data)} days)")
