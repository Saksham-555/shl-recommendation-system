# """
# Evaluation Script for SHL Assessment Recommendation System
# Calculates Mean Recall@K on the labeled train set
# """

# import pandas as pd
# import chromadb
# from sentence_transformers import SentenceTransformer
# import json
# from typing import List, Dict

# def load_train_data(csv_path: str) -> List[Dict]:
#     """
#     Load train data from CSV and parse ground truth URLs
#     Expected columns: Query, Assessment_url
#     """
#     # Try multiple encodings
#     for encoding in ['utf-8', 'cp1252', 'latin-1', 'iso-8859-1']:
#         try:
#             df = pd.read_csv(csv_path, encoding=encoding)
#             print(f"✅ Successfully read CSV with {encoding} encoding")
#             break
#         except (UnicodeDecodeError, Exception) as e:
#             if encoding == 'iso-8859-1':  # Last attempt
#                 raise Exception(f"Could not read CSV with any encoding: {e}")
#             continue
    
#     # Group by Query to get all relevant assessments
#     train_queries = []
#     for query, group in df.groupby('Query'):
#         relevant_urls = group['Assessment_url'].tolist()
#         train_queries.append({
#             'query': query,
#             'relevant_urls': relevant_urls
#         })
    
#     print(f"✅ Loaded {len(train_queries)} unique queries")
#     print(f"✅ Total labeled pairs: {len(df)} query-assessment pairs")
    
#     return train_queries

# def get_recommendations(query: str, collection, model, k: int = 10) -> List[str]:
#     """Get top K recommendation URLs for a query"""
#     results = collection.query(
#         query_texts=[query],
#         n_results=k,
#         include=["metadatas"]
#     )
    
#     # Extract URLs
#     recommended_urls = [
#         results["metadatas"][0][i]["url"] 
#         for i in range(len(results["ids"][0]))
#     ]
    
#     return recommended_urls

# def calculate_recall_at_k(recommended: List[str], relevant: List[str]) -> float:
#     """
#     Calculate Recall@K for a single query
#     Recall@K = (Number of relevant items in top K) / (Total relevant items)
#     """
#     if len(relevant) == 0:
#         return 0.0
    
#     matched = sum(1 for url in recommended if url in relevant)
#     recall = matched / len(relevant)
    
#     return recall

# def evaluate_system(train_csv_path: str, chroma_db_path: str = "app/chroma_db", k: int = 10):
#     """
#     Main evaluation function
#     """
#     print(f"🔍 Starting evaluation with K={k}")
#     print("=" * 60)
    
#     # Load model and database
#     print("📊 Loading model and vector database...")
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    
#     try:
#         collection = chroma_client.get_collection("shl_assessments")
#         print(f"✅ Loaded collection with {collection.count()} assessments")
#     except ValueError:
#         print("❌ Collection 'shl_assessments' not found. Run rag.py first!")
#         return
    
#     # Load train data
#     print(f"\n📂 Loading train data from: {train_csv_path}")
#     train_queries = load_train_data(train_csv_path)
#     print(f"✅ Loaded {len(train_queries)} queries with ground truth")
    
#     # Calculate Recall@K for each query
#     recall_scores = []
    
#     print(f"\n🎯 Calculating Recall@{k} for each query...")
#     print("-" * 60)
    
#     for i, item in enumerate(train_queries, 1):
#         query = item['query']
#         relevant_urls = item['relevant_urls']
        
#         # Get recommendations
#         recommended_urls = get_recommendations(query, collection, model, k)
        
#         # Calculate recall
#         recall = calculate_recall_at_k(recommended_urls, relevant_urls)
#         recall_scores.append(recall)
        
#         # Count matches
#         matches = sum(1 for url in recommended_urls if url in relevant_urls)
        
#         print(f"Query {i}/{len(train_queries)}:")
#         print(f"  Text: {query[:80]}...")
#         print(f"  Relevant assessments: {len(relevant_urls)}")
#         print(f"  Matched in top {k}: {matches}")
#         print(f"  Recall@{k}: {recall:.4f}")
#         print()
    
