import json

with open('/Users/apple/Documents/Shopify Theme VS code/DivyaPrabha Food/templates/index.json', 'r') as f:
    lines = f.readlines()

# Strip any comment lines at the start (Shopify CLI might add /* ... */)
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

print("ORDER:")
print(data.get('order', []))

print("\nSECTIONS:")
for section_id, section in data.get('sections', {}).items():
    print(f"ID: {section_id}, Type: {section.get('type')}, Settings: {list(section.get('settings', {}).keys())}")
    if section.get('type') == 'dp-why-choose-us':
        print("  -> FOUND dp-why-choose-us settings:", section.get('settings'))
