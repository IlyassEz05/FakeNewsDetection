# 📚 Explication Complète du Système de Détection de Fausses Nouvelles

## 🎯 Vue d'Ensemble

Ce document explique **en détail** comment fonctionne tout le système, depuis que l'utilisateur saisit un texte dans le site web jusqu'à l'affichage du résultat final.

---

## 🔄 FLUX COMPLET : De l'Utilisateur à la Réponse

### Étape 1 : L'Utilisateur Saisit un Texte (Frontend)

**Fichier** : `frontend/script.js`

```javascript
// L'utilisateur tape dans le textarea
const text = textInput.value.trim();  // Exemple: "wydad a signé hakim ziyech"
```

**Ce qui se passe** :
1. L'utilisateur écrit un texte dans la zone de texte du site web
2. Clique sur le bouton "Analyser" ou appuie sur Ctrl+Enter
3. La fonction `analyzeText()` est déclenchée

### Étape 2 : Envoi de la Requête HTTP (Frontend → Backend)

**Code** : `frontend/script.js` lignes 42-49

```javascript
const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: text }),  // {"text": "wydad a signé hakim ziyech"}
    signal: controller.signal
});
```

**Ce qui se passe** :
- Le frontend envoie une requête HTTP POST vers `http://localhost:8000/analyze`
- Le corps de la requête contient le texte au format JSON : `{"text": "wydad a signé hakim ziyech"}`
- Le frontend attend la réponse (avec un timeout de 60 secondes)

---

### Étape 3 : Réception de la Requête (Backend - main.py)

**Fichier** : `backend/main.py`

**Code** : lignes 74-116

```python
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    # request.text contient maintenant "wydad a signé hakim ziyech"
    user_text = request.text.strip()
```

**Ce qui se passe** :
1. FastAPI reçoit la requête POST sur l'endpoint `/analyze`
2. Il valide automatiquement que le format correspond à `AnalyzeRequest` (qui contient un champ `text: str`)
3. Le texte est extrait et nettoyé (`.strip()` enlève les espaces au début/fin)

---

### Étape 4 : Détection de la Langue

**Code** : `backend/main.py` ligne 96

```python
language = vector_search.detect_language(user_text)
```

**Fonction appelée** : `backend/vector_search.py` lignes 249-272

```python
def detect_language(text: str) -> str:
    try:
        lang = detect(text)  # Utilise la bibliothèque langdetect
        if lang in ["fr", "fr-FR"]:
            return "fr"
        elif lang in ["en", "en-US", "en-GB"]:
            return "en"
        else:
            # Détection basique par caractères français
            return "fr" if any(char in text for char in "àâäéèêëïîôùûüÿç") else "en"
    except Exception:
        return "fr" if any(char in text for char in "àâäéèêëïîôùûüÿç") else "en"
```

**Ce qui se passe** :
- Pour "wydad a signé hakim ziyech" → détecte "fr" (français)
- Cette information sera utilisée pour filtrer les articles par langue plus tard

---

### Étape 5 : Recherche de l'Article le Plus Proche

**Code** : `backend/main.py` ligne 99

```python
closest_doc, score = vector_search.find_closest_article(user_text, language=language)
```

C'est **LA FONCTION PRINCIPALE** qui fait tout le travail ! Plongeons dans les détails.

---

## 🔍 DÉTAILS : La Fonction `find_closest_article()`

**Fichier** : `backend/vector_search.py` lignes 450-497

Cette fonction effectue **3 étapes principales** :

### Étape 5.1 : Génération de l'Embedding du Texte Utilisateur

**Code** : ligne 470

```python
query_embedding = generate_embedding(user_text, normalize=False)
```

**Fonction** : `generate_embedding()` lignes 275-295

```python
def generate_embedding(text: str, normalize: bool = False) -> List[float]:
    model = get_model()  # Récupère le modèle sentence-transformers
    embedding = model.encode(
        text,                    # "wydad a signé hakim ziyech"
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=normalize  # False dans notre cas
    )
    return embedding.tolist()  # Convertit en liste Python [0.123, -0.456, ...]
```

