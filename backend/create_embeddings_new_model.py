"""
Script pour recréer les embeddings avec un modèle multilingue plus performant
Ce script utilise paraphrase-multilingual-mpnet-base-v2 qui est beaucoup mieux pour le français

USAGE:
1. Sauvegardez votre collection wydad_vector actuelle (backup)
2. Videz wydad_vector: db.wydad_vector.deleteMany({})
3. Exécutez ce script: python3 create_embeddings_new_model.py
"""

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
from datetime import datetime

# -------------------------
# MongoDB
# -------------------------
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)

db = client["elbotola"]
source_collection = db["wydad_news"]
vector_collection = db["wydad_vector"]

# -------------------------
# Nouveau Modèle Multilingue Performant
# -------------------------
print("📦 Chargement du modèle multilingue performant...")
print("⚠️  Ce modèle est plus lent mais beaucoup plus précis pour le français")
print("   Temps estimé: ~10-15 minutes pour 3000 articles\n")

# Option 1: Très performant (768 dimensions)
model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

# Option 2: Bon compromis (384 dimensions, comme avant)
# model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

print(f"✅ Modèle chargé: {model.get_sentence_embedding_dimension()} dimensions\n")

# -------------------------
# Vérification
# -------------------------
existing_count = vector_collection.count_documents({})
if existing_count > 0:
    response = input(f"⚠️  La collection wydad_vector contient {existing_count} documents.\n"
                     "   Voulez-vous les supprimer et recréer? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        vector_collection.delete_many({})
        print("✅ Collection vidée\n")
    else:
        print("❌ Annulé. Les embeddings existants seront conservés.\n")
        exit()

# -------------------------
# Lecture des documents
# -------------------------
documents = list(source_collection.find())
print(f"🔎 {len(documents)} documents trouvés dans wydad_news\n")

inserted = 0
skipped = 0

for doc in tqdm(documents, desc="Création des embeddings"):
    url = doc.get("url")

    # Éviter les doublons (au cas où)
    if vector_collection.find_one({"url": url}):
        skipped += 1
        continue

    texts = []

    if doc.get("title_fr"):
        texts.append(("fr", doc["title_fr"]))

    if doc.get("title_en"):
        texts.append(("en", doc["title_en"]))

    for lang, text in texts:
        # Générer l'embedding avec le nouveau modèle
        embedding = model.encode(text, show_progress_bar=False).tolist()

        vector_doc = {
            "url": url,
            "language": lang,
            "text": text,
            "embedding": embedding,
            "created_at": datetime.utcnow()
        }

        vector_collection.insert_one(vector_doc)
        inserted += 1

print(f"\n✅ {inserted} vecteurs créés avec le nouveau modèle")
print(f"⏭️  {skipped} documents ignorés (doublons)")
print(f"\n📝 N'oubliez pas de mettre à jour MODEL_NAME dans vector_search.py !")

