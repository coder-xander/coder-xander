#!/usr/bin/env python3
"""
Fetch open PR count authored by coder-xander across all GitHub repos,
then update the README section between LATEST_PRS markers.

No authentication required — uses public GitHub API (rate: 10 req/min).
"""
import json, sys, urllib.request, urllib.error

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "profile-pr-updater",
}


def api(path: str) -> dict:
    req = urllib.request.Request(f"https://api.github.com{path}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌ API error {e.code}: {e.reason}", file=sys.stderr)
        return {"total_count": 0, "items": []}


# ── Fetch open PR count ─────────────────────────────────────────
search = api(
    "/search/issues?"
    "q=author:coder-xander+type:pr+state:open&"
    "per_page=1"
)
total: int = search.get("total_count", 0)

# ── Read current README ──────────────────────────────────────────
readme_path = "README.md"
with open(readme_path, encoding="utf-8") as f:
    content = f.read()

# ── Replace markers or insert ────────────────────────────────────
marker_start = "<!-- LATEST_PRS_START -->"
marker_end = "<!-- LATEST_PRS_END -->"

new_section = f"""\
{marker_start}

### 📬 Latest Pull Requests

Currently **{total}** open PR(s) authored by [coder-xander](https://github.com/coder-xander).

{marker_end}"""

if marker_start in content and marker_end in content:
    start = content.index(marker_start)
    end = content.index(marker_end) + len(marker_end)
    content = content[:start] + new_section + content[end:]
else:
    content += f"\n\n---\n\n{new_section}\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ README updated — {total} open PR(s)")
