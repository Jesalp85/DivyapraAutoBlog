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

verified_keywords = [
    # 🥭 Raw Mango Achar
    {"keyword": "Buy Mango Pickle Online", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Traditional Gujarati Keri Achar", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Rajapuri Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Gujarati Baa nu Athanu", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Homemade Keri nu Athanu", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Saurashtra Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Raw Mango Achar Online", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Mustard Oil Keri Achar", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Preservative Free Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Kathiyawadi Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Authentic Keri Pickle India", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Sun Cured Mango Achar", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Kachi Ghani Mustard Oil Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Grandma Style Mango Pickle", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Pure Homemade Aam Ka Achar", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Spicy Keri Athanu", "link": "/products/mango-pickle-traditional-keri-achar-gujarati", "cat": "mango"},
    {"keyword": "Katka Keri Cut Mango", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Gujarati Cut Mango Pickle", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Katka Keri nu Athanu", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Crunchy Raw Mango Achar", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},

    # 🍯 Sweet & Jaggery
    {"keyword": "Buy Gor Keri Pickle Online", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Jaggery Sweet Mango Pickle", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gujarati Gorkeri Achar", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Organic Jaggery Mango Pickle", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sweet & Tangy Keri Athanu", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gud Ka Achar Online", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Traditional Gorkeri Recipe", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gujarati Sweet Mango Pickle", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gor Keri Athanu Buy Online", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Saurashtra Gor Keri", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Buy Gujarati Chhundo Online", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sun Cured Mango Chhundo", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Shredded Mango Sweet Relish", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sweet Chunda Pickle Online", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gujarati Chhundo Athanu", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Traditional Chunda Recipe", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sweet Grated Mango Achar", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Buy Sweet Mango Pickle Online", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Meethi Keri Achar Online", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Sweet Homemade Mango Pickle", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},

    # 🫙 Gujarati Heritage
    {"keyword": "Buy Gunda Keri Pickle Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Gujarati Lasode Ka Achar", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Stuffed Gunda Pickle Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Kathiyawadi Gunda Keri Athanu", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Gunda Mango Pickle Buy Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Lasora Pickle Online India", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Buy Chana Keri Methi Pickle", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Sprouted Chickpea Mango Achar", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Gujarati Methia Keri Athanu", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Methi Mango Pickle Online", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Fenugreek Raw Mango Pickle", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Chana Keri Achar Online", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},

    # 📍 Regional Buyers
    {"keyword": "Buy Pickles Online Mumbai", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Delhi", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Bangalore", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Ahmedabad", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Pune", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Hyderabad", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Surat", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Vadodara", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Rajkot", "link": "/collections/pickles", "cat": "regional"},

    # 🛒 All Collections & General
    {"keyword": "Shop All Pickles & Spices", "link": "/collections/all-products", "cat": "general"},
    {"keyword": "Best Indian Pickles Online", "link": "/collections/best-seller", "cat": "general"},
    {"keyword": "Pure Homemade Achar Store", "link": "/collections/homemade-pickles", "cat": "general"},
    {"keyword": "Organic Pickles Buy Online", "link": "/collections/organic-pickles", "cat": "general"},
    {"keyword": "Zero Preservatives Achar", "link": "/collections/organic-pickles", "cat": "general"},
    {"keyword": "Traditional Gujarati Foods", "link": "/collections/traditional-gujarati-foods", "cat": "gujarati"},
    {"keyword": "Buy Gujarati Achar Masala", "link": "/collections/all-masala", "cat": "spices"},
    {"keyword": "Pure Organic Spices Online", "link": "/collections/all-spices", "cat": "spices"},
    {"keyword": "Buy Pickle Combos Online", "link": "/collections/all-combo-offers", "cat": "general"},
    {"keyword": "Tangy & Spicy Gujarati Pickles", "link": "/collections/tangyspicy-pickle", "cat": "mango"},
    {"keyword": "Sweet & Tangy Pickles", "link": "/collections/sweet-tangy", "cat": "sweet"}
]

new_blocks = {}
block_order = []
for idx, kw in enumerate(verified_keywords, 1):
    tag_id = f"tag_{idx}"
    new_blocks[tag_id] = {
        "type": "keyword_link",
        "settings": {
            "keyword": kw["keyword"],
            "link": kw["link"],
            "category": kw["cat"]
        }
    }
    block_order.append(tag_id)

data["sections"]["dp_popular_searches"]["blocks"] = new_blocks
data["sections"]["dp_popular_searches"]["block_order"] = block_order
data["sections"]["dp_popular_searches"]["settings"]["title"] = "POPULAR SEARCHES"

new_json_str = comment_header + json.dumps(data, indent=2)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_json_str)

print(f"SUCCESS! Created {len(new_blocks)} verified keyword blocks in index.json!")
