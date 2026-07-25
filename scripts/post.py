"""seaux9.art posting CLI — publish to the site (and later, everywhere).

Add a journal post:
    python scripts/post.py post "Title here" "Body text here" --tags news,9squad

Add an event:
    python scripts/post.py event "Show Title" 2026-09-01 --time "7:00 PM" \
        --venue "Venue Name" --city "Atlanta, GA" --info "One-liner" --cta RSVP

Then commit + deploy (or pass --push to do it automatically if this folder
becomes a git repo wired to the host, same flow as prmlrecords.com).

Cross-posting: --crosspost sends the post to a self-hosted Postiz instance
(https://github.com/gitroomhq/postiz-app) so the same words land on
TikTok/IG/FB/YouTube/X at once. Set POSTIZ_URL + POSTIZ_API_KEY env vars.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_JSON = ROOT / "content" / "site.json"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def load() -> dict:
    return json.loads(SITE_JSON.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    SITE_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)


def add_post(args) -> dict:
    data = load()
    entry = {
        "id": slugify(args.title),
        "date": args.date or dt.date.today().isoformat(),
        "title": args.title,
        "body": args.body,
        "tags": [t.strip() for t in (args.tags or "news").split(",") if t.strip()],
    }
    data["posts"] = [p for p in data["posts"] if p["id"] != entry["id"]] + [entry]
    save(data)
    print(f"posted: {entry['id']} ({entry['date']})")
    return entry


def add_event(args) -> dict:
    data = load()
    d = dt.date.fromisoformat(args.date)
    entry = {
        "id": slugify(args.title),
        "title": args.title,
        "date": args.date,
        "displayDate": d.strftime("%b %-d · %Y").upper() if os.name != "nt"
        else d.strftime("%b %d · %Y").replace(" 0", " ").upper(),
        "time": args.time,
        "venue": args.venue,
        "city": args.city,
        "info": args.info,
        "cta": args.cta,
        "link": args.link,
    }
    data["events"] = [e for e in data["events"] if e["id"] != entry["id"]] + [entry]
    save(data)
    print(f"event added: {entry['id']} ({entry['displayDate']})")
    return entry


def git_push(message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print("pushed — host will redeploy")


def crosspost(entry: dict) -> None:
    """Send the post to a Postiz instance for multi-platform publishing."""
    url = os.environ.get("POSTIZ_URL")
    key = os.environ.get("POSTIZ_API_KEY")
    if not url or not key:
        print("crosspost skipped: set POSTIZ_URL and POSTIZ_API_KEY "
              "(see https://docs.postiz.com/public-api)")
        return
    payload = {
        "type": "now",
        "posts": [{
            "content": [{"content": f"{entry['title']}\n\n{entry['body']}\n\nseaux9.art"}],
            # integration ids are configured inside Postiz; empty = all defaults
        }],
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/api/public/v1/posts",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"crossposted via Postiz: HTTP {r.status}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish to seaux9.art")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("post", help="add a journal post")
    p.add_argument("title")
    p.add_argument("body")
    p.add_argument("--tags", default="news")
    p.add_argument("--date", default=None, help="YYYY-MM-DD (default today)")
    p.add_argument("--push", action="store_true")
    p.add_argument("--crosspost", action="store_true")

    e = sub.add_parser("event", help="add an event")
    e.add_argument("title")
    e.add_argument("date", help="YYYY-MM-DD")
    e.add_argument("--time", default="TBA")
    e.add_argument("--venue", default="TBA")
    e.add_argument("--city", default="Atlanta, GA")
    e.add_argument("--info", default="")
    e.add_argument("--cta", default="RSVP")
    e.add_argument("--link", default="#connect")
    e.add_argument("--push", action="store_true")
    e.add_argument("--crosspost", action="store_true")

    args = ap.parse_args()
    entry = add_post(args) if args.cmd == "post" else add_event(args)
    if args.crosspost:
        crosspost(entry)
    if args.push:
        git_push(f"content: {args.cmd} — {entry['id']}")


if __name__ == "__main__":
    main()
