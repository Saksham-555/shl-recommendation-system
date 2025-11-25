# 🧠 SHL Assessment Recommendation System

An AI-powered recommendation engine that helps HR professionals find the most relevant SHL assessments based on natural language queries or job descriptions.

---

## 🌟 Live Demo

- **Frontend:** [https://shl-recommendation-system-080.streamlit.app](https://shl-recommendation-system-080.streamlit.app)
- **API:** [https://shl-recommendation-system-bfvn.onrender.com](https://shl-recommendation-system-bfvn.onrender.com)
- **Docs:** [API Docs (Swagger)](https://shl-recommendation-system-bfvn.onrender.com/docs)
- **GitHub:** [https://github.com/Saksham-555/shl-recommendation-system](https://github.com/Saksham-555/shl-recommendation-system)

---

## 📊 Project Overview

This system helps hiring managers instantly discover relevant SHL assessments across 377+ Individual Test Solutions, powered by advanced semantic search and Google Gemini AI insights.

**Key Features:**
- Semantic Search over real SHL catalog (377 individual solutions)
- Test type balancing (technical vs. soft skill)
- AI-generated justifications using Google Gemini
- Streamlit frontend and REST API backend (FastAPI)
- Validated on provided test set (see results below)

---

## 💡 Quick Start

### 1. Environment Setup

Clone repository
git clone https://github.com/Saksham-555/shl-recommendation-system.git
cd shl-recommendation-system

Setup Python virtual environment
python -m venv venv
venv\Scripts\activate # On Windows

Install dependencies
pip install -r requirements.txt

Set up Gemini API key
echo GEMINI_API_KEY=your_google_gemini_api_key > .env


### 2. Running in Production

Both API and frontend are already deployed:

| Component        | URL                                                          |
|------------------|--------------------------------------------------------------|
| API Endpoint     | https://shl-recommendation-system-bfvn.onrender.com          |
| Frontend App     | https://shl-recommendation-system-080.streamlit.app          |
| API Documentation| https://shl-recommendation-system-bfvn.onrender.com/docs     |

### 3. Develop/Run Locally

Start API server
uvicorn app.api_fixed:app --reload

Start Streamlit UI
streamlit run frontend/streamlit_app.py


---
image.png

## 🛠️ Project Structure

shl-recommendation-system/
├── app/
│ ├── api_fixed.py # FastAPI backend
│ ├── rag.py # Vector DB builder
│ ├── scrapper_new.py # SHL web scraper
│ └── chroma_db/ # Vector DB (prebuilt)
├── data/
│ ├── shl_individual_assessments.json
│ ├── Gen_AI_Dataset_Train.csv
│ └── Gen_AI_Dataset_Test.csv
├── frontend/
│ └── streamlit_app.py
├── evaluation.py
├── predict_test.py
├── requirements.txt
├── README.md
├── predictions_submission.csv
└── .env


---

## 📡 API Endpoints

### `GET /health`
Returns system health.

### `POST /recommend`

**Input:**
{
"text": "Java developer who collaborates with business teams",
"use_ai": true
}

**Output:**
{
"query": "...",
"total_found": 15,
"returned": 10,
"recommendations": [
{
"name": "...",
"url": "...",
"description": "...",
"duration": "...",
"job_level": "...",
"test_type": "...",
"relevance_score": 0.82,
"ai_insights": "..."
}
]
}


Docs: [https://shl-recommendation-system-bfvn.onrender.com/docs](https://shl-recommendation-system-bfvn.onrender.com/docs)

---

## 🎨 Core Features

- Semantic retrieval (sentence-transformers all-MiniLM-L6-v2, 384-dimensional)
- Answers queries for technical and soft skills (balancing with Test Type K/P)
- Google Gemini AI for result explanations
- Download recommendations as CSV from UI
- Easily extendable to add Pre-packaged Solutions (if desired)

---

## 📊 Results

- **Total scraped assessments:** 377 (Individual Test Solutions)
- **Mean Recall@5:** 9.1%
- **Mean Recall@10:** 10.1%
- **Test queries evaluated:** 10 (train), 9 (test, in CSV)

**Why is Recall < 15%?**  
Following the assignment, only "Individual Test Solutions" are included (per instructions to ignore "Pre-packaged Job Solutions"). The provided label data mostly references Pre-packaged solutions, so this is expected.

---

## 📝 Evaluation

python evaluation.py

Results are saved to evaluation_results_k5.json and k10.json


**Test Predictions:**

python predict_test.py

Outputs predictions_submission.csv


---

## 🚀 Deployment

### Backend (Render.com)
- [x] pip install -r requirements.txt
- [x] uvicorn app.api_fixed:app --host 0.0.0.0 --port $PORT
- [x] GEMINI_API_KEY in environment variables

### Frontend (Streamlit Cloud)
- [x] App redeploys on pushing to `main`
- [x] Configurable API endpoint URL

---

## 🧑‍💻 Contributors

- **Saksham** ([@Saksham-555](https://github.com/Saksham-555))

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- SHL (assessment catalog)
- Google Gemini (free API)
- ChromaDB, Sentence-Transformers, Streamlit, and FastAPI

---

## 📝 Further Improvements

- Add Pre-packaged Solutions
- User feedback for re-ranking
- Duration/time filter
- Enhanced test type detection using LLM
- Cache popular queries for speed

---