**Ce qui se passe** :
1. On récupère le modèle `all-MiniLM-L6-v2` (chargé une seule fois au démarrage)
2. Le modèle encode le texte en un vecteur de **384 nombres** (dimensions)
3. Exemple : "wydad a signé hakim ziyech" → `[0.123, -0.456, 0.789, ...]` (384 nombres)

**Explication** :
- Un embedding est une représentation numérique du sens du texte
- Plus deux textes ont un sens similaire, plus leurs embeddings sont proches dans l'espace vectoriel
- 384 dimensions = 384 nombres qui représentent différentes caractéristiques sémantiques

---

### Étape 5.2 : Recherche Vectorielle par Similarité Cosinus

**Code** : lignes 476-482

```python
top_k = 20
cosine_results = vector_search(query_embedding, limit=top_k, language_filter=language, min_score=-1.0)
```

#### 🔬 LA FONCTION `vector_search()` EN DÉTAIL

**Fichier** : `backend/vector_search.py` lignes 351-447

##### Sous-étape A : Connexion à MongoDB

```python
vectors_collection = db.get_vectors_collection()  # Collection wydad_vector
news_collection = db.get_news_collection()        # Collection wydad_news
```

**Fichier** : `backend/db.py`

```python
def get_vectors_collection():
    global _vectors_collection
    if _vectors_collection is None:
        database = get_database()
        _vectors_collection = database[VECTORS_COLLECTION_NAME]  # "wydad_vector"
    return _vectors_collection
```

##### Sous-étape B : Chargement de Tous les Embeddings

**Code** : lignes 380-384

```python
mongo_filter = {"language": "fr"}  # Si language="fr"

all_vectors = list(vectors_collection.find(
    mongo_filter,
    {"_id": 1, "url": 1, "language": 1, "text": 1, "embedding": 1, "created_at": 1}
))
```

**Ce qui se passe** :
- On charge **TOUS** les documents de `wydad_vector` qui ont `language="fr"` (environ 3002 documents sur 6004)
- Chaque document contient un embedding de 384 dimensions
- Exemple de document :
  ```json
  {
    "_id": ObjectId("..."),
    "url": "https://www.elbotola.com/article/...",
    "language": "fr",
    "text": "Wydad signe Hakim Ziyech",
    "embedding": [0.124, -0.457, 0.788, ...],  // 384 nombres
    "created_at": ISODate("...")
  }
  ```

##### Sous-étape C : Calcul de la Similarité Cosinus pour Chaque Embedding

**Code** : lignes 389-412

```python
# Convertir l'embedding de la requête en array NumPy
query_array = np.array(query_embedding, dtype=np.float32)
# Exemple: [0.123, -0.456, 0.789, ...] → array NumPy

# Calculer la norme du vecteur requête
query_norm = np.linalg.norm(query_array)
# Norme = longueur du vecteur = √(0.123² + (-0.456)² + 0.789² + ...)

scored_docs = []
for doc in all_vectors:  # Pour chaque document (3002 documents)
    doc_embedding = doc.get("embedding")  # [0.124, -0.457, 0.788, ...]
    doc_array = np.array(doc_embedding, dtype=np.float32)
    doc_norm = np.linalg.norm(doc_array)
    
    # CALCUL DE LA SIMILARITÉ COSINUS
    score = float(np.dot(query_array, doc_array) / (query_norm * doc_norm))
    
    if score >= min_score:  # min_score = -1.0, donc on garde tout
        scored_docs.append((score, doc))
```

#### 📐 EXPLICATION MATHÉMATIQUE : Similarité Cosinus

**Formule** :
```
similarité_cosinus = (A · B) / (||A|| × ||B||)
```

Où :
- `A · B` = produit scalaire (dot product) = A₁×B₁ + A₂×B₂ + ... + A₃₈₄×B₃₈₄
- `||A||` = norme du vecteur A = √(A₁² + A₂² + ... + A₃₈₄²)
- `||B||` = norme du vecteur B

