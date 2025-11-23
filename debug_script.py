import json
import pandas as pd

# Load scraped data
with open("data/shl_individual_assessments.json", "r", encoding='utf-8') as f:
    scraped = json.load(f)

scraped_urls = set([assess['url'].lower().strip('/') for assess in scraped])

# Load ground truth
train_df = pd.read_csv("data/Gen_AI_Dataset_Train.csv", encoding='cp1252')
ground_truth_urls = set(train_df['Assessment_url'].str.lower().str.strip('/'))

# Check overlap
overlap = scraped_urls.intersection(ground_truth_urls)

print(f"Scraped assessments: {len(scraped_urls)}")
print(f"Ground truth URLs: {len(ground_truth_urls)}")
print(f"Overlap: {len(overlap)}")
print(f"Overlap %: {len(overlap)/len(ground_truth_urls)*100:.2f}%")

# Show mismatches
missing = ground_truth_urls - scraped_urls
print(f"\n❌ Missing from scraped data ({len(missing)}):")
for url in list(missing)[:10]:
    print(f"  - {url}")
