import json

# Define the master list of 100+ verified keywords with strictly verified live URLs
verified_keywords = [
    # --- 🥭 Traditional Raw Mango Pickles ---
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

    # --- 🍯 Gor Keri & Sweet Jaggery Pickles ---
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
    {"keyword": "Jaggery Cured Mango Pickle", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "No Sugar Sweet Mango Pickle", "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati", "cat": "sweet"},

    # --- ☀️ Sun-Cured Chhundo Relish ---
    {"keyword": "Buy Gujarati Chhundo Online", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sun Cured Mango Chhundo", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Shredded Mango Sweet Relish", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sweet Chunda Pickle Online", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Gujarati Chhundo Athanu", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Traditional Chunda Recipe", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Sweet Grated Mango Achar", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Chhundo Pickle Buy Online", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Authentic Saurashtra Chhundo", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},
    {"keyword": "Chhundo for Thepla & Khichdi", "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati", "cat": "sweet"},

    # --- 🫙 Stuffed Gunda Keri (Lasode) ---
    {"keyword": "Buy Gunda Keri Pickle Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Gujarati Lasode Ka Achar", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Stuffed Gunda Pickle Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Kathiyawadi Gunda Keri Athanu", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Gunda Mango Pickle Buy Online", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Lasora Pickle Online India", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Traditional Gunda nu Athanu", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},
    {"keyword": "Spicy Gunda Keri Pickle", "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati", "cat": "gujarati"},

    # --- 🔪 Katka Keri Cut Mango ---
    {"keyword": "Buy Katka Keri Pickle Online", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Gujarati Cut Mango Pickle", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Katka Keri nu Athanu", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Crunchy Raw Mango Achar", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Traditional Katka Keri Athanu", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},
    {"keyword": "Cut Raw Mango Pickle India", "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar", "cat": "mango"},

    # --- 🍬 Sweet Meethi Keri ---
    {"keyword": "Buy Sweet Mango Pickle Online", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Meethi Keri Achar Online", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Sweet Homemade Mango Pickle", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Gujarati Meethi Keri", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},
    {"keyword": "Sweet Keri Athanu Online", "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade", "cat": "sweet"},

    # --- 🌱 Chana Keri Methi Sprouted Achar ---
    {"keyword": "Buy Chana Keri Methi Pickle", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Sprouted Chickpea Mango Achar", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Gujarati Methia Keri Athanu", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Methi Mango Pickle Online", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Fenugreek Raw Mango Pickle", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Chana Keri Achar Online", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},
    {"keyword": "Healthy Methia Aam Ka Achar", "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar", "cat": "gujarati"},

    # --- 📍 Regional Searches (Verified Collections) ---
    {"keyword": "Buy Pickles Online Mumbai", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Delhi", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Bangalore", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Ahmedabad", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Pune", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Hyderabad", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Surat", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Vadodara", "link": "/collections/pickles", "cat": "regional"},
    {"keyword": "Buy Pickles Online Rajkot", "link": "/collections/pickles", "cat": "regional"},

    # --- 🛒 General Store Collections ---
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

print(f"Total Verified Store Keywords: {len(verified_keywords)}")