**Exemple concret** :
```
Requête:     A = [0.123, -0.456, 0.789, ...] (384 dimensions)
Document 1:  B = [0.124, -0.457, 0.788, ...] (384 dimensions)

Produit scalaire: A · B = (0.123 × 0.124) + (-0.456 × -0.457) + (0.789 × 0.788) + ...
Norme A: ||A|| = √(0.123² + (-0.456)² + 0.789² + ...)
Norme B: ||B|| = √(0.124² + (-0.457)² + 0.788² + ...)

Similarité = (A · B) / (||A|| × ||B||)
           ≈ 0.85 (par exemple)
```

**Interprétation** :
- Score entre **-1 et 1** (généralement entre **0 et 1** pour des embeddings)
- **1.0** = textes identiques (vecteurs dans la même direction)
- **0.0** = textes orthogonaux (pas de relation)
- **-1.0** = textes opposés (rare avec des embeddings)
- Plus le score est proche de 1, plus les textes sont sémantiquement similaires

**Pourquoi la similarité cosinus ?**
- Elle mesure l'**angle** entre deux vecteurs, pas leur longueur
- Deux textes peuvent avoir des longueurs différentes mais le même sens → similarité élevée
- Exemple : "Wydad signe Ziyech" et "Le Wydad recrute Hakim Ziyech" ont des longueurs différentes mais un sens similaire → score cosinus élevé

##### Sous-étape D : Tri et Sélection des TOP-20

**Code** : lignes 414-416

```python
# Trier par score décroissant
scored_docs.sort(key=lambda x: x[0], reverse=True)
# Exemple: [(0.85, doc1), (0.72, doc2), (0.68, doc3), ...]

# Prendre les 20 meilleurs
top_results = scored_docs[:limit]  # limit = 20
```

**Ce qui se passe** :
- On trie les documents par score de similarité cosinus décroissant
- On garde seulement les **20 meilleurs résultats**
- Exemple : Les 20 articles les plus similaires à "wydad a signé hakim ziyech"

##### Sous-étape E : Lookup vers les Articles Complets

**Code** : lignes 418-445

```python
results = []
for score, doc in top_results:  # Pour chaque TOP-20
    url = doc.get("url")
    
    # Chercher l'article complet dans wydad_news
    article = news_collection.find_one({"url": url})
    
    # Construire le résultat final
    result_doc = {
        "_id": doc.get("_id"),
        "score": score,              # Score cosinus (ex: 0.85)
        "language": doc.get("language"),
        "text": doc.get("text"),     # "Wydad signe Hakim Ziyech"
        "url": url,
    }
    
    # Ajouter les infos de l'article complet si trouvé
    if article:
        result_doc["title_fr"] = article.get("title_fr")
        result_doc["title_en"] = article.get("title_en")
        result_doc["image"] = article.get("image")
    
    results.append(result_doc)
```

**Ce qui se passe** :
- Pour chaque document du TOP-20, on fait un lookup dans `wydad_news` avec le `url`
- On combine les informations de `wydad_vector` (embedding, texte) avec `wydad_news` (titres, image, etc.)
- On obtient une liste de 20 résultats avec leurs scores cosinus

**Retour de `vector_search()`** :
```python
[
    {
        "score": 0.85,
        "text": "Wydad signe Hakim Ziyech",
        "url": "https://...",
        "language": "fr",
        "title_fr": "Wydad signe Hakim Ziyech",
        ...
    },
    {
        "score": 0.72,
        "text": "Ziyech arrive au Wydad",
        "url": "https://...",
        ...
    },
    ... (18 autres résultats)
]
```

---

### Étape 5.3 : Extraction d'Entités de la Requête

**Code** : `find_closest_article()` ligne 488

```python
query_entities = extract_entities(user_text, language)
```

**Fonction** : `extract_entities()` lignes 70-108

