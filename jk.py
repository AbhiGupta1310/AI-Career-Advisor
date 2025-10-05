import json

# Read file with multiple objects (even without commas)
with open("combined_output.json", "r") as f:
    text = f.read()

# Fix: insert commas and wrap with brackets if needed
# Split by '}\n{' pattern
objects = text.strip().replace("}\n{", "}|SPLIT|{").split("|SPLIT|")
data = [json.loads(obj) for obj in objects]

# Save as valid JSON array
with open("combined.json", "w") as f:
    json.dump(data, f, indent=2)
