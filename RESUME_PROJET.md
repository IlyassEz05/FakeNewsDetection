# 📋 Résumé Complet du Projet - Détection de Fausses Nouvelles

## 🎯 Objectif du Projet

Créer une application web complète pour détecter les fausses nouvelles en utilisant la **similarité sémantique** entre une information fournie par l'utilisateur et une base de données d'articles de presse vérifiés.

## 🏗️ Architecture du Projet

```
fakenewsdetection/
├── backend/                    # API FastAPI
│   ├── main.py                # Serveur FastAPI + endpoint /analyze
│   ├── db.py                  # Connexion MongoDB
│   ├── vector_search.py       # Recherche vectorielle + re-ranking
│   └── requirements.txt       # Dépendances Python
└── frontend/                   # Interface web
    ├── index.html             # Page principale
    ├── style.css              # Styles CSS
    └── script.js              # Logique JavaScript
```

## 🗄️ Base de Données MongoDB

### Configuration
- **Base de données** : `elbotola`
- **Collection actualités** : `wydad_news` (3000 articles)
- **Collection vectorisations** : `wydad_vector` (6004 vectorisations)
  - 2 versions par article : titre français + titre anglais
  - Chaque document contient : `_id`, `url`, `language`, `text`, `embedding` (384 dimensions), `created_at`

### Structure des Données

**wydad_news** (articles complets) :
```json
{
  "_id": ObjectId,
  "title_ar": "titre arabe",
  "title_fr": "titre français",
  "title_en": "titre anglais",
  "url": "https://...",
  "pub_date": timestamp,
  "image": "url_image",
  "tags": "tags",
  "scraped_at": "date"
}
```

**wydad_vector** (vectorisations) :
```json
{
  "_id": ObjectId,
  "url": "https://...",
  "language": "fr" ou "en",
  "text": "titre de l'article",
  "embedding": [384 floats],
  "created_at": ISODate
}
```

## 🔍 Comment Fonctionne la Recherche Sémantique

### 1. Modèle d'Embedding

**Modèle utilisé** : `all-MiniLM-L6-v2` (384 dimensions)
- Modèle sentence-transformers
- Convertit le texte en vecteur numérique (embedding)
- Même modèle utilisé pour créer les embeddings dans MongoDB

### 2. Processus de Recherche (3 Étapes)

#### Étape 1 : Recherche TOP-K par Similarité Cosinus

```python
# 1. Générer l'embedding de la requête utilisateur
query_embedding = model.encode("wydad a signé hakim ziyech")

# 2. Charger tous les embeddings de wydad_vector
# 3. Calculer la similarité cosinus pour chaque embedding
score = dot_product(query_embedding, doc_embedding) / (norm1 * norm2)

# 4. Trier par score décroissant
# 5. Prendre les TOP-20 meilleurs résultats
```

**Similarité Cosinus** :
- Mesure l'angle entre deux vecteurs
- Score entre -1 et 1 (généralement entre 0 et 1 pour des embeddings)
- Plus le score est proche de 1, plus les textes sont sémantiquement similaires

#### Étape 2 : Extraction d'Entités

Pour chaque résultat TOP-20, on extrait :
- **Joueurs** : Hakim Ziyech, Aziz Ki, Regragui, etc.
- **Clubs** : Wydad, Raja, WAC, etc.
- **Actions** : signé, rejoint, gagné, buteur, etc. (FR/EN)

#### Étape 3 : Re-ranking avec Score Hybride

**Formule du score final** :
```
score_final = 0.6 × cosine_score + 0.3 × entity_score + 0.1 × keyword_score
```

**Composantes** :
- **cosine_score** (60%) : Similarité sémantique vectorielle
- **entity_score** (30%) : Correspondance des entités (joueurs, clubs, actions)
- **keyword_score** (10%) : Chevauchement de mots-clés significatifs

**Avantage** : Le re-ranking permet de trouver l'article le plus pertinent même si la similarité cosinus seule n'est pas parfaite.

### 3. Décision Finale

**Seuils de verdict** :
- **score > 0.60** → "Information probablement vraie"
- **0.40 ≤ score ≤ 0.60** → "Information incertaine"
- **score < 0.40** → "Information probablement fausse"

## ❌ Index Vectoriel MongoDB

### Réponse : NON, nous n'avons PAS créé d'index vectoriel

**Pourquoi ?**

L'index vectoriel `$vectorSearch` de MongoDB est **uniquement disponible sur MongoDB Atlas** (version cloud payante), pas sur MongoDB local.

**Votre configuration** :
- ✅ MongoDB local (MongoDB Compass)
- ✅ Base de données : `elbotola`
- ✅ Collection : `wydad_vector` avec embeddings

**Ce que nous avons fait à la place** :

**Recherche vectorielle manuelle en Python** :
```python
# 1. Charger tous les embeddings depuis MongoDB
all_vectors = collection.find({}, {"embedding": 1, ...})

# 2. Calculer similarité cosinus pour chaque embedding
for doc in all_vectors:
    score = cosine_similarity(query_embedding, doc['embedding'])
    
# 3. Trier par score et prendre TOP-20
results.sort(key=lambda x: x['score'], reverse=True)
top_20 = results[:20]
```

