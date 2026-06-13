#!/usr/bin/env python3
"""
Fetch open PRs authored by coder-xander across all GitHub repos,
then update the README section between LATEST_PRS markers.

Requires GH_PAT env var (a PAT with public_repo / repo scope).
"""
import json, os, re, sys, urllib.request

TOKEN = os.environ.get("GH_PAT")
if not TOKEN:
    print("❌ GH_PAT env var not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "profile-pr-updater",
}


def api(path: str) -> dict:
    req = urllib.request.Request(f"https://api.github.com{path}", headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def pr_icon(pr: dict) -> str:
    if pr.get("pull_request", {}).get("merged_at"):
        return "✅"
    return "🟢"


# ── Fetch open PRs authored by coder-xander ──────────────────────
search = api(
    "/search/issues?"
    "q=author:coder-xander+type:pr+state:open&"
    "per_page=10&sort=created&order=desc"
)
items: list = search.get("items", [])
total: int = search.get("total_count", 0)

# Build table rows
rows: list[str] = []
for pr in items:
    repo = pr["repository_url"].split("/repos/")[1]
    num = pr["number"]
    title = pr["title"][:56] + ("…" if len(pr["title"]) > 56 else "")
    created = pr["created_at"][:10]
    icon = pr_icon(pr)
    rows.append(
        f"| [{repo}](https://github.com/{repo}) | "
        f"[#{num}]({pr['html_url']}) | "
        f"{icon} {title} | {created} |"
    )

pr_block = "\n".join(rows) if rows else (
    "| No open PRs at the moment. | | | |"
)

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

| Project | # | Title | Created |
|---------|---|-------|---------|
{pr_block}

{marker_end}"""

if marker_start in content and marker_end in content:
    start = content.index(marker_start)
    end = content.index(marker_end) + len(marker_end)
    content = content[:start] + new_section + content[end:]
else:
    # Append before the final signature block
    content += f"\n\n---\n\n{new_section}\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ README updated — {total} open PR(s) found, {len(rows)} displayed")
