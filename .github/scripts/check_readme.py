"""Verify README.md structure:
1. PR automation markers preserved
2. HTML tag balance
3. img tags have src and no self-closing
4. every assets/*.svg referenced exists and is well-formed XML
5. no raw '#' left in URLs that should be %23
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
path = os.path.join(BASE, "README.md")
with open(path, encoding="utf-8") as f:
    content = f.read()

errors = []

# 1. PR markers
if "<!-- LATEST_PRS_START -->" not in content:
    errors.append("missing LATEST_PRS_START marker")
if "<!-- LATEST_PRS_END -->" not in content:
    errors.append("missing LATEST_PRS_END marker")
start = content.index("<!-- LATEST_PRS_START -->")
end = content.index("<!-- LATEST_PRS_END -->")
if end < start:
    errors.append("PR markers out of order")

# 2. HTML tag balance
for tag in ["div", "table", "tr", "picture"]:
    opens = len(re.findall(rf"<{tag}[\s>]", content))
    closes = len(re.findall(rf"</{tag}>", content))
    if opens != closes:
        errors.append(f"tag <{tag}> unbalanced: open={opens} close={closes}")

# 3. img tags
imgs = re.findall(r"<img\b[^>]*>", content)
for img in imgs:
    if "src=" not in img:
        errors.append(f"img without src: {img[:80]}")
    if img.rstrip().endswith("/>"):
        errors.append(f"img should not be self-closing: {img[:80]}")
    if "data:" in img:
        errors.append(f"data URI should be replaced by assets/ path: {img[:80]}")

# 4. assets referenced exist & are well-formed XML
asset_refs = re.findall(r'src="(assets/[^"]+)"', content)
for ref in asset_refs:
    full = os.path.join(BASE, ref)
    if not os.path.isfile(full):
        errors.append(f"missing asset: {ref}")
        continue
    try:
        ET.parse(full)
    except ET.ParseError as e:
        errors.append(f"invalid SVG XML in {ref}: {e}")

# 5. raw '#' in any URL src (should be %23)
for img in imgs:
    if 'src="https://' in img and "#" in img:
        errors.append(f"raw '#' in URL: {img[:100]}")

print(f"OK: {len(imgs)} img tags, {len(asset_refs)} asset references")
if errors:
    print("ERRORS:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("ALL STRUCTURE CHECKS PASSED")
