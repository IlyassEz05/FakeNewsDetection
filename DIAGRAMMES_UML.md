# 📊 Diagrammes UML pour le Projet de Détection de Fausses Nouvelles

## 🎯 Diagrammes Recommandés pour votre Projet

### 1. **Diagramme de Cas d'Utilisation** (Use Case Diagram)
- **Utilité** : Montre les interactions entre l'utilisateur et le système
- **Acteurs** : Utilisateur (sans authentification nécessaire)
- **Cas d'utilisation** : Analyser une information, Consulter les résultats

### 2. **Diagramme de Classe** (Class Diagram)
- **Utilité** : Structure des classes et leurs relations
- **Classes principales** : Modèles de données (AnalyzeRequest, AnalyzeResponse), Services (VectorSearch, DatabaseConnection), Modèle ML (SentenceTransformer)

### 3. **Diagramme de Séquence** (Sequence Diagram)
- **Utilité** : Flux d'exécution d'une requête d'analyse
- **Montre** : Interaction entre Frontend → Backend → MongoDB → Modèle ML

### 4. **Diagramme de Composants** (Component Diagram)
- **Utilité** : Architecture des composants du système
- **Composants** : Frontend, Backend API, Base de données, Modèle ML

### 5. **Diagramme de Déploiement** (Deployment Diagram)
- **Utilité** : Architecture physique du système
- **Montre** : Navigateur web, Serveur FastAPI, MongoDB local

---

## 📋 1. Diagramme de Cas d'Utilisation

### Entités et Acteurs

**Acteur** :
- **Utilisateur** : Personne qui utilise l'application web pour vérifier une information

**Cas d'utilisation** :
1. **Analyser une information** : L'utilisateur saisit un texte et demande une analyse
2. **Consulter les résultats** : L'utilisateur visualise le verdict, le score et l'article le plus proche
3. **Voir les détails de l'article** : L'utilisateur accède à l'URL source de l'article

### Diagramme de Cas d'Utilisation (Format Mermaid)

```mermaid
graph TB
    User[👤 Utilisateur]
    
    UC1[Analyser une information]
    UC2[Consulter les résultats]
    UC3[Voir les détails de l'article]
    
    User --> UC1
    User --> UC2
    User --> UC3
    
    UC1 -.->|inclut| UC2
    UC2 -.->|peut inclure| UC3
```

### Description Textuelle

```
┌─────────────────────────────────────────┐
│         Système de Détection            │
│         de Fausses Nouvelles            │
└─────────────────────────────────────────┘
              │
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐      ┌──────────────┐
│ Analyser│      │ Consulter les│
│ une info│      │   résultats  │
└─────────┘      └──────────────┘
    │                   │
    └─────────┬─────────┘
              │
              ▼
    ┌──────────────────┐
    │ Voir les détails │
    │   de l'article   │
    └──────────────────┘

Acteur: 👤 Utilisateur
```

---

## 🏗️ 2. Diagramme de Classe

### Entités Identifiées

**Classes principales** :

1. **AnalyzeRequest** (Modèle de données)
   - Attributs : `text: str`
   - Méthodes : Validation

2. **AnalyzeResponse** (Modèle de données)
   - Attributs : `verdict: str`, `score: float`, `closest_article: str`, `source_url: str`, `language: str`

3. **VectorSearchService** (Service de recherche)
   - Méthodes : `find_closest_article()`, `vector_search()`, `generate_embedding()`, `extract_entities()`, `re_rank_results()`

4. **DatabaseConnection** (Service de base de données)
   - Méthodes : `get_news_collection()`, `get_vectors_collection()`, `close_connection()`

5. **LanguageDetector** (Service utilitaire)
   - Méthodes : `detect_language()`

6. **EmbeddingModel** (Modèle ML)
   - Attributs : `model: SentenceTransformer`
   - Méthodes : `get_model()`, `encode()`

7. **Article** (Entité métier)
   - Attributs : `_id`, `title_fr`, `title_en`, `url`, `pub_date`, etc.

8. **VectorizedArticle** (Entité métier)
   - Attributs : `_id`, `url`, `language`, `text`, `embedding`, `created_at`

### Diagramme de Classe (Format Mermaid)

