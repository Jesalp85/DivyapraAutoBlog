import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

test_urls = [
    # Products
    "https://divyaprabhafoods.com/products/mango-pickle-traditional-keri-achar-gujarati",
    "https://divyaprabhafoods.com/products/gor-keri-pickle-jaggery-mango-achar-gujarati",
    "https://divyaprabhafoods.com/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati",
    "https://divyaprabhafoods.com/products/gunda-keri-pickle-lasode-ka-achar-gujarati",
    "https://divyaprabhafoods.com/products/katka-keri-pickle-homemade-gujarati-mango-achar",
    "https://divyaprabhafoods.com/products/sweet-mango-pickle-meethi-keri-achar-homemade",
    "https://divyaprabhafoods.com/products/chana-keri-methi-pickle-gujarati-methia-achar",
    "https://divyaprabhafoods.com/products/aachar-masala-ready-pickle-mix-gujarati-methia-sambhar",
    "https://divyaprabhafoods.com/products/hing-powder-pure-asafoetida-gold-quality-organic",
    # Collections
    "https://divyaprabhafoods.com/collections/all"
]

print("--- VERIFYING LIVE STOREFRONT URLS ---")
valid_product_handles = []
for url in test_urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as resp:
            status = resp.getcode()
            final_url = resp.geturl()
            print(f"[{status}] {url}")
            if status == 200 and "404" not in final_url:
                valid_product_handles.append(url.replace("https://divyaprabhafoods.com", ""))
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] ❌ INVALID (404): {url}")
    except Exception as e:
        print(f"Error checking {url}: {e}")

print("\n--- VALID STORE PATHS ---")
for path in valid_product_handles:
    print(path)
