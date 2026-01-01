"""
Module de recherche vectorielle
Gère la génération d'embeddings et la recherche vectorielle dans MongoDB
Note: Utilise une recherche vectorielle manuelle (calcul de similarité cosinus) 
      car $vectorSearch n'est disponible que sur MongoDB Atlas
"""
from sentence_transformers import SentenceTransformer
from langdetect import detect
from typing import Tuple, List, Dict, Any, Set
import numpy as np
import re
import db

# Modèle sentence-transformers pour générer les embeddings
# IMPORTANT: Ce modèle DOIT être exactement le même que celui utilisé pour créer les embeddings dans MongoDB
# 
# PROBLÈME: all-MiniLM-L6-v2 est principalement pour l'anglais et ne capture pas bien les nuances en français
# SOLUTION: Pour améliorer la précision, utilisez un modèle multilingue performant comme :
#   - paraphrase-multilingual-mpnet-base-v2 (768 dim, très performant)
#   - paraphrase-multilingual-MiniLM-L12-v2 (384 dim, bon compromis)
# 
# Note: Si vous changez de modèle, vous DEVEZ recréer tous les embeddings dans wydad_vector
MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dimensions, modèle anglais (limité pour le français)

# Instance globale du modèle (chargé une seule fois)
_model: SentenceTransformer = None