#     # Calculate mean recall
#     mean_recall = sum(recall_scores) / len(recall_scores)
    
#     print("=" * 60)
#     print(f"📊 FINAL RESULTS")
#     print("=" * 60)
#     print(f"Total queries evaluated: {len(train_queries)}")
#     print(f"Mean Recall@{k}: {mean_recall:.4f}")
#     print(f"Min Recall@{k}: {min(recall_scores):.4f}")
#     print(f"Max Recall@{k}: {max(recall_scores):.4f}")
#     print("=" * 60)
    
#     # Save results
#     results = {
#         "k": k,
#         "total_queries": len(train_queries),
#         "mean_recall": mean_recall,
#         "min_recall": min(recall_scores),
#         "max_recall": max(recall_scores),
#         "individual_scores": recall_scores
#     }
    
#     with open(f"evaluation_results_k{k}.json", "w") as f:
#         json.dump(results, f, indent=2)
    
#     print(f"\n✅ Results saved to evaluation_results_k{k}.json")
    
#     return mean_recall

# if __name__ == "__main__":
#     # Update this path to your train CSV
#     TRAIN_CSV = "data/Gen_AI_Dataset_Train.csv"
    
#     # Run evaluation for different K values
#     print("🚀 SHL Assessment Recommendation System - Evaluation\n")
    
#     for k in [5, 10]:
#         mean_recall = evaluate_system(TRAIN_CSV, k=k)
#         print(f"\n{'='*60}\n")
    
#     print("✅ Evaluation complete!")

"""
Evaluation Script for SHL Assessment Recommendation System
Calculates Mean Recall@K on the labeled train set
"""

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict


# def normalize_url(url: str) -> str:
#     """
#     Normalize URL for comparison
#     - Removes /solutions/ prefix if present
#     - Removes trailing slashes
#     - Converts to lowercase
#     """
#     normalized = url.replace('/solutions/products/', '/products/')
#     normalized = normalized.rstrip('/')
#     normalized = normalized.lower()
#     return normalized

def normalize_url(url: str) -> str:
    """
    Aggressive URL normalization - matches regardless of /solutions/ prefix
    """
    url = url.lower().strip().rstrip('/')
    
    # Remove protocol and domain
    url = url.replace('https://', '').replace('http://', '')
    url = url.replace('www.shl.com/', '').replace('shl.com/', '')
    
    # Normalize path - remove /solutions/ variations
    url = url.replace('solutions/products/product-catalog/view/', '')
    url = url.replace('products/product-catalog/view/', '')
    url = url.replace('solutions/products/', '')
    url = url.replace('products/', '')
    
    # Return just the assessment slug
    parts = [p for p in url.split('/') if p]
    if parts:
        return parts[-1]  # Final slug only: "automata-fix-new"
    
    return url

# Example transformations:
# https://www.shl.com/solutions/products/product-catalog/view/automata-fix-new/
# → automata-fix-new

# https://www.shl.com/products/product-catalog/view/automata-fix-new/
# → automata-fix-new



def load_train_data(csv_path: str) -> List[Dict]:
    """
    Load train data from CSV and parse ground truth URLs
    Expected columns: Query, Assessment_url
    """
    # Try multiple encodings
    for encoding in ['utf-8', 'cp1252', 'latin-1', 'iso-8859-1']:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"✅ Successfully read CSV with {encoding} encoding")
            break
        except (UnicodeDecodeError, Exception) as e:
            if encoding == 'iso-8859-1':
                raise Exception(f"Could not read CSV with any encoding: {e}")
            continue
    
    # Group by Query to get all relevant assessments
    train_queries = []
    for query, group in df.groupby('Query'):
        relevant_urls = group['Assessment_url'].tolist()
        train_queries.append({
            'query': query,
            'relevant_urls': relevant_urls
        })
    
    print(f"✅ Loaded {len(train_queries)} unique queries")
    print(f"✅ Total labeled pairs: {len(df)} query-assessment pairs")
    
    return train_queries