```python
def extract_entities(text: str, language: str = 'fr') -> Dict[str, Set[str]]:
    text_lower = text.lower()  # "wydad a signé hakim ziyech"
    
    # Extraction des joueurs
    players = set()
    for player in KNOWN_PLAYERS:  # {'hakim ziyech', 'ziyech', 'aziz ki', ...}
        if player in text_lower:
            players.add(player)
    # Résultat: players = {'hakim ziyech', 'ziyech'}
    
    # Extraction des clubs
    clubs = set()
    for club in KNOWN_CLUBS:  # {'wydad', 'wydad casablanca', 'raja', ...}
        if club in text_lower:
            clubs.add(club)
    # Résultat: clubs = {'wydad'}
    
    # Extraction des actions
    actions = set()
    keywords = ACTION_KEYWORDS.get(language, ACTION_KEYWORDS['fr'])
    # ACTION_KEYWORDS['fr'] = {'signé', 'signer', 'rejoint', 'arrivé', ...}
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            actions.add(keyword)
    # Résultat: actions = {'signé'}
    
    return {
        'players': players,  # {'hakim ziyech', 'ziyech'}
        'clubs': clubs,      # {'wydad'}
        'actions': actions   # {'signé'}
    }
```

**Ce qui se passe** :
- On analyse le texte de la requête pour identifier :
  - **Joueurs** : "hakim ziyech", "ziyech"
  - **Clubs** : "wydad"
  - **Actions** : "signé"
- Ces entités seront utilisées pour améliorer la pertinence lors du re-ranking

---

### Étape 5.4 : Re-ranking avec Score Hybride

**Code** : `find_closest_article()` ligne 491

```python
re_ranked_results = re_rank_results(cosine_results, user_text, query_entities, language)
```

#### 🎯 LA FONCTION `re_rank_results()` EN DÉTAIL

**Fichier** : `backend/vector_search.py` lignes 191-246

##### Processus de Re-ranking

```python
def re_rank_results(results: List[Dict[str, Any]], 
                   query_text: str, 
                   query_entities: Dict[str, Set[str]],
                   language: str) -> List[Dict[str, Any]]:
    re_ranked = []
    
    for result in results:  # Pour chacun des 20 résultats TOP-K
        cosine_score = result.get('score', 0.0)  # Ex: 0.85
        doc_text = result.get('text', '')  # "Wydad signe Hakim Ziyech"
        
        # 1. Extraire les entités du document
        doc_entities = extract_entities(doc_text, language)
        # Exemple: {'players': {'hakim ziyech'}, 'clubs': {'wydad'}, 'actions': {'signe'}}
        
        # 2. Calculer le score d'entités
        entity_score = calculate_entity_match_score(query_entities, doc_entities)
        # Compare les entités de la requête avec celles du document
        
        # 3. Calculer le score de mots-clés
        keyword_score = calculate_keyword_overlap_score(query_text, doc_text)
        # Compare les mots significatifs communs
        
        # 4. CALCULER LE SCORE HYBRIDE FINAL
        cosine_normalized = max(0.0, min(1.0, cosine_score))  # S'assurer entre 0 et 1
        
        hybrid_score = (
            0.6 * cosine_normalized +    # 60% similarité sémantique vectorielle
            0.3 * entity_score +         # 30% correspondance d'entités
            0.1 * keyword_score          # 10% chevauchement de mots-clés
        )
        
        # Exemple de calcul:
        # cosine_normalized = 0.85
        # entity_score = 0.90 (beaucoup d'entités en commun)
        # keyword_score = 0.70 (beaucoup de mots en commun)
        # hybrid_score = 0.6 × 0.85 + 0.3 × 0.90 + 0.1 × 0.70
        #              = 0.51 + 0.27 + 0.07
        #              = 0.85
        
        result['score_final'] = hybrid_score
        re_ranked.append(result)
    
    # Trier par score final décroissant
    re_ranked.sort(key=lambda x: x.get('score_final', 0.0), reverse=True)
    
    return re_ranked
```

