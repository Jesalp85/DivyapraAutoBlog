import json

filepath = "templates/index.json"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

comment_header = ""
if content.startswith("/*"):
    idx = content.find("*/")
    if idx != -1:
        comment_header = content[:idx+2] + "\n"
        json_str = content[idx+2:].strip()
    else:
        json_str = content
else:
    json_str = content

data = json.loads(json_str)

# Short, concise keywords linking to products, blog guides, blog tags, and collections
new_blocks = {
    "tag_1": { "type": "keyword_link", "settings": { "keyword": "Rajapuri Raw Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati" } },
    "tag_2": { "type": "keyword_link", "settings": { "keyword": "Gor Keri Jaggery Mango", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati" } },
    "tag_3": { "type": "keyword_link", "settings": { "keyword": "Sun-Cured Shredded Chhundo", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati" } },
    "tag_4": { "type": "keyword_link", "settings": { "keyword": "Stuffed Gunda Keri Achar", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati" } },
    "tag_5": { "type": "keyword_link", "settings": { "keyword": "Katka Keri Cut Mango", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar" } },
    "tag_6": { "type": "keyword_link", "settings": { "keyword": "Meethi Keri Sweet Mango", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade" } },
    "tag_7": { "type": "keyword_link", "settings": { "keyword": "Chana Keri Methia Achar", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar" } },
    "tag_8": { "type": "keyword_link", "settings": { "keyword": "Gujarati Achar Masala Mix", "link": "/products/aachar-masala-ready-pickle-mix-gujarati-methia-sambhar" } },
    "tag_9": { "type": "keyword_link", "settings": { "keyword": "Pure Organic Hing Powder", "link": "/products/hing-powder-pure-asafoetida-gold-quality-organic" } },

    "tag_10": { "type": "keyword_link", "settings": { "keyword": "Gunda Keri Recipe Guide", "link": "/blogs/news/gunda-keri-pickle-online-gujarati-lasode-ka-achar-guide" } },
    "tag_11": { "type": "keyword_link", "settings": { "keyword": "Sun-Cured Chhundo Guide", "link": "/blogs/news/gujarati-chhundo-pickle-online-authentic-sun-cured-mango" } },
    "tag_12": { "type": "keyword_link", "settings": { "keyword": "Chana Keri Methi Benefits", "link": "/blogs/news/chana-keri-methi-achar-sprouted-chickpea-mango-pickle" } },
    "tag_13": { "type": "keyword_link", "settings": { "keyword": "Katka Keri Cut Mango Guide", "link": "/blogs/news/katka-keri-pickle-gujarati-traditional-cut-mango-achar" } },
    "tag_14": { "type": "keyword_link", "settings": { "keyword": "Organic Jaggery Gor Keri Secrets", "link": "/blogs/news/jaggery-gor-keri-achar-traditional-sweet-mango-pickle" } },
    "tag_15": { "type": "keyword_link", "settings": { "keyword": "Spot Fake vs Pure Achar", "link": "/blogs/news/how-to-spot-fake-vs-pure-homemade-pickles" } },
    "tag_16": { "type": "keyword_link", "settings": { "keyword": "Pickle & Meal Pairing Guide", "link": "/blogs/news/the-ultimate-indian-pickle-meal-pairing-guide" } },
    "tag_17": { "type": "keyword_link", "settings": { "keyword": "Cold-Pressed Mustard Oil", "link": "/blogs/news/why-cold-pressed-kachi-ghani-mustard-oil-is-mandatory" } },

    "tag_18": { "type": "keyword_link", "settings": { "keyword": "Heritage Recipes", "link": "/blogs/news/tagged/heritage-recipes" } },
    "tag_19": { "type": "keyword_link", "settings": { "keyword": "Health & Spices", "link": "/blogs/news/tagged/health-spices" } },
    "tag_20": { "type": "keyword_link", "settings": { "keyword": "Buying Guides", "link": "/blogs/news/tagged/buying-guides" } },
    "tag_21": { "type": "keyword_link", "settings": { "keyword": "Pickle Pairings", "link": "/blogs/news/tagged/pickle-pairings" } },
    "tag_22": { "type": "keyword_link", "settings": { "keyword": "Artisanal Craft", "link": "/blogs/news/tagged/artisanal-craft" } },

    "tag_23": { "type": "keyword_link", "settings": { "keyword": "All Homemade Pickles", "link": "/collections/all" } },
    "tag_24": { "type": "keyword_link", "settings": { "keyword": "Preservative-Free Achar", "link": "/collections/all" } },
    "tag_25": { "type": "keyword_link", "settings": { "keyword": "Organic Jaggery Pickles", "link": "/collections/all" } },
    "tag_26": { "type": "keyword_link", "settings": { "keyword": "Saurashtra Baa nu Athanu", "link": "/collections/all" } }
}

block_order = list(new_blocks.keys())

data["sections"]["dp_popular_searches"]["blocks"] = new_blocks
data["sections"]["dp_popular_searches"]["block_order"] = block_order
data["sections"]["dp_popular_searches"]["settings"]["title"] = "POPULAR SEARCHES"
data["sections"]["dp_popular_searches"]["settings"]["style_preset"] = "pills"

new_json_str = comment_header + json.dumps(data, indent=2)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_json_str)

print("SUCCESS! Updated templates/index.json with short, clean keywords for all products, collections, and blog guides.")