def get_recommendations(query: str, collection, model, k: int = 10) -> List[str]:
    """Get top K recommendation URLs for a query"""
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["metadatas"]
    )
    
    # Extract URLs
    recommended_urls = [
        results["metadatas"][0][i]["url"] 
        for i in range(len(results["ids"][0]))
    ]
    
    return recommended_urls


def calculate_recall_at_k(recommended: List[str], relevant: List[str]) -> float:
    """
    Calculate Recall@K for a single query with URL normalization
    Recall@K = (Number of relevant items in top K) / (Total relevant items)
    """
    if len(relevant) == 0:
        return 0.0
    
    # Normalize URLs for comparison
    recommended_normalized = [normalize_url(url) for url in recommended]
    relevant_normalized = [normalize_url(url) for url in relevant]
    
    matched = sum(1 for url in recommended_normalized if url in relevant_normalized)
    recall = matched / len(relevant)
    
    return recall


def evaluate_system(train_csv_path: str, chroma_db_path: str = "app/chroma_db", k: int = 10):
    """
    Main evaluation function
    """
    print(f"🔍 Starting evaluation with K={k}")
    print("=" * 60)
    
    # Load model and database
    print("📊 Loading model and vector database...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    
    try:
        collection = chroma_client.get_collection("shl_assessments")
        print(f"✅ Loaded collection with {collection.count()} assessments")
    except ValueError:
        print("❌ Collection 'shl_assessments' not found. Run rag.py first!")
        return
    
    # Load train data
    print(f"\n📂 Loading train data from: {train_csv_path}")
    train_queries = load_train_data(train_csv_path)
    print(f"✅ Loaded {len(train_queries)} queries with ground truth")
    
    # Calculate Recall@K for each query
    recall_scores = []
    
    print(f"\n🎯 Calculating Recall@{k} for each query...")
    print("-" * 60)
    
    for i, item in enumerate(train_queries, 1):
        query = item['query']
        relevant_urls = item['relevant_urls']
        
        # Get recommendations
        recommended_urls = get_recommendations(query, collection, model, k)
        
        # Calculate recall
        recall = calculate_recall_at_k(recommended_urls, relevant_urls)
        recall_scores.append(recall)
        
        # Count matches (with normalization for display)
        recommended_normalized = [normalize_url(url) for url in recommended_urls]
        relevant_normalized = [normalize_url(url) for url in relevant_urls]
        matches = sum(1 for url in recommended_normalized if url in relevant_normalized)
        
        print(f"Query {i}/{len(train_queries)}:")
        print(f"  Text: {query[:80]}...")
        print(f"  Relevant assessments: {len(relevant_urls)}")
        print(f"  Matched in top {k}: {matches}")
        print(f"  Recall@{k}: {recall:.4f}")
        print()
    
    # Calculate mean recall
    mean_recall = sum(recall_scores) / len(recall_scores)
    
    print("=" * 60)
    print(f"📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Total queries evaluated: {len(train_queries)}")
    print(f"Mean Recall@{k}: {mean_recall:.4f}")
    print(f"Min Recall@{k}: {min(recall_scores):.4f}")
    print(f"Max Recall@{k}: {max(recall_scores):.4f}")
    print("=" * 60)
    
    # Save results
    results = {
        "k": k,
        "total_queries": len(train_queries),
        "mean_recall": mean_recall,
        "min_recall": min(recall_scores),
        "max_recall": max(recall_scores),
        "individual_scores": recall_scores
    }
    
    with open(f"evaluation_results_k{k}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to evaluation_results_k{k}.json")
    
    return mean_recall


if __name__ == "__main__":
    TRAIN_CSV = "data/Gen_AI_Dataset_Train.csv"
    
    print("🚀 SHL Assessment Recommendation System - Evaluation\n")
    
    for k in [5, 10]:
        mean_recall = evaluate_system(TRAIN_CSV, k=k)
        print(f"\n{'='*60}\n")
    
    print("✅ Evaluation complete!")