#### 📊 Calcul du Score d'Entités

**Fonction** : `calculate_entity_match_score()` lignes 111-156

```python
def calculate_entity_match_score(query_entities, doc_entities) -> float:
    score = 0.0
    total_weight = 0.0
    
    # Score pour les joueurs (poids 0.5)
    if query_entities['players']:
        player_intersection = query_entities['players'] & doc_entities['players']
        # Intersection: {'hakim ziyech'} & {'hakim ziyech', 'ziyech'} = {'hakim ziyech'}
        
        player_union = query_entities['players'] | doc_entities['players']
        # Union: {'hakim ziyech', 'ziyech'} | {'hakim ziyech'} = {'hakim ziyech', 'ziyech'}
        
        player_score = len(player_intersection) / len(player_union)
        # 1 / 2 = 0.5
        
        score += player_score * 0.5  # Poids 0.5
        total_weight += 0.5
    
    # Score pour les clubs (poids 0.3)
    if query_entities['clubs']:
        club_intersection = query_entities['clubs'] & doc_entities['clubs']
        # {'wydad'} & {'wydad'} = {'wydad'}
        club_union = query_entities['clubs'] | doc_entities['clubs']
        # {'wydad'} | {'wydad'} = {'wydad'}
        
        club_score = len(club_intersection) / len(club_union)
        # 1 / 1 = 1.0
        
        score += club_score * 0.3
        total_weight += 0.3
    
    # Score pour les actions (poids 0.2)
    if query_entities['actions']:
        action_intersection = query_entities['actions'] & doc_entities['actions']
        # {'signé'} & {'signe'} = {} (pas de correspondance exacte, mais "signé" et "signe" sont liés)
        # Pour simplifier, on cherche une correspondance exacte
        action_union = query_entities['actions'] | doc_entities['actions']
        
        action_score = len(action_intersection) / len(action_union) if action_union else 0.0
        # 0 / 2 = 0.0
        
        score += action_score * 0.2
        total_weight += 0.2
    
    # Normaliser le score
    if total_weight > 0:
        return score / total_weight
    
    # Exemple: score = 0.5*0.5 + 1.0*0.3 + 0.0*0.2 = 0.25 + 0.3 + 0 = 0.55
    # total_weight = 0.5 + 0.3 + 0.2 = 1.0
    # entity_score = 0.55 / 1.0 = 0.55
```

#### 🔤 Calcul du Score de Mots-Clés

**Fonction** : `calculate_keyword_overlap_score()` lignes 159-188

```python
def calculate_keyword_overlap_score(query_text: str, doc_text: str) -> float:
    # Tokeniser en mots
    query_words = set(re.findall(r'\b\w+\b', query_text.lower()))
    # {'wydad', 'a', 'signé', 'hakim', 'ziyech'}
    
    doc_words = set(re.findall(r'\b\w+\b', doc_text.lower()))
    # {'wydad', 'signe', 'hakim', 'ziyech'}
    
    # Exclure les mots vides (stopwords)
    stopwords = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'a', 'à', ...}
    
    query_words = {w for w in query_words if len(w) > 2 and w not in stopwords}
    # {'wydad', 'signé', 'hakim', 'ziyech'}
    
    doc_words = {w for w in doc_words if len(w) > 2 and w not in stopwords}
    # {'wydad', 'signe', 'hakim', 'ziyech'}
    
    # Calculer le chevauchement
    intersection = query_words & doc_words
    # {'wydad', 'hakim', 'ziyech'}
    
    overlap_score = len(intersection) / len(query_words)
    # 3 / 4 = 0.75
    
    return min(1.0, overlap_score)
```

---

### Étape 5.5 : Retour du Meilleur Résultat

**Code** : `find_closest_article()` lignes 493-497

```python
# Retourner le meilleur résultat (premier de la liste, déjà trié)
closest = re_ranked_results[0]
final_score = closest.get('score_final', closest.get('score', 0.0))

return closest, final_score
```

