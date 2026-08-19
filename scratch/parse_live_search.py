import urllib.request
import re

url = 'https://divyaprabhafoods.com/search?type=product&q=Mango+Pickle'
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

print("Search HTML Length:", len(html))

# Let's check if the raw tags are still present under ccp-tags
# Raw tag 'aam-ka-achaar'
print("Contains 'aam-ka-achaar':", 'aam-ka-achaar' in html)
# Let's extract blocks with class ccp-tags
tags_blocks = re.findall(r'<div class="ccp-tags"[^>]*>(.*?)</div>', html, re.DOTALL)
for i, block in enumerate(tags_blocks):
    print(f"Product Card {i+1} Badges:")
    # print spans inside
    spans = re.findall(r'<span class="ccp-tag">(.*?)</span>', block)
    print(spans)