def get_model() -> SentenceTransformer:
    """
    Retourne le modèle sentence-transformers (singleton)
    Le modèle est chargé une seule fois pour optimiser les performances
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


# Dictionnaires pour l'extraction d'entités
KNOWN_PLAYERS = {
    'hakim ziyech', 'ziyech', 'aziz ki',
    'Noureddine Amrabat', 'Mouad Aounzo', 'Lorch','Hamza Hannouri',
    'Ferreira','mohamed Moufid','Ayoub Boucheta','Amine Aboulfath','mehdi benabid', 'Joseph Bakassu',
    'Abdelghafour Lamirate','Walid Sebbar', 'Oussama Zemraoui','Mohamed Amine Benhachem', 
    'Bouchouari','Bart', 'Rhulani Mokwena','Nassim Chadli','Walid Nassi','Tumisang','Youssef Motie'
}

KNOWN_CLUBS = {
    'wydad', 'wydad casablanca', 'wac', 'raja', 'raja casablanca',
    'fath', 'fath rabat', 'difaa', 'difaa el jadida', 'rca', 'olympique',
    'as far', 'far rabat', 'moghreb tetouan', 'irt', 'rsb'
}

# Actions clés en français et anglais
ACTION_KEYWORDS = {
    'fr': {'signé', 'signer', 'rejoint', 'arrivé', 'transfert', 'recruté', 
           'début', 'première', 'premier match', 'buteur', 'but', 'buts',
           'victoire', 'gagné', 'gagner', 'défaite', 'perdu', 'perdre',
           'blessé', 'blessure', 'suspendu', 'carton', 'rouge', 'jaune',
           'derby', 'classique', 'match', 'rencontre'},
    'en': {'signed', 'sign', 'joined', 'joined', 'transfer', 'transfered',
           'debut', 'first', 'first match', 'scorer', 'goal', 'goals',
           'victory', 'won', 'win', 'defeat', 'lost', 'lose',
           'injured', 'injury', 'suspended', 'card', 'red', 'yellow',
           'derby', 'match', 'game'}
}


def extract_entities(text: str, language: str = 'fr') -> Dict[str, Set[str]]:
    """
    Extrait les entités (joueurs, clubs, actions) d'un texte
    
    Args:
        text: Le texte à analyser
        language: Langue du texte ('fr' ou 'en')
        
    Returns:
        Dictionnaire avec 'players', 'clubs', 'actions'
    """
    text_lower = text.lower()
    
    # Extraction des joueurs
    players = set()
    for player in KNOWN_PLAYERS:
        if player in text_lower:
            players.add(player)
    
    # Extraction des clubs
    clubs = set()
    for club in KNOWN_CLUBS:
        if club in text_lower:
            clubs.add(club)
    
    # Extraction des actions
    actions = set()
    keywords = ACTION_KEYWORDS.get(language, ACTION_KEYWORDS['fr'])
    for keyword in keywords:
        # Recherche avec word boundaries pour éviter les faux positifs
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            actions.add(keyword)
    
    return {
        'players': players,
        'clubs': clubs,
        'actions': actions
    }


def calculate_entity_match_score(query_entities: Dict[str, Set[str]], 
                                 doc_entities: Dict[str, Set[str]]) -> float:
    """
    Calcule un score de correspondance entre les entités
    
    Args:
        query_entities: Entités extraites de la requête
        doc_entities: Entités extraites du document
        
    Returns:
        Score entre 0 et 1
    """
    score = 0.0
    total_weight = 0.0
    
    # Score pour les joueurs (poids élevé)
    if query_entities['players']:
        player_intersection = query_entities['players'] & doc_entities['players']
        player_union = query_entities['players'] | doc_entities['players']
        if player_union:
            player_score = len(player_intersection) / len(player_union)
            score += player_score * 0.5  # Poids 0.5
            total_weight += 0.5
    
    # Score pour les clubs (poids élevé)
    if query_entities['clubs']:
        club_intersection = query_entities['clubs'] & doc_entities['clubs']
        club_union = query_entities['clubs'] | doc_entities['clubs']
        if club_union:
            club_score = len(club_intersection) / len(club_union)
            score += club_score * 0.3  # Poids 0.3
            total_weight += 0.3
    
    # Score pour les actions (poids moyen)
    if query_entities['actions']:
        action_intersection = query_entities['actions'] & doc_entities['actions']
        action_union = query_entities['actions'] | doc_entities['actions']
        if action_union:
            action_score = len(action_intersection) / len(action_union)
            score += action_score * 0.2  # Poids 0.2
            total_weight += 0.2
    
    # Normaliser le score
    if total_weight > 0:
        return score / total_weight
    return 0.0


def calculate_keyword_overlap_score(query_text: str, doc_text: str) -> float:
    """
    Calcule un score de chevauchement de mots-clés simples
    
    Args:
        query_text: Texte de la requête
        doc_text: Texte du document
        
    Returns:
        Score entre 0 et 1
    """
    # Tokeniser en mots (simple)
    query_words = set(re.findall(r'\b\w+\b', query_text.lower()))
    doc_words = set(re.findall(r'\b\w+\b', doc_text.lower()))
    
    # Mots communs (exclure les mots trop courts et trop communs)
    stopwords = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'a', 'à', 
                 'un', 'une', 'pour', 'avec', 'dans', 'sur', 'the', 'a', 'an',
                 'and', 'or', 'for', 'with', 'in', 'on', 'at', 'to', 'of'}
    
    query_words = {w for w in query_words if len(w) > 2 and w not in stopwords}
    doc_words = {w for w in doc_words if len(w) > 2 and w not in stopwords}
    
    if not query_words:
        return 0.0
    
    intersection = query_words & doc_words
    overlap_score = len(intersection) / len(query_words)
    
    return min(1.0, overlap_score)


def re_rank_results(results: List[Dict[str, Any]], 
                   query_text: str, 
                   query_entities: Dict[str, Set[str]],
                   language: str) -> List[Dict[str, Any]]:
    """
    Re-classe les résultats avec un score hybride
    
    Args:
        results: Liste de résultats avec scores cosine
        query_text: Texte de la requête originale
        query_entities: Entités extraites de la requête
        language: Langue du texte
        
    Returns:
        Liste de résultats re-classés avec score_final
    """
    re_ranked = []
    
    for result in results:
        cosine_score = result.get('score', 0.0)
        doc_text = result.get('text', '')
        
        # Extraire les entités du document
        doc_entities = extract_entities(doc_text, language)
        
        # Calculer les scores
        entity_score = calculate_entity_match_score(query_entities, doc_entities)
        keyword_score = calculate_keyword_overlap_score(query_text, doc_text)
        
        # Score hybride final selon la formule demandée
        # 0.6 * cosine + 0.3 * entity + 0.1 * keyword
        # S'assurer que cosine_score est entre 0 et 1 (les scores de similarité cosinus sont généralement entre -1 et 1)
        # Normaliser pour être entre 0 et 1: (score + 1) / 2, ou simplement max(0, score)
        cosine_normalized = max(0.0, min(1.0, cosine_score))  # Clamper entre 0 et 1
        
        hybrid_score = (
            0.6 * cosine_normalized +
            0.3 * entity_score +
            0.1 * keyword_score
        )
        
        # S'assurer que le score final est bien entre 0 et 1
        hybrid_score = max(0.0, min(1.0, hybrid_score))
        
        # Ajouter le score final au résultat
        result['score_final'] = hybrid_score
        result['score_cosine'] = cosine_score  # Score original (pour debug)
        result['score_entity'] = entity_score
        result['score_keyword'] = keyword_score
        
        re_ranked.append(result)
    
    # Trier par score final décroissant
    re_ranked.sort(key=lambda x: x.get('score_final', 0.0), reverse=True)
    
    return re_ranked


def detect_language(text: str) -> str:
    """
    Détecte la langue du texte (français ou anglais)
    
    Args:
        text: Le texte à analyser
        
    Returns:
        "fr" ou "en"
    """
    try:
        lang = detect(text)
        # Normaliser les codes de langue
        if lang in ["fr", "fr-FR"]:
            return "fr"
        elif lang in ["en", "en-US", "en-GB"]:
            return "en"
        else:
            # Par défaut, on considère que c'est français ou anglais
            # On peut améliorer cette logique selon les besoins
            return "fr" if any(char in text for char in "àâäéèêëïîôùûüÿç") else "en"
    except Exception:
        # En cas d'erreur, on essaie une détection basique
        return "fr" if any(char in text for char in "àâäéèêëïîôùûüÿç") else "en"


def generate_embedding(text: str, normalize: bool = False) -> List[float]:
    """
    Génère un embedding vectoriel pour le texte donné
    
    Args:
        text: Le texte à encoder
        normalize: Si True, normalise l'embedding (pour améliorer la similarité cosinus)
        
    Returns:
        Liste de 384 floats représentant l'embedding
    """
    model = get_model()
    # Optimisation: utiliser show_progress_bar=False pour plus de rapidité
    # Normaliser les embeddings peut améliorer la précision de la similarité cosinus
    embedding = model.encode(
        text, 
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=normalize
    )
    return embedding.tolist()


def normalize_vector(vec: np.ndarray) -> np.ndarray:
    """
    Normalise un vecteur pour améliorer la similarité cosinus
    
    Args:
        vec: Vecteur à normaliser
        
    Returns:
        Vecteur normalisé
    """
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def cosine_similarity(vec1: List[float], vec2: List[float], normalize: bool = True) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs
    
    Args:
        vec1: Premier vecteur
        vec2: Deuxième vecteur
        normalize: Si True, normalise les vecteurs avant le calcul
        
    Returns:
        Score de similarité cosinus (entre -1 et 1, généralement entre 0 et 1 pour des embeddings)
    """
    vec1_array = np.array(vec1, dtype=np.float32)
    vec2_array = np.array(vec2, dtype=np.float32)
    
    # Normaliser les vecteurs pour améliorer la précision de la similarité cosinus
    if normalize:
        vec1_array = normalize_vector(vec1_array)
        vec2_array = normalize_vector(vec2_array)
    
    # Calcul de la similarité cosinus
    dot_product = np.dot(vec1_array, vec2_array)
    
    # Si les vecteurs sont déjà normalisés, le produit scalaire est directement la similarité
    if normalize:
        return float(np.clip(dot_product, -1.0, 1.0))
    
    # Sinon, calculer avec les normes
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.clip(dot_product / (norm1 * norm2), -1.0, 1.0))


