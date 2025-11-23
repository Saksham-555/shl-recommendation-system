"""
SHL Assessment Recommendation API
Using Google Gemini API for AI-powered insights
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from bs4 import BeautifulSoup
import requests
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()


# Initialize Google Gemini (free tier)
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('ggemini-1.5-flash')
except Exception as e:
    print(f"Warning: Gemini initialization failed: {e}")
    model = None


app = FastAPI(
    title="SHL Assessment Recommender",
    description="AI-powered assessment recommendations using RAG",
    version="1.0"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="app/chroma_db")


class QueryRequest(BaseModel):
    text: str
    use_ai: bool = True


def scrape_job_description(url: str) -> str:
    """Scrape job description from URL"""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple selectors for job descriptions
        selectors = [
            "div.job-description",
            "section.description",
            "div[class*='description']",
            "div[id*='description']"
        ]
        
        for selector in selectors:
            job_desc_div = soup.select_one(selector)
            if job_desc_div:
                return job_desc_div.get_text(" ", strip=True)
        
        return ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scraping error: {str(e)}")


def normalize_score(score: float) -> float:
    """Ensure scores are between 0-1 with fallback"""
    try:
        # ChromaDB returns distance (lower is better), convert to similarity
        return max(0.0, min(1.0, 1 - abs(float(score))))
    except:
        return 0.5


def generate_gemini_insights(description: str) -> str:
    """Generate short HR-focused insights using Gemini"""
    if not model:
        return "AI insights unavailable"
    
    try:
        prompt = f"""As an HR expert, analyze this assessment and provide 3 concise bullet points (max 15 words each):

Description: {description[:300]}

Format as:
• Key skill measured
• Ideal candidate level  
• Best use case"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
                temperature=0.3,
            )
        )
        
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "AI insights unavailable"


def balance_test_types(results: list, query_text: str) -> list:
    """Balance recommendations between Test Type K (Knowledge) and P (Personality)"""
    # Check if query mentions both technical and soft skills
    technical_keywords = [
        'java', 'python', 'sql', 'coding', 'technical', 'developer', 
        'programming', 'software', 'engineer', 'development'
    ]
    soft_keywords = [
        'communication', 'collaboration', 'teamwork', 'personality', 
        'leadership', 'behavioral', 'interpersonal', 'management'
    ]
    
    query_lower = query_text.lower()
    has_technical = any(kw in query_lower for kw in technical_keywords)
    has_soft = any(kw in query_lower for kw in soft_keywords)
    
    # If query needs both, ensure balanced mix
    if has_technical and has_soft:
        k_tests = [r for r in results if 'K' in r.get('test_type', '')]
        p_tests = [r for r in results if 'P' in r.get('test_type', '')]
        
        # Aim for 60% technical, 40% soft skills
        target_k = 6
        target_p = 4
        
        balanced = k_tests[:target_k] + p_tests[:target_p]
        return balanced[:10]
    
    return results[:10]


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SHL Assessment Recommendation API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gemini_status = "connected" if model else "unavailable"
    
    try:
        collection = chroma_client.get_collection("shl_assessments")
        db_count = collection.count()
        db_status = f"ready ({db_count} assessments)"
    except:
        db_status = "not initialized"
    
    return {
        "status": "healthy",
        "message": "SHL Assessment Recommendation API is running",
        "version": "1.0",
        "gemini_ai": gemini_status,
        "vector_db": db_status
    }


@app.post("/recommend")
async def recommend(request: QueryRequest):
    """
    Recommend assessments based on query
    
    Request body:
    - text: Job description or search query (or URL to scrape)
    - use_ai: Enable AI-generated insights (default: True)
    
    Returns: {"recommendations": [...]}
    """
    try:
        collection = chroma_client.get_collection("shl_assessments")
    except ValueError:
        raise HTTPException(
            status_code=500, 
            detail="Vector database not initialized. Please run rag.py first!"
        )

    # Handle URL or text query
    query_text = request.text.strip()
    
    if query_text.startswith(("http://", "https://")):
        print(f"Scraping job description from: {query_text}")
        query_text = scrape_job_description(query_text)
        
        if not query_text:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract job description from URL"
            )

    # Semantic search - get top 15 for filtering
    results = collection.query(
        query_texts=[query_text],
        n_results=15,
        include=["metadatas", "documents", "distances"]
    )

    # Build recommendations list
    recommendations = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        
        assessment = {
            "name": metadata.get("name", "Unknown"),
            "url": metadata.get("url", ""),
            "description": metadata.get("description", "No description available"),
            "duration": metadata.get("duration", "Not specified"),
            "languages": metadata.get("languages", "Not specified"),
            "job_level": metadata.get("job_level", "Not specified"),
            "remote_testing": metadata.get("remote_testing", "Not specified"),
            "adaptive_support": metadata.get("adaptive_support", "Not specified"),
            "test_type": metadata.get("test_type", "Not specified"),
            "relevance_score": normalize_score(results["distances"][0][i]),
        }
        
        # Add AI insights if requested
        if request.use_ai and model:
            assessment["ai_insights"] = generate_gemini_insights(
                metadata.get("description", "")
            )
        else:
            assessment["ai_insights"] = ""
        
        recommendations.append(assessment)

    # Apply Test Type balancing
    recommendations = balance_test_types(recommendations, request.text)
    
    # Return top 10 with proper format
    return {
        "query": query_text[:200] + "..." if len(query_text) > 200 else query_text,
        "total_found": len(results["ids"][0]),
        "returned": len(recommendations),
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
