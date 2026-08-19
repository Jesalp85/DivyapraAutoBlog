import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://divyaprabhafoods.com/sitemap.xml"
print("--- FETCHING SITEMAP INDEX ---")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        content = resp.read().decode('utf-8')
        locs = re.findall(r'<loc>(.*?)</loc>', content)
        for l in locs:
            print("Sub-sitemap:", l)
            try:
                sub_req = urllib.request.Request(l, headers=headers)
                with urllib.request.urlopen(sub_req, context=ctx) as sub_resp:
                    sub_content = sub_resp.read().decode('utf-8')
                    urls = re.findall(r'<loc>(.*?)</loc>', sub_content)
                    print(f"  Found {len(urls)} URLs in {l}")
                    for u in urls[:15]:
                        print("   -", u)
            except Exception as e:
                print("  Error reading sub-sitemap:", e)
except Exception as e:
    print("Error:", e)
