"""PRML booking → seaux9.art auto-sync.

When a SEAUX9 booking is confirmed through the PRML Records pipeline
(/prml-booking), drop a JSON file into 16_CLAUDE_OPS/seaux9-bookings/
(or pass a path directly) and run this script. The event lands on
seaux9.art automatically — including livestream ticketing if flagged.

Booking JSON shape:
{
  "title": "Private Show — The Venue",
  "date": "2026-10-04",
  "time": "8:00 PM",
  "venue": "The Venue",
  "city": "Atlanta, GA",
  "info": "One-liner for fans",
  "public": true,              // false = don't publish on the site
  "livestream": true,          // true = shows LIVESTREAM badge
  "ticket_url": "https://buy.stripe.com/..."   // optional per-event stream ticket
}

Usage:
  python scripts/booking-sync.py path/to/booking.json      # single file
  python scripts/booking-sync.py --scan                    # process queue dir
"""
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_JSON = ROOT / "content" / "site.json"
QUEUE = ROOT.parent / "16_CLAUDE_OPS" / "seaux9-bookings"
DONE = QUEUE / "processed"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def display_date(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b %d · %Y").replace(" 0", " ").upper()


def apply_booking(path: Path) -> bool:
    b = json.loads(path.read_text(encoding="utf-8"))
    if not b.get("public", True):
        print(f"skipped (private): {path.name}")
        return False
    data = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    entry = {
        "id": slugify(f"{b['title']}-{b['date']}"),
        "title": b["title"],
        "date": b["date"],
        "displayDate": display_date(b["date"]),
        "time": b.get("time", "TBA"),
        "venue": b.get("venue", "TBA"),
        "city": b.get("city", "Atlanta, GA"),
        "info": b.get("info", ""),
        "cta": "Stream ticket" if b.get("livestream") and b.get("ticket_url") else "RSVP",
        "link": b.get("ticket_url") or data.get("mailing", {}).get("url", "#connect"),
        "livestream": bool(b.get("livestream")),
    }
    data["events"] = [e for e in data["events"] if e["id"] != entry["id"]] + [entry]
    SITE_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)
    print(f"event synced: {entry['id']} ({entry['displayDate']})"
          + (" [LIVESTREAM]" if entry["livestream"] else ""))
    return True


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] != "--scan":
        apply_booking(Path(sys.argv[1]))
        return
    QUEUE.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(exist_ok=True)
    pending = sorted(QUEUE.glob("*.json"))
    if not pending:
        print(f"queue empty: {QUEUE}")
        return
    for f in pending:
        try:
            apply_booking(f)
            f.rename(DONE / f.name)
        except Exception as e:  # keep the queue moving; bad file stays put
            print(f"ERROR {f.name}: {e}")


if __name__ == "__main__":
    main()
