"""seaux9.art build step.

1. Injects the traced logo paths from assets/seaux9-logo.svg into the
   <symbol id="s9-logo"> block in index.html (idempotent — safe to re-run).
2. Regenerates content/site.data.js from content/site.json so the site
   renders when opened straight from disk (file://) as well as when hosted.

Run after ANY edit to content/site.json:  python scripts/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
LOGO = ROOT / "assets" / "seaux9-logo.svg"
SITE_JSON = ROOT / "content" / "site.json"
SITE_DATA = ROOT / "content" / "site.data.js"


def inject_logo() -> None:
    svg = LOGO.read_text(encoding="utf-8")
    paths = "".join(re.findall(r"<path[^>]*/?>(?:</path>)?", svg))
    if not paths:
        raise SystemExit("No <path> elements found in logo SVG")
    html = INDEX.read_text(encoding="utf-8")
    new_html, n = re.subn(
        r'(<symbol id="s9-logo"[^>]*>).*?(</symbol>)',
        lambda m: m.group(1) + paths + m.group(2),
        html,
        flags=re.DOTALL,
    )
    if n != 1:
        raise SystemExit("Logo symbol block not found in index.html")
    INDEX.write_text(new_html, encoding="utf-8")
    print(f"logo: {len(paths) // 1024} KB of path data injected into index.html")


def embed_content() -> None:
    data = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    js = "// AUTO-GENERATED from site.json — edit site.json, then run scripts/build.py\n"
    js += "window.SEAUX9_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    SITE_DATA.write_text(js, encoding="utf-8")
    print(f"content: site.data.js regenerated ({len(data['posts'])} posts, "
          f"{len(data['events'])} events, {len(data['releases'])} releases)")


def gen_ics() -> None:
    """Generate a subscribable iCal feed (events.ics) from site.json events.

    Fans subscribe once (webcal://seaux9.art/events.ics) and every deploy
    updates their calendar automatically.
    """
    import re as _re
    from datetime import datetime, timedelta

    data = json.loads(SITE_JSON.read_text(encoding="utf-8"))

    def parse_time(t: str):
        m = _re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", t.strip(), _re.I)
        if not m:
            return None
        h, mi = int(m.group(1)) % 12, int(m.group(2))
        if m.group(3).upper() == "PM":
            h += 12
        return h, mi

    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//SEAUX9//seaux9.art//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:SEAUX9 Events", "X-WR-TIMEZONE:America/New_York",
        "X-WR-CALDESC:Every SEAUX9 show and pull-up. seaux9.art",
    ]
    for e in data.get("events", []):
        parts = [p.strip() for p in e.get("time", "").replace("–", "-").split("-")]
        start = parse_time(parts[0]) if parts and parts[0] else None
        end = parse_time(parts[1]) if len(parts) > 1 else None
        d0 = datetime.strptime(e["date"], "%Y-%m-%d")
        if start:
            dt_start = d0.replace(hour=start[0], minute=start[1])
            dt_end = d0.replace(hour=end[0], minute=end[1]) if end else dt_start + timedelta(hours=3)
            fmt = "%Y%m%dT%H%M%S"
            dt_lines = [
                f"DTSTART;TZID=America/New_York:{dt_start.strftime(fmt)}",
                f"DTEND;TZID=America/New_York:{dt_end.strftime(fmt)}",
            ]
        else:  # all-day fallback
            dt_lines = [f"DTSTART;VALUE=DATE:{d0.strftime('%Y%m%d')}"]
        desc = e.get("info", "").replace(",", r"\,")
        loc = f"{e.get('venue', '')}, {e.get('city', '')}".replace(",", r"\,")
        summary = e["title"].replace(",", r"\,")
        lines += ["BEGIN:VEVENT", f"UID:{e['id']}@seaux9.art",
                  f"DTSTAMP:{d0.strftime('%Y%m%dT000000Z')}", *dt_lines,
                  f"SUMMARY:SEAUX9 — {summary}", f"DESCRIPTION:{desc}",
                  f"LOCATION:{loc}", "URL:https://seaux9.art/#events", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    (ROOT / "events.ics").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    print(f"calendar: events.ics regenerated ({len(data.get('events', []))} events)")


if __name__ == "__main__":
    inject_logo()
    embed_content()
    gen_ics()
    print("build complete — open index.html or deploy the folder")
