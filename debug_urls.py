# save as debug_urls.py
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Load train data
df = pd.read_csv('data/Gen_AI_Dataset_Train.csv', encoding='cp1252')
print("Sample URLs from train data:")
print(df['Assessment_url'].head(3).tolist())

# Load ChromaDB
chroma_client = chromadb.PersistentClient(path="app/chroma_db")
collection = chroma_client.get_collection("shl_assessments")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Get one query
query = df.iloc[0]['Query']
print(f"\nQuery: {query[:80]}...")

# Get recommendations
results = collection.query(
    query_texts=[query],
    n_results=5,
    include=["metadatas"]
)

print("\nRecommended URLs:")
for i in range(5):
    print(f"{i+1}. {results['metadatas'][0][i]['url']}")

print("\n" + "="*80)
print("URL COMPARISON:")
print("="*80)
print("Train data URL format:", df['Assessment_url'].iloc[0])
print("Scraped URL format:   ", results['metadatas'][0][0]['url'])