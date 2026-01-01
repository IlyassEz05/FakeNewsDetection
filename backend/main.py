"""
Application FastAPI principale
Endpoint pour l'analyse de fausses nouvelles
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import vector_search
import db

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Fake News Detection API",
    description="API pour la détection de fausses nouvelles par similarité sémantique",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modèle de requête
class AnalyzeRequest(BaseModel):
    text: str


# Modèle de réponse
class AnalyzeResponse(BaseModel):
    verdict: str
    score: float
    closest_article: str
    source_url: str
    language: str


def get_verdict(score: float) -> str:
    """
    Détermine le verdict basé sur le score final hybride
    
    Args:
        score: Score final hybride (entre 0 et 1)
        
    Returns:
        Verdict en français
    """
    # Seuils de décision ajustés
    if score > 0.60:
        return "Information probablement vraie"
    elif score >= 0.40:
        return "Information incertaine"
    else:
        return "Information probablement fausse"


@app.get("/")
async def root():
    """
    Endpoint de test pour vérifier que l'API fonctionne
    """
    return {
        "message": "Fake News Detection API",
        "status": "running",
        "endpoint": "/analyze"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyse un texte pour détecter s'il s'agit de fausses nouvelles
    
    Args:
        request: Objet contenant le texte à analyser
        
    Returns:
        Réponse avec le verdict, le score, l'article le plus proche, etc.
    """
    try:
        # Vérifier que le texte n'est pas vide
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Le texte ne peut pas être vide"
            )
        
        user_text = request.text.strip()
        
        # Détecter la langue du texte
        language = vector_search.detect_language(user_text)
        
        # Trouver l'article le plus proche (avec filtre de langue pour plus de précision)
        closest_doc, score = vector_search.find_closest_article(user_text, language=language)
        
        # Déterminer le verdict basé sur le score final hybride
        # Le score est déjà entre 0 et 1 (score hybride)
        display_score = max(0.0, min(1.0, score))
        
        verdict = get_verdict(display_score)
        
        # Construire la réponse
        response = AnalyzeResponse(
            verdict=verdict,
            score=round(display_score, 4),  # Score final hybride arrondi à 4 décimales
            closest_article=closest_doc.get("text", ""),
            source_url=closest_doc.get("url", ""),
            language=language
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """
    Précharge le modèle sentence-transformers au démarrage
    pour éviter le délai lors du premier appel
    """
    print("🔄 Préchargement du modèle sentence-transformers...")
    try:
        # Précharger le modèle pour éviter le délai au premier appel
        vector_search.get_model()
        print("✅ Modèle chargé avec succès")
    except Exception as e:
        print(f"⚠️  Erreur lors du préchargement du modèle: {e}")
        print("   Le modèle sera chargé à la demande lors du premier appel")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Ferme la connexion MongoDB à l'arrêt de l'application
    """
    db.close_connection()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

