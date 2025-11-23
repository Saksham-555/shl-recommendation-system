"""
RAG Pipeline - Vector Database Creation
Creates ChromaDB with embeddings for semantic search
"""

import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
from pathlib import Path
from typing import List


class ChromaEmbeddingFunction:
    """Custom embedding function for ChromaDB"""
    
    def __init__(self):
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(input)
        return [embedding.tolist() for embedding in embeddings]


def stringify(value):
    """Convert lists to comma-separated strings"""
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return str(value)


def create_vector_db():
    """
    Create ChromaDB vector database from scraped assessments
    """
    print("🚀 Starting Vector Database Creation")
    print("=" * 70)
    
    # Initialize ChromaDB
    chroma_path = os.path.join("app", "chroma_db")
    Path(chroma_path).mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    
    print(f"✅ ChromaDB initialized at: {chroma_path}")
    
    # Load scraped data
    json_path = os.path.join("data", "shl_individual_assessments.json")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"❌ JSON file not found at {json_path}\n"
            f"   Please run scraper.py first!"
        )
    
    print(f"✅ Found JSON data at: {json_path}")
    
    with open(json_path, "r", encoding='utf-8') as f:
        assessments = json.load(f)
    
    if not isinstance(assessments, list):
        raise ValueError("JSON data should be a list of assessments")
    
    print(f"✅ Loaded {len(assessments)} assessments")
    
    # Prepare documents and metadata
    documents = []
    metadatas = []
    
    print("\n📝 Processing assessments...")
    
    for i, item in enumerate(assessments):
        if not isinstance(item, dict):
            print(f"⚠️  Skipping invalid item at index {i}")
            continue
        
        # Required fields check
        if 'name' not in item or 'url' not in item:
            print(f"⚠️  Skipping incomplete item at index {i}")
            continue
        
        # Combine all text fields for embedding
        # This creates a rich semantic representation
        combined_text = " ".join([
            item.get('name', ''),
            item.get('description', ''),
            item.get('duration', ''),
            stringify(item.get('languages', [])),
            item.get('job_level', ''),
            item.get('test_type', ''),
            item.get('remote_testing', ''),
            item.get('adaptive_support', '')
        ])
        
        documents.append(combined_text)
        
        # Store metadata for retrieval
        metadatas.append({
            "name": item.get("name", "Unknown"),
            "url": item.get("url", ""),
            "description": item.get("description", "No description"),
            "duration": item.get("duration", "Not specified"),
            "languages": stringify(item.get("languages", [])),
            "job_level": item.get("job_level", "Not specified"),
            "remote_testing": item.get("remote_testing", "Not specified"),
            "adaptive_support": item.get("adaptive_support", "Not specified"),
            "test_type": item.get("test_type", "Not specified")
        })
        
        if (i + 1) % 50 == 0:
            print(f"   Processed {i + 1}/{len(assessments)} assessments...")
    
    if not documents:
        raise ValueError("❌ No valid assessments found in JSON data")
    
    print(f"✅ Prepared {len(documents)} documents for embedding")
    
    # Delete existing collection if it exists
    try:
        chroma_client.delete_collection("shl_assessments")
        print("♻️  Deleted existing collection")
    except (ValueError, Exception):
        pass  # Collection didn't exist
    
    # Create collection with embedding function
    print("\n🔄 Creating ChromaDB collection...")
    collection = chroma_client.create_collection(
        name="shl_assessments",
        embedding_function=ChromaEmbeddingFunction()
    )
    
    # Add data in batches
    print("🔄 Adding embeddings to database...")
    batch_size = 100
    
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        
        collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=[str(j) for j in range(i, batch_end)]
        )
        
        print(f"   Added batch {i//batch_size + 1} ({batch_end} total)")
    
    print("\n" + "=" * 70)
    print(f"🎉 SUCCESS! Vector database created")
    print(f"   Total assessments: {len(documents)}")
    print(f"   Collection name: shl_assessments")
    print(f"   Storage path: {chroma_path}")
    print("=" * 70)


if __name__ == "__main__":
    create_vector_db()