# Fake News Detection - Full-Stack Academic Project

This academic project aims to build a **complete web application** capable of detecting fake news based on the **semantic similarity** between news articles. It combines **automated scraping**, **translation**, **vectorization**, **MongoDB storage**, and a web interface for searching and analyzing articles.

---

## 🚀 Project Objectives

- Automatically extract news articles from online sources (scraping)
- Translate articles into **French and English** for a multilingual dataset
- Generate embeddings (vectors) from the text for semantic search
- Store the data and embeddings in **MongoDB**
- Automate the entire pipeline (scraping → translation → vectorization → storage) using a `cron` job
- Develop a web application to search and compare articles based on similarity

---

## 📋 Project Structure

fakenewsdetection/
├── backend/
│ ├── main.py # Main FastAPI application
│ ├── db.py # MongoDB connection
│ ├── scraper.py # Scraping and extraction scripts
│ ├── embedding.py # Embedding generation
│ ├── pipeline.py # Automated pipeline (cron)
│ └── requirements.txt # Python dependencies
├── frontend/
│ ├── index.html # User interface
│ ├── style.css # CSS styles
│ └── script.js # Frontend logic
└── README.md

---

## 🛠️ Prerequisites

- **Python 3.9+**
- **Local MongoDB** (or Atlas if available)
- Python libraries: `requests`, `pandas`, `pymongo`, `sentence-transformers`, `fastapi`, `uvicorn`, `googletrans`
- **Cron** (Linux/macOS) for automating the pipeline

---

## 🔧 Installation and Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
2. Configure MongoDB
Start MongoDB locally:
mongod
Create a database news_db and collections:
news → stores original articles (title, text, url, language, date)
news_embedding → stores vectorized articles (text, url, embedding, language, date)
Example connection in db.py:
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
news_collection = db["news"]
embedding_collection = db["news_embedding"]
📝 Automated Pipeline
The full pipeline consists of several steps:
1. Scraping
Automatically extracts articles from http://api.elbotola.com/newsfeed/v3/
Retrieves title, text, url, language, and date
Temporarily stores articles in the news collection
2. Translation
Automatically translates articles into French and English
Stores translated versions linked via the same url
3. Vectorization (Embeddings)
Uses the model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions)
Generates an embedding for each article (title + text)
Stores embeddings in news_embedding collection:
{
  "url": "...",
  "language": "fr",
  "text": "...",
  "embedding": [0.01, -0.02, ...],
  "created_at": "2025-12-22T23:44:49.882+00:00"
}
Total: ~3000 articles → 6002 embeddings (FR + EN)
4. Automation via Cron
Script pipeline.py runs daily to update news articles
Cron command (macOS/Linux):
crontab -e
Add:
0 2 * * * /usr/bin/python3 /Users/ilyassez/Documents/fakenewsdetection/backend/pipeline.py >> /Users/ilyassez/Documents/fakenewsdetection/logs/pipeline.log 2>&1
Executes the pipeline automatically at 2 AM daily
▶️ Running the Web Application
Backend (FastAPI)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The backend server will be accessible at: http://localhost:8000
Frontend
cd frontend
python -m http.server 8080
Open in browser: http://localhost:8080
🔍 Vector Search / Cosine Similarity
Every new article or text submitted is converted into an embedding
Similarity with existing articles is calculated using cosine similarity:
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))
The most similar articles (highest scores) are returned with their URL and text
Note: MongoDB Atlas $vectorSearch can be used if available, but here we use local MongoDB + Python cosine similarity
📡 API Endpoints
POST /analyze
Analyze a text to detect similarity with existing articles
Request:

{
  "text": "Your text to analyze"
}
Response:
{
  "verdict": "Probably true information",
  "score": 0.9234,
  "closest_article": "Most similar article text...",
  "source_url": "https://example.com/article",
  "language": "fr"
}
🖥️ Demonstration
The web application allows:
Text-based search
Displaying similar articles
Filtering by language
Access to the original source URL
🔍 Technologies Used
Scraping & Processing: requests, pandas, googletrans
Vectorization: sentence-transformers
Backend: FastAPI, Python
Database: MongoDB (local)
Automation: Cron
Frontend: HTML, CSS, JavaScript
Search: Cosine similarity
💡 Key Points
Fully automated pipeline: scraping → translation → vectorization → storage
Multilingual dataset (FR + EN)
Semantic vectorization for intelligent search
Web application for testing and visualizing fake news detection
