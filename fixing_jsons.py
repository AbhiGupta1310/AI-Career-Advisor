import json

# # Load your JSON (example with file)
# with open("json/businees_intelligence_developers.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# # Check if the first element is a list (extra nesting)
# if isinstance(data[0], list):
#     data = data[0]  # flatten it

# # Now 'data' has the same structure as your first JSON
# with open("json/businees_intelligence_developerss.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=2, ensure_ascii=False)


# Read file with multiple objects (even without commas)
with open("json/combined_output.json", "r") as f:
    text = f.read()

# Fix: insert commas and wrap with brackets if needed
# Split by '}\n{' pattern
objects = text.strip().replace("}\n{", "}|SPLIT|{").split("|SPLIT|")
data = [json.loads(obj) for obj in objects]

# Save as valid JSON array
with open("combined.json", "w") as f:
    json.dump(data, f, indent=2)
