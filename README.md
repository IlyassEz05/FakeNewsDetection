# Détection de Fausses Nouvelles - Application Full-Stack

Application web complète pour la détection de fausses nouvelles utilisant la similarité sémantique avec MongoDB Vector Search.

## 🚀 Structure du Projet

```
fakenewsdetection/
├── backend/
│   ├── main.py              # Application FastAPI principale
│   ├── db.py                # Connexion MongoDB
│   ├── vector_search.py     # Recherche vectorielle
│   └── requirements.txt     # Dépendances Python
└── frontend/
    ├── index.html           # Interface utilisateur
    ├── style.css            # Styles CSS
    └── script.js            # Logique frontend
```

## 📋 Prérequis

- Python 3.8+
- MongoDB local (avec la collection de news déjà configurée)
- Index vectoriel MongoDB configuré : `news_vector_index`

## 🔧 Installation

### 1. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurer MongoDB

Assurez-vous que :
- MongoDB est démarré localement (`mongod`)
- La base de données contient une collection avec des articles
- L'index vectoriel `news_vector_index` est créé sur le champ `embedding`

### 3. Ajuster la configuration (si nécessaire)

Modifiez dans `backend/db.py` :
- `DATABASE_NAME` : nom de votre base de données
- `COLLECTION_NAME` : nom de votre collection

## ▶️ Démarrage

### Backend

```bash
cd backend
python main.py
```

Ou avec uvicorn directement :
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur `http://localhost:8000`

### Frontend

Ouvrez simplement `frontend/index.html` dans votre navigateur, ou servez-le avec un serveur HTTP local :

```bash
cd frontend
python -m http.server 8080
```

Puis ouvrez `http://localhost:8080` dans votre navigateur.

## 📡 API Endpoints

### POST /analyze

Analyse un texte pour détecter s'il s'agit de fausses nouvelles.

**Request:**
```json
{
  "text": "Votre texte à analyser ici..."
}
```

**Response:**
```json
{
  "verdict": "Information probablement vraie",
  "score": 0.9234,
  "closest_article": "Texte de l'article le plus proche...",
  "source_url": "https://example.com/article",
  "language": "fr"
}
```

## 🎯 Logique de Décision

- **score > 0.85** → "Information probablement vraie"
- **0.65 ≤ score ≤ 0.85** → "Information douteuse"
- **score < 0.65** → "Information probablement fausse"

## 🔍 Technologies Utilisées

- **Backend**: FastAPI, Python
- **Base de données**: MongoDB (local)
- **Recherche vectorielle**: MongoDB Atlas Vector Search ($vectorSearch)
- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2, 384 dimensions)
- **Frontend**: HTML, CSS, JavaScript vanilla

## 📝 Notes

- Le modèle sentence-transformers est chargé automatiquement au premier usage
- La détection de langue est automatique (français/anglais)
- L'application utilise l'agrégation MongoDB `$vectorSearch` pour la recherche

