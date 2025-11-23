import json

with open("data/shl_individual_assessments.json", "r", encoding='utf-8') as f:
    assessments = json.load(f)

# Count missing descriptions
no_desc = sum(1 for a in assessments if "unavailable" in a.get("description", "").lower())
print(f"Assessments with poor descriptions: {no_desc}/{len(assessments)}")

# Sample some assessments
print("\nSample Assessment:")
print(json.dumps(assessments[0], indent=2))
