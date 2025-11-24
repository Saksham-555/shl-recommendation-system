"""
Generate predictions for unlabeled test set
Format: CSV with Query and Assessment_url columns
"""

import pandas as pd
import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000/recommend"
TEST_FILE = "data/Gen_AI_Dataset_Test.csv"
OUTPUT_FILE = "predictions_submission.csv"

print("🔍 Loading test set...")
test_df = pd.read_csv(TEST_FILE, encoding='cp1252')
print(f"✅ Loaded {len(test_df)} test queries\n")

results = []

for idx, row in test_df.iterrows():
    query = row['Query']
    
    print(f"Query {idx+1}/{len(test_df)}:")
    print(f"  {query[:80]}...")
    
    try:
        # Call your API
        response = requests.post(
            API_URL,
            json={"text": query, "use_ai": False},  # Disable AI for faster response
            timeout=30
        )
        response.raise_for_status()
        
        recommendations = response.json()['recommendations']
        
        # Add each recommendation as separate row (required format)
        for rec in recommendations[:10]:  # Max 10 as per requirement
            results.append({
                'Query': query,
                'Assessment_url': rec['url']
            })
        
        print(f"  ✅ Generated {len(recommendations)} recommendations\n")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")
        # Add at least one dummy recommendation to avoid empty results
        results.append({
            'Query': query,
            'Assessment_url': 'https://www.shl.com/products/product-catalog/'
        })
    
    time.sleep(1)  # Rate limiting

# Save in required format
output_df = pd.DataFrame(results)
output_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 70)
print(f"🎉 SUCCESS!")
print(f"   Total predictions: {len(results)}")
print(f"   Queries processed: {len(test_df)}")
print(f"   Saved to: {OUTPUT_FILE}")
print("=" * 70)

# Verify format
print("\nFirst 5 rows of submission:")
print(output_df.head())