**Ce qui est retourné** :
```python
(
    {
        "score": 0.85,           # Score cosinus original
        "score_final": 0.88,     # Score hybride final (après re-ranking)
        "score_entity": 0.90,    # Score d'entités
        "score_keyword": 0.75,   # Score de mots-clés
        "text": "Wydad signe Hakim Ziyech",
        "url": "https://www.elbotola.com/article/...",
        "language": "fr",
        "title_fr": "Wydad signe Hakim Ziyech",
        ...
    },
    0.88  # Score final
)
```

---

### Étape 6 : Détermination du Verdict (Backend - main.py)

**Code** : `backend/main.py` lignes 103-105

```python
display_score = max(0.0, min(1.0, score))  # S'assurer entre 0 et 1
verdict = get_verdict(display_score)
```

**Fonction** : `get_verdict()` lignes 43-59

```python
def get_verdict(score: float) -> str:
    if score > 0.60:
        return "Information probablement vraie"
    elif score >= 0.40:
        return "Information incertaine"
    else:
        return "Information probablement fausse"
```

**Exemple** :
- Score final = 0.88 → "Information probablement vraie"
- Score final = 0.55 → "Information incertaine"
- Score final = 0.25 → "Information probablement fausse"

---

### Étape 7 : Construction de la Réponse JSON

**Code** : `backend/main.py` lignes 107-114

```python
response = AnalyzeResponse(
    verdict="Information probablement vraie",
    score=0.88,
    closest_article="Wydad signe Hakim Ziyech",
    source_url="https://www.elbotola.com/article/...",
    language="fr"
)
```

**Format JSON retourné** :
```json
{
    "verdict": "Information probablement vraie",
    "score": 0.88,
    "closest_article": "Wydad signe Hakim Ziyech",
    "source_url": "https://www.elbotola.com/article/...",
    "language": "fr"
}
```

---

### Étape 8 : Réception et Affichage (Frontend)

**Code** : `frontend/script.js` lignes 58-59

```javascript
const data = await response.json();
displayResults(data);
```

**Fonction** : `displayResults()` lignes 78-141

```javascript
function displayResults(data) {
    // Afficher le verdict
    verdictText.textContent = data.verdict;  // "Information probablement vraie"
    
    // Afficher le score
    const scorePercentage = Math.round(data.score * 100);
    scoreValue.textContent = `${scorePercentage}%`;  // "88%"
    scoreBar.style.width = `${scorePercentage}%`;    // Barre à 88%
    
    // Afficher l'article le plus proche
    closestArticle.textContent = data.closest_article;  // "Wydad signe Hakim Ziyech"
    
    // Afficher l'URL source
    sourceUrl.href = data.source_url;
    
    // Afficher la langue détectée
    detectedLanguage.textContent = "Français";
}
```

**Ce qui se passe** :
- Le frontend reçoit la réponse JSON
- Il met à jour l'interface utilisateur :
  - Badge du verdict (vert pour "vraie", orange pour "incertaine", rouge pour "fausse")
  - Barre de score animée (88% de largeur)
  - Texte de l'article le plus proche
  - Lien vers l'article source
  - Langue détectée

---

## 🔧 ARCHITECTURE TECHNIQUE

### Intégration dans main.py

**Imports** : `backend/main.py` lignes 9-10

```python
import vector_search  # Module de recherche vectorielle
import db             # Module de connexion MongoDB
```

**Utilisation** :
1. `vector_search.detect_language()` → Détection de langue
2. `vector_search.find_closest_article()` → Recherche principale
3. `db.close_connection()` → Fermeture MongoDB (au shutdown)

### Préchargement du Modèle

**Code** : `backend/main.py` lignes 127-140

```python
@app.on_event("startup")
async def startup_event():
    print("🔄 Préchargement du modèle sentence-transformers...")
    vector_search.get_model()  # Charge le modèle au démarrage
    print("✅ Modèle chargé avec succès")
```

