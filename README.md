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

```
fakenewsdetection/
├── backend/
│   ├── main.py              # Main FastAPI application
│   ├── db.py                # MongoDB connection
│   ├── vector_search.py     # Vector search and similarity
│   ├── scraper.py           # Scraping and extraction scripts
│   ├── embedding.py         # Embedding generation
│   ├── pipeline.py          # Automated pipeline (cron)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # User interface
│   ├── style.css            # CSS styles
│   └── script.js            # Frontend logic
└── README.md
```

---

## 🛠️ Prerequisites

- **Python 3.9+**
- **Local MongoDB** (or MongoDB Atlas)
- Python libraries:
  - `requests`
  - `pandas`
  - `pymongo`
  - `sentence-transformers`
  - `fastapi`
  - `uvicorn`
  - `googletrans`
- **Cron** (Linux/macOS) for automating the pipeline

---

## 🔧 Installation and Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure MongoDB

Start MongoDB locally:

```bash
mongod
```

Create a database `elbotola` and collections:
- `wydad_news` → stores original articles (title, text, url, language, date)
- `wydad_vector` → stores vectorized articles (text, url, embedding, language, date)

Example connection in `db.py`:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["elbotola"]
news_collection = db["wydad_news"]
embedding_collection = db["wydad_vector"]
```

---

## 📝 Automated Pipeline

The full pipeline consists of several steps:

### Scraping
- Automatically extracts articles from `http://api.elbotola.com/newsfeed/v3/`
- Retrieves title, text, URL, language, and date
- Temporarily stores articles in the `wydad_news` collection

### Translation
- Automatically translates articles into French and English
- Stores translated versions linked via the same URL

### Vectorization (Embeddings)
- Uses the model `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Generates an embedding for each article (title + text)
- Stores embeddings in `wydad_vector` collection:

```json
{
  "url": "...",
  "language": "fr",
  "text": "...",
  "embedding": [0.01, -0.02, ...],
  "created_at": "2025-12-22T23:44:49.882+00:00"
}
```

- Total: ~3000 articles → 6004 embeddings (FR + EN)

### Automation via Cron

`pipeline.py` runs daily to update news articles.

Cron command (macOS/Linux):

```bash
crontab -e
```

Add:

```
0 2 * * * /usr/bin/python3 /Users/ilyassez/Documents/fakenewsdetection/backend/pipeline.py >> /Users/ilyassez/Documents/fakenewsdetection/logs/pipeline.log 2>&1
```

Executes the pipeline automatically at 2 AM daily.

---

## ▶️ Running the Web Application

### Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend server will be accessible at: `http://localhost:8000`

### Frontend

```bash
cd frontend
python -m http.server 8080
```

Open in browser: `http://localhost:8080`

---

## 🔍 Vector Search / Cosine Similarity

Every new article or text submitted is converted into an embedding.

Similarity with existing articles is calculated using cosine similarity:

```python
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))
```

The most similar articles (highest scores) are returned with their URL and text.

**Note:** MongoDB Atlas `$vectorSearch` can be used if available, but here we use **local MongoDB + Python cosine similarity** for manual calculation.

---

## 📡 API Endpoints

### POST /analyze

Analyze a text to detect similarity with existing articles.

**Request:**

```json
{
  "text": "Your text to analyze"
}
```

**Response:**

```json
{
  "verdict": "Information probablement vraie",
  "score": 0.9234,
  "closest_article": "Most similar article text...",
  "source_url": "https://example.com/article",
  "language": "fr"
}
```

### Verdict Logic

- **score > 0.60** → "Information probablement vraie"
- **0.40 ≤ score ≤ 0.60** → "Information incertaine"
- **score < 0.40** → "Information probablement fausse"

---

## 🖥️ Demonstration

The web application allows:
- Text-based search
- Displaying similar articles
- Filtering by language (automatic detection)
- Access to the original source URL
- Real-time similarity scoring

---

## 🎥 Demo Video
A short demonstration video of the project is available at the following link:
https://drive.google.com/file/d/1HCHqEBwnJZLu_9QHc9o8DQ0RZbSEu3kA/view?usp=drive_link

## 🔍 Technologies Used

- **Scraping & Processing**: `requests`, `pandas`, `googletrans`
- **Vectorization**: `sentence-transformers` (all-MiniLM-L6-v2)
- **Backend**: FastAPI, Python
- **Database**: MongoDB (local)
- **Automation**: Cron
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Search**: Cosine similarity (NumPy)

---

## 💡 Key Points

- ✅ Fully automated pipeline: scraping → translation → vectorization → storage
- ✅ Multilingual dataset (FR + EN)
- ✅ Semantic vectorization for intelligent search
- ✅ Web application for testing and visualizing fake news detection
- ✅ Hybrid re-ranking system (cosine similarity + entity matching + keyword overlap)
- ✅ Local MongoDB with manual vector search implementation

---

## 📚 Documentation

Additional documentation is available in the repository:
- `RESUME_PROJET.md` - Complete project summary
- `EXPLICATION_COMPLETE.md` - Detailed technical explanation
- `DIAGRAMMES_UML.md` - UML diagrams (Use Case, Class, Sequence, Component, Deployment)
- `INTRODUCTION_PRESENTATION.md` - Presentation materials

---

## 📄 License

This is an academic project developed for educational purposes.

---

## 👤 Author

**IlyassEz05**

- GitHub: [@IlyassEz05](https://github.com/IlyassEz05)
- Repository: [FakeNewsDetection](https://github.com/IlyassEz05/FakeNewsDetection)

---

## 🤝 Contributing

This is an academic project. Contributions and suggestions are welcome!

---

**Made with ❤️ for academic research in fake news detection**