def vector_search(query_embedding: List[float], limit: int = 3, language_filter: str = None, min_score: float = 0.0) -> List[Dict[str, Any]]:
    """
    Effectue une recherche vectorielle dans MongoDB local
    Utilise un calcul manuel de similarité cosinus car $vectorSearch n'est disponible que sur Atlas
    
    Recherche dans la collection de vectorisations (wydad_vector)
    Le lien avec wydad_news se fait par le champ 'url'
    
    Structure:
    - Collection wydad_vector: contient les embeddings avec url, text, language
    - Collection wydad_news: contient les articles complets (liés par url)
    
    Args:
        query_embedding: L'embedding de la requête (384 dimensions)
        limit: Nombre de résultats à retourner (par défaut 3)
        language_filter: Filtrer par langue ("fr" ou "en"), None pour toutes les langues
        min_score: Score minimum pour inclure un résultat (par défaut 0.0)
        
    Returns:
        Liste de documents correspondants avec leurs scores de similarité
    """
    vectors_collection = db.get_vectors_collection()
    news_collection = db.get_news_collection()
    
    # Construire le filtre MongoDB
    mongo_filter = {}
    if language_filter:
        mongo_filter["language"] = language_filter
    
    # Récupérer tous les documents de vectorisation (filtrés par langue si demandé)
    all_vectors = list(vectors_collection.find(
        mongo_filter,
        {"_id": 1, "url": 1, "language": 1, "text": 1, "embedding": 1, "created_at": 1}
    ))
    
    if not all_vectors:
        return []
    
    # Convertir query_embedding en numpy array
    query_array = np.array(query_embedding, dtype=np.float32)
    
    # Calculer la similarité cosinus pour chaque embedding
    # Note: On ne normalise PAS pour rester cohérent avec les embeddings existants
    # qui peuvent ne pas être normalisés dans la base de données
    query_norm = np.linalg.norm(query_array)
    if query_norm == 0:
        return []
    
    scored_docs = []
    for doc in all_vectors:
        doc_embedding = doc.get("embedding")
        if doc_embedding and len(doc_embedding) == len(query_embedding):
            doc_array = np.array(doc_embedding, dtype=np.float32)
            doc_norm = np.linalg.norm(doc_array)
            
            if doc_norm > 0:
                # Calcul de similarité cosinus standard (sans normalisation préalable)
                score = float(np.dot(query_array, doc_array) / (query_norm * doc_norm))
                
                # Filtrer les scores trop bas
                if score >= min_score:
                    scored_docs.append((score, doc))
    
    # Trier par score décroissant et prendre les meilleurs résultats
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_docs[:limit]
    
    # Construire les résultats finaux avec lookup vers wydad_news
    results = []
    for score, doc in top_results:
        url = doc.get("url")
        
        # Faire le lookup vers wydad_news
        article = None
        if url:
            article = news_collection.find_one({"url": url})
        
        # Construire le document de résultat
        result_doc = {
            "_id": doc.get("_id"),
            "score": score,
            "language": doc.get("language"),
            "text": doc.get("text", ""),
            "url": url,
            "created_at": doc.get("created_at")
        }
        
        # Ajouter les informations de l'article si trouvé
        if article:
            result_doc["title_fr"] = article.get("title_fr")
            result_doc["title_en"] = article.get("title_en")
            result_doc["title_ar"] = article.get("title_ar")
            result_doc["image"] = article.get("image")
        
        results.append(result_doc)
    
    return results