```mermaid
classDiagram
    class AnalyzeRequest {
        +str text
        +validate()
    }
    
    class AnalyzeResponse {
        +str verdict
        +float score
        +str closest_article
        +str source_url
        +str language
    }
    
    class VectorSearchService {
        -SentenceTransformer model
        +find_closest_article(text, language) Tuple
        +vector_search(embedding, limit) List
        +generate_embedding(text) List[float]
        +extract_entities(text, language) Dict
        +re_rank_results(results, query, entities) List
        +cosine_similarity(vec1, vec2) float
    }
    
    class DatabaseConnection {
        -MongoClient client
        -Database database
        +get_news_collection() Collection
        +get_vectors_collection() Collection
        +close_connection()
    }
    
    class LanguageDetector {
        +detect_language(text) str
    }
    
    class EmbeddingModel {
        -SentenceTransformer model
        +get_model() SentenceTransformer
        +encode(text) List[float]
    }
    
    class Article {
        +ObjectId _id
        +str title_fr
        +str title_en
        +str title_ar
        +str url
        +int pub_date
        +str image
        +str tags
    }
    
    class VectorizedArticle {
        +ObjectId _id
        +str url
        +str language
        +str text
        +List[float] embedding
        +datetime created_at
    }
    
    class FastAPIApp {
        +app: FastAPI
        +analyze_text(request) AnalyzeResponse
        +get_verdict(score) str
    }
    
    FastAPIApp --> AnalyzeRequest
    FastAPIApp --> AnalyzeResponse
    FastAPIApp --> VectorSearchService
    VectorSearchService --> DatabaseConnection
    VectorSearchService --> EmbeddingModel
    VectorSearchService --> LanguageDetector
    DatabaseConnection --> Article
    DatabaseConnection --> VectorizedArticle
```

### Diagramme de Classe Détaillé (Format Textuel)

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPIApp                            │
├─────────────────────────────────────────────────────────────┤
│ - app: FastAPI                                              │
├─────────────────────────────────────────────────────────────┤
│ + analyze_text(request: AnalyzeRequest) : AnalyzeResponse  │
│ + get_verdict(score: float) : str                          │
│ + startup_event()                                           │
│ + shutdown_event()                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ utilise
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AnalyzeRequest                            │
├─────────────────────────────────────────────────────────────┤
│ - text: str                                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   AnalyzeResponse                           │
├─────────────────────────────────────────────────────────────┤
│ - verdict: str                                              │
│ - score: float                                              │
│ - closest_article: str                                      │
│ - source_url: str                                           │
│ - language: str                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                VectorSearchService                          │
├─────────────────────────────────────────────────────────────┤
│ - model: SentenceTransformer                                │
│ - KNOWN_PLAYERS: Set[str]                                   │
│ - KNOWN_CLUBS: Set[str]                                     │
│ - ACTION_KEYWORDS: Dict[str, Set[str]]                     │
├─────────────────────────────────────────────────────────────┤
│ + find_closest_article(text, language) : Tuple             │
│ + vector_search(embedding, limit) : List[Dict]           │
│ + generate_embedding(text) : List[float]                   │
│ + extract_entities(text, language) : Dict                 │
│ + re_rank_results(results, query, entities) : List         │
│ + cosine_similarity(vec1, vec2) : float                    │
│ + detect_language(text) : str                              │
│ - normalize_vector(vec) : np.ndarray                        │
│ - calculate_entity_match_score() : float                   │
│ - calculate_keyword_overlap_score() : float                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ utilise
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
│DatabaseConnect│  │EmbeddingModel│  │LanguageDetector  │
├───────────────┤  ├──────────────┤  ├──────────────────┤
│-client        │  │-model        │  │                  │
│-database      │  │              │  │                  │
├───────────────┤  ├──────────────┤  ├──────────────────┤
│+get_news_     │  │+get_model()  │  │+detect_language()│
│ collection()  │  │+encode()     │  │                  │
│+get_vectors_  │  │              │  │                  │
│ collection()  │  │              │  │                  │
│+close_        │  │              │  │                  │
│ connection()  │  │              │  │                  │
└───────────────┘  └──────────────┘  └──────────────────┘
        │
        │ accède à
        ▼
┌─────────────────────────────────────────────────────────────┐
│                         Article                             │
├─────────────────────────────────────────────────────────────┤
│ - _id: ObjectId                                             │
│ - title_fr: str                                              │
│ - title_en: str                                              │
│ - title_ar: str                                              │
│ - url: str                                                   │
│ - pub_date: int                                              │
│ - image: str                                                 │
│ - tags: str                                                  │
│ - scraped_at: datetime                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   VectorizedArticle                         │
├─────────────────────────────────────────────────────────────┤
│ - _id: ObjectId                                             │
│ - url: str                                                   │
│ - language: str                                              │
│ - text: str                                                  │
│ - embedding: List[float] (384 dimensions)                    │
│ - created_at: datetime                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. Diagramme de Séquence

### Diagramme de Séquence (Format Mermaid)

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant API as FastAPI App
    participant VS as VectorSearchService
    participant DB as MongoDB
    participant ML as Modèle ML

    U->>F: Saisit un texte
    F->>API: POST /analyze {text: "..."}
    
    API->>VS: detect_language(text)
    VS-->>API: "fr"
    
    API->>VS: find_closest_article(text, language)
    
    VS->>ML: generate_embedding(text)
    ML-->>VS: embedding [384 floats]
    
    VS->>DB: find() - Charger tous les embeddings
    DB-->>VS: 6004 documents avec embeddings
    
    VS->>VS: Calculer similarité cosinus pour chaque embedding
    VS->>VS: Trier et prendre TOP-20
    
    VS->>VS: extract_entities(query)
    VS->>VS: re_rank_results() - Score hybride
    
    VS->>DB: find_one({url: ...}) - Lookup article
    DB-->>VS: Article complet
    
    VS-->>API: (closest_doc, final_score)
    
    API->>API: get_verdict(score)
    API-->>F: AnalyzeResponse {verdict, score, article, url}
    
    F->>U: Affiche les résultats
