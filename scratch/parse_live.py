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

# Search for the stylesheet block of Why Choose Us
# It usually contains .dp-wcu-section
matches = re.findall(r'(\.dp-wcu-section\s*\{[^}]+\})', html)
for m in matches:
    print("Found .dp-wcu-section match:")
    print(m)

matches_heading = re.findall(r'(\.dp-wcu__heading\s*\{[^}]+\})', html)
for m in matches_heading:
    print("Found .dp-wcu__heading match:")
    print(m)

# Let's search for "Zero Preservatives" in HTML to see if it's there
print("Zero Preservatives in HTML:", "Zero Preservatives" in html)
# Let's also check if "aam-ka-achaar" is in the HTML (if we search or not)
print("aam-ka-achaar in HTML:", "aam-ka-achaar" in html)