**Pourquoi ?**
- Le modèle est lourd (~90 MB)
- Le charger prend 2-5 secondes
- En le préchargeant au démarrage, la première requête est aussi rapide que les suivantes

### Fermeture MongoDB

**Code** : `backend/main.py` lignes 143-148

```python
@app.on_event("shutdown")
async def shutdown_event():
    db.close_connection()  # Ferme proprement la connexion MongoDB
```

---

## 📊 RÉCAPITULATIF DU FLUX COMPLET

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. UTILISATEUR saisit "wydad a signé hakim ziyech"              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND (script.js)                                         │
│    - analyzeText() déclenché                                    │
│    - POST http://localhost:8000/analyze                         │
│    - Body: {"text": "wydad a signé hakim ziyech"}              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. BACKEND (main.py) - analyze_text()                           │
│    - Reçoit AnalyzeRequest                                      │
│    - Extrait: user_text = "wydad a signé hakim ziyech"         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. DÉTECTION DE LANGUE (vector_search.detect_language)          │
│    - Langue détectée: "fr"                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. RECHERCHE PRINCIPALE (vector_search.find_closest_article)    │
│    │                                                             │
│    ├─ 5.1. Génération embedding                                 │
│    │      model.encode("wydad a signé hakim ziyech")           │
│    │      → [0.123, -0.456, 0.789, ...] (384 dimensions)       │
│    │                                                             │
│    ├─ 5.2. Recherche vectorielle                                │
│    │      - Charge 3002 embeddings depuis MongoDB               │
│    │      - Calcule similarité cosinus pour chacun              │
│    │      - Trie et prend TOP-20                                │
│    │                                                             │
│    ├─ 5.3. Extraction d'entités                                 │
│    │      - Joueurs: {'hakim ziyech', 'ziyech'}                 │
│    │      - Clubs: {'wydad'}                                    │
│    │      - Actions: {'signé'}                                  │
│    │                                                             │
│    └─ 5.4. Re-ranking hybride                                   │
│           - Score final = 0.6×cosine + 0.3×entity + 0.1×keyword │
│           - Trie par score final                                │
│           - Retourne le meilleur                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. DÉTERMINATION DU VERDICT (get_verdict)                       │
│    - Score = 0.88 > 0.60                                        │
│    - Verdict = "Information probablement vraie"                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. CONSTRUCTION DE LA RÉPONSE JSON                              │
│    {                                                             │
│      "verdict": "Information probablement vraie",               │
│      "score": 0.88,                                             │
│      "closest_article": "Wydad signe Hakim Ziyech",            │
│      "source_url": "https://...",                               │
│      "language": "fr"                                           │
│    }                                                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. FRONTEND (displayResults)                                    │
│    - Affiche verdict                                            │
│    - Affiche score (88%)                                        │
│    - Affiche article le plus proche                             │
│    - Affiche lien source                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ TEMPS D'EXÉCUTION APPROXIMATIF

1. **Génération embedding** : 500ms - 2s
2. **Chargement MongoDB** : 500ms - 1s (3002 documents)
3. **Calcul similarité cosinus** : 1-2s (3002 calculs)
4. **Re-ranking** : 500ms - 1s (20 résultats)
5. **Lookup MongoDB** : 500ms - 1s (20 lookups)

**Total** : ~3-7 secondes par requête

---

## 🎓 POINTS CLÉS À RETENIR

1. **Embedding** : Transformation du texte en vecteur numérique (384 nombres)
2. **Similarité cosinus** : Mesure de la similarité sémantique entre deux vecteurs
3. **Re-ranking** : Amélioration de la précision avec un score hybride (60% cosinus + 30% entités + 10% mots-clés)
4. **Pas d'index vectoriel** : Calcul manuel car MongoDB local (pas Atlas)
5. **Performance** : 3-7 secondes par requête (charge tous les embeddings)

---

Voilà ! C'est l'explication complète de tout le système. Si vous avez des questions sur une partie spécifique, n'hésitez pas à demander !

