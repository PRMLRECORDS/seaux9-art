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


if __name__ == "__main__":
    inject_logo()
    embed_content()
    print("build complete — open index.html or deploy the folder")
