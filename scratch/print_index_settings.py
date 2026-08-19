import json

with open('/Users/apple/Documents/Shopify Theme VS code/DivyaPrabha Food/templates/index.json', 'r') as f:
    lines = f.readlines()

json_str = ""
in_comment = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith('/*'):
        in_comment = True
        continue
    if in_comment:
        if stripped.endswith('*/'):
            in_comment = False
        continue
    json_str += line

data = json.loads(json_str)
print(data['sections']['custom_product_grid_TBrBP4']['settings'])
