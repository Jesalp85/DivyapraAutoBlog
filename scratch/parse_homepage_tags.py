import urllib.request
import re

url = 'https://divyaprabhafoods.com/?nocache=99999'
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
except Exception as e:
    print("Error fetching:", e)
    html = ""

print("HTML Length:", len(html))

# Extract all blocks with class cpg-tags
tags_blocks = re.findall(r'<div class="cpg-tags"[^>]*>(.*?)</div>', html, re.DOTALL)
print("Number of cpg-tags blocks found:", len(tags_blocks))
for i, block in enumerate(tags_blocks[:5]):
    print(f"Product {i+1} Badges:")
    spans = re.findall(r'<span class="cpg-tag">(.*?)</span>', block)
    print(spans)
