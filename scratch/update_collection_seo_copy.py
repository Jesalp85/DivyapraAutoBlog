import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
collection_id = 479914066134
ctx = ssl.create_default_context()

seo_html_body = """
<h2>Buy Authentic Gujarati Pickles Online Direct from Saurashtra</h2>
<p>
  Welcome to <strong>DivyaPrabha Foods</strong>, home of Baa’s authentic 45-year family heritage recipes. If you are looking to <strong>buy Gujarati pickles online</strong>, our handcrafted achaar collection brings you the true culinary taste of Saurashtra and Kathiyawad. Every jar of our Gujarati pickles is made with 100% natural ingredients, farm-fresh Rajapuri raw mangoes, wild seasonal Gunda (glueberries), pure wood-pressed yellow mustard oil (Kachi Ghani), pink rock salt (Sendha Namak), and traditional hand-ground spices.
</p>

<h2>Why DivyaPrabha Homemade Gujarati Pickles Stand Out</h2>
<p>
  Unlike commercial store-bought pickles loaded with artificial vinegar, chemical preservative sodium benzoate, and cheap palm oil, DivyaPrabha Food pickles follow ancient sun-curing traditions:
</p>
<ul>
  <li><strong>8-Hour Rooftop Solar Sun-Drying:</strong> Raw mangoes and spices are cured in natural solar heat to eliminate fruit moisture without high-heat processing.</li>
  <li><strong>100% Wood-Pressed Yellow Mustard Oil:</strong> Submerged in pure cold-pressed yellow mustard oil to naturally preserve crunchiness and prevent mold for 12+ months.</li>
  <li><strong>Refined Sugar-Free Sweet Achar:</strong> Our famous Gor Keri and Chhundo sweet pickles use 100% organic jaggery instead of white refined sugar.</li>
  <li><strong>Zero Artificial Chemicals:</strong> 100% free from synthetic food colors, palm oil, or chemical acidity regulators.</li>
</ul>

<h2>Explore Our Signature Gujarati Achaar Collection</h2>
<p>
  Discover our 7 iconic handcrafted varieties available for nationwide express delivery:
</p>
<ol>
  <li><strong>Gor Keri (Jaggery Mango Pickle):</strong> Sweet & tangy Rajapuri mango cubes infused with organic jaggery, cinnamon, and Kashmiri red chilli.</li>
  <li><strong>Chhundo (Sun-Cured Shredded Mango Relish):</strong> Traditional shredded raw mango relish slow-caramelized under Saurashtra solar heat with roasted cumin.</li>
  <li><strong>Gunda Keri (Stuffed Lasode Glueberry Achar):</strong> Seasonal wild glueberries stuffed with shredded raw mango and yellow mustard Kuria.</li>
  <li><strong>Methia Keri (Chana Keri Methi Achar):</strong> Protein-packed achaar with sprouted chickpeas, fenugreek seeds, and sour raw mango.</li>
  <li><strong>Katka Keri & Traditional Aam Ka Achar:</strong> Crunchy bite-sized cut mango cubes cured in mustard oil and single-origin Asafoetida (Hing).</li>
</ol>
"""

payload = {
    "custom_collection": {
        "id": collection_id,
        "body_html": seo_html_body
    }
}

url = f"{shop_url}/admin/api/2024-04/custom_collections/{collection_id}.json"
data_bytes = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data_bytes, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
}, method="PUT")

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        res = json.loads(resp.read().decode())
        print("✅ Custom Collection Description Updated Successfully!")
        print("Collection Title:", res.get("custom_collection", {}).get("title"))
except Exception as e:
    print("❌ Custom Collection Update Error:", e)

    # Fallback to Smart Collection if custom collection returns 404
    url_smart = f"{shop_url}/admin/api/2024-04/smart_collections/{collection_id}.json"
    payload_smart = {
        "smart_collection": {
            "id": collection_id,
            "body_html": seo_html_body
        }
    }
    data_smart = json.dumps(payload_smart).encode("utf-8")
    req_smart = urllib.request.Request(url_smart, data=data_smart, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }, method="PUT")

    try:
        with urllib.request.urlopen(req_smart, context=ctx) as resp:
            res_smart = json.loads(resp.read().decode())
            print("✅ Smart Collection Description Updated Successfully!")
            print("Collection Title:", res_smart.get("smart_collection", {}).get("title"))
    except Exception as e2:
        print("❌ Smart Collection Update Error:", e2)
