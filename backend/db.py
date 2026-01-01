"""
Module de connexion à MongoDB
Gère la connexion à la base de données MongoDB locale
"""
from pymongo import MongoClient
from typing import Optional

# Configuration de connexion MongoDB (local)
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "elbotola"  # Nom de la base de données
NEWS_COLLECTION_NAME = "wydad_news"  # Collection des actualités (3000 articles)
VECTORS_COLLECTION_NAME = "wydad_vector"  # Collection des vectorisations (6004 vectorisations - titres FR et EN)

# Client MongoDB global
_client: Optional[MongoClient] = None
_database = None
_news_collection = None
_vectors_collection = None


def get_client() -> MongoClient:
    """
    Retourne le client MongoDB (singleton)
    """
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_database():
    """
    Retourne la base de données MongoDB
    """
    global _database
    if _database is None:
        client = get_client()
        _database = client[DATABASE_NAME]
    return _database


def get_news_collection():
    """
    Retourne la collection des actualités (wydad_news)
    """
    global _news_collection
    if _news_collection is None:
        database = get_database()
        _news_collection = database[NEWS_COLLECTION_NAME]
    return _news_collection


def get_vectors_collection():
    """
    Retourne la collection des vectorisations
    """
    global _vectors_collection
    if _vectors_collection is None:
        database = get_database()
        _vectors_collection = database[VECTORS_COLLECTION_NAME]
    return _vectors_collection


def get_collection():
    """
    Retourne la collection des vectorisations (par défaut pour compatibilité)
    """
    return get_vectors_collection()


def close_connection():
    """
    Ferme la connexion MongoDB
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None