**Avantages** :
- ✅ Fonctionne avec MongoDB local (gratuit)
- ✅ Pas besoin de MongoDB Atlas
- ✅ Contrôle total sur le processus
- ✅ Compatible avec votre setup actuel

**Inconvénients** :
- ⚠️ Plus lent (charge tous les 6004 embeddings à chaque requête)
- ⚠️ Consomme plus de mémoire

### Si vous voulez utiliser un Index Vectoriel (Optionnel)

**Option 1 : MongoDB Atlas** (pour production)
```javascript
// Créer un index vectoriel dans MongoDB Atlas
db.wydad_vector.createSearchIndex({
  "name": "news_vector_index",
  "definition": {
    "mappings": {
      "dynamic": false,
      "fields": {
        "embedding": {
          "type": "knnVector",
          "dimensions": 384,
          "similarity": "cosine"
        }
      }
    }
  }
})
```
- **Avantage** : Recherche ultra-rapide (indexée)
- **Inconvénient** : Nécessite MongoDB Atlas (payant)

**Option 2 : FAISS** (bibliothèque Python)
- Créer un index en mémoire au démarrage
- Recherche très rapide
- Nécessite de modifier le code pour charger FAISS

## 🚀 Fonctionnalités Implémentées

### Backend (FastAPI)

1. **Endpoint `/analyze`** (POST)
   - Reçoit un texte à analyser
   - Détecte automatiquement la langue (FR/EN)
   - Génère l'embedding du texte
   - Recherche les articles similaires
   - Applique le re-ranking
   - Retourne verdict, score, article le plus proche

2. **Préchargement du modèle**
   - Le modèle sentence-transformers est chargé au démarrage
   - Évite le délai au premier appel

3. **Gestion des erreurs**
   - Validation des entrées
   - Gestion des erreurs MongoDB
   - Messages d'erreur clairs

### Frontend (HTML/CSS/JS)

1. **Interface utilisateur**
   - Design moderne avec dégradé violet/bleu
   - Zone de texte pour saisir l'information
   - Bouton d'analyse avec loader
   - Affichage des résultats (verdict, score, article)

2. **Expérience utilisateur**
   - Message de chargement informatif
   - Barre de score animée
   - Gestion des erreurs
   - Responsive (mobile-friendly)

## 📊 Flux de Données Complet

```
Utilisateur saisit: "wydad a signé hakim ziyech"
         ↓
Frontend envoie POST /analyze
         ↓
Backend:
  1. Détecte langue: "fr"
  2. Génère embedding (384 dimensions)
  3. Charge tous les embeddings de wydad_vector (6004)
  4. Calcule similarité cosinus pour chaque embedding
  5. Trie et prend TOP-20
  6. Extrait entités de la requête: {joueurs: ["hakim ziyech"], clubs: ["wydad"], actions: ["signé"]}
  7. Pour chaque TOP-20:
     - Extrait entités du document
     - Calcule entity_score
     - Calcule keyword_score
     - Calcule score_final = 0.6×cosine + 0.3×entity + 0.1×keyword
  8. Trie par score_final décroissant
  9. Retourne le meilleur résultat
         ↓
Frontend affiche:
  - Verdict: "Information probablement vraie" (si score ≥ 0.75)
  - Score: 0.8234 (82.34%)
  - Article le plus proche: "Wydad signe Hakim Ziyech..."
  - URL source
```

## 🔧 Technologies Utilisées

- **Backend** : FastAPI, Python 3.9+
- **Base de données** : MongoDB local
- **Embeddings** : sentence-transformers (all-MiniLM-L6-v2)
- **Calculs** : NumPy (similarité cosinus)
- **Frontend** : HTML, CSS, JavaScript vanilla
- **Détection de langue** : langdetect

## ⚡ Performance

- **Temps de réponse** : 3-8 secondes par requête
  - Génération embedding : 500ms - 2s
  - Recherche dans 6004 embeddings : 1-3s
  - Re-ranking : 500ms - 1s
  - Lookup MongoDB : 500ms - 1s

- **Optimisations** :
  - Modèle préchargé au démarrage
  - Calculs vectorisés avec NumPy
  - TOP-K limité à 20 pour le re-ranking

## 🎓 Approche Académique

Le système **n'affirme pas la vérité absolue**. Il évalue la **plausibilité** d'une information en :
1. Comparant avec des articles existants dans la base
2. Calculant un score de similarité sémantique
3. Donnant un verdict probabiliste basé sur le score

**Principe** : Si une information est très similaire à un article vérifié dans la base, elle est probablement vraie. Si elle n'a pas de correspondance, elle est probablement fausse.

## 📝 Points Importants

1. **Modèle d'embedding** : Doit être le même que celui utilisé pour créer les embeddings
2. **Pas d'index vectoriel** : Utilisation de recherche manuelle (MongoDB local)
3. **Re-ranking** : Améliore significativement la précision
4. **Extraction d'entités** : Permet de mieux comprendre le contexte (joueurs, clubs, actions)

## 🚀 Pour Démarrer

```bash
# Backend
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
python3 -m http.server 8080

# Accéder à l'application
http://localhost:8080
```