def find_closest_article(user_text: str, language: str = None) -> Tuple[Dict[str, Any], float]:
    """
    Trouve l'article le plus proche du texte utilisateur avec re-ranking hybride
    
    Processus:
    1. Recherche TOP-K (20) par similarité cosinus
    2. Extraction d'entités (joueurs, clubs, actions)
    3. Re-ranking avec score hybride (cosine + entity + keyword)
    4. Retourne le meilleur résultat
    
    Args:
        user_text: Le texte de l'utilisateur à analyser
        language: Langue du texte ("fr" ou "en") pour filtrer les résultats, None pour toutes les langues
        
    Returns:
        Tuple contenant:
        - Le document le plus proche (dict avec score_final)
        - Le score final hybride (float entre 0 et 1)
    """
    # Générer l'embedding du texte utilisateur
    query_embedding = generate_embedding(user_text, normalize=False)
    
    # Déterminer la langue si non fournie
    if language is None:
        language = detect_language(user_text)
    
    # Étape 1: Recherche TOP-K par similarité cosinus (20 résultats)
    top_k = 20
    cosine_results = vector_search(query_embedding, limit=top_k, language_filter=language, min_score=-1.0)
    
    # Si pas de résultats avec le filtre de langue, essayer sans filtre
    if not cosine_results:
        cosine_results = vector_search(query_embedding, limit=top_k, language_filter=None, min_score=-1.0)
    
    if not cosine_results:
        raise ValueError("Aucun article trouvé dans la base de données")
    
    # Étape 2: Extraction d'entités de la requête
    query_entities = extract_entities(user_text, language)
    
    # Étape 3: Re-ranking avec score hybride
    re_ranked_results = re_rank_results(cosine_results, user_text, query_entities, language)
    
    # Étape 4: Retourner le meilleur résultat
    closest = re_ranked_results[0]
    final_score = closest.get('score_final', closest.get('score', 0.0))
    
    return closest, final_score