```

---

## 🧩 4. Diagramme de Composants

### Diagramme de Composants (Format Mermaid)

```mermaid
graph TB
    subgraph "Frontend"
        HTML[HTML/CSS/JS]
    end
    
    subgraph "Backend"
        API[FastAPI Application]
        VS[VectorSearchService]
        DB_CONN[DatabaseConnection]
    end
    
    subgraph "Base de Données"
        MONGO[(MongoDB)]
        NEWS[wydad_news Collection]
        VECTORS[wydad_vector Collection]
    end
    
    subgraph "Modèle ML"
        ST[SentenceTransformer]
        MODEL[all-MiniLM-L6-v2]
    end
    
    HTML -->|HTTP POST| API
    API --> VS
    API --> DB_CONN
    VS --> ST
    ST --> MODEL
    DB_CONN --> MONGO
    MONGO --> NEWS
    MONGO --> VECTORS
```

---

## 🖥️ 5. Diagramme de Déploiement

### Diagramme de Déploiement (Format Mermaid)

```mermaid
graph TB
    subgraph "Machine Locale"
        subgraph "Navigateur Web"
            BROWSER[Chrome/Firefox/Safari]
        end
        
        subgraph "Serveur Backend"
            FASTAPI[FastAPI Server<br/>Port 8000]
            PYTHON[Python 3.9+]
        end
        
        subgraph "Base de Données"
            MONGO[(MongoDB Local<br/>Port 27017)]
            COMPASS[MongoDB Compass]
        end
        
        subgraph "Modèle ML"
            MODEL_FILE[all-MiniLM-L6-v2<br/>Modèle local]
        end
    end
    
    BROWSER -->|HTTP| FASTAPI
    FASTAPI --> PYTHON
    FASTAPI --> MONGO
    FASTAPI --> MODEL_FILE
    COMPASS --> MONGO
```

---

## 📝 Notes pour la Documentation

### Points à Mentionner dans votre Rapport

1. **Pas d'authentification** : Le système est ouvert, pas de gestion d'utilisateurs
2. **Architecture simple** : Frontend → Backend → Base de données
3. **Modèle ML intégré** : Sentence-transformers chargé en mémoire
4. **Base de données locale** : MongoDB local (pas de cloud)

### Diagrammes à Inclure dans votre Rapport

**Minimum requis** :
1. ✅ Diagramme de Cas d'Utilisation
2. ✅ Diagramme de Classe
3. ✅ Diagramme de Séquence

**Optionnels (pour plus de détails)** :
4. Diagramme de Composants
5. Diagramme de Déploiement

---

## 🛠️ Outils pour Créer les Diagrammes

1. **Draw.io / diagrams.net** (gratuit, en ligne)
2. **Lucidchart** (gratuit avec limitations)
3. **PlantUML** (gratuit, basé sur texte)
4. **Visual Paradigm** (gratuit pour étudiants)
5. **Mermaid** (gratuit, intégré dans Markdown)

### Exemple PlantUML (pour diagramme de classe)

```plantuml
@startuml
class AnalyzeRequest {
    - text: str
}

class AnalyzeResponse {
    - verdict: str
    - score: float
    - closest_article: str
    - source_url: str
    - language: str
}

class VectorSearchService {
    - model: SentenceTransformer
    + find_closest_article(text, language): Tuple
    + vector_search(embedding, limit): List
    + generate_embedding(text): List[float]
}

class DatabaseConnection {
    - client: MongoClient
    + get_news_collection(): Collection
    + get_vectors_collection(): Collection
}

FastAPIApp --> AnalyzeRequest
FastAPIApp --> AnalyzeResponse
FastAPIApp --> VectorSearchService
VectorSearchService --> DatabaseConnection
@enduml
```

---

## ✅ Résumé

**Diagrammes recommandés** :
1. ✅ **Cas d'utilisation** : Montre l'interaction utilisateur-système
2. ✅ **Classe** : Structure des classes et relations
3. ✅ **Séquence** : Flux d'exécution d'une requête

**Entités principales** :
- **Utilisateur** (acteur unique, pas d'authentification)
- **Classes métier** : AnalyzeRequest, AnalyzeResponse, Article, VectorizedArticle
- **Services** : VectorSearchService, DatabaseConnection, LanguageDetector
- **Modèle ML** : EmbeddingModel (SentenceTransformer)

Ces diagrammes montrent clairement l'architecture de votre système sans nécessiter d'authentification ou de gestion d'utilisateurs complexes.

