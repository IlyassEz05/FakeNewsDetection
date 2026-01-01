#!/bin/bash
# Script de démarrage du serveur FastAPI

echo "🚀 Démarrage du serveur Fake News Detection API..."
echo "📡 Le serveur sera accessible sur http://localhost:8000"
echo "📖 Documentation API disponible sur http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

cd "$(dirname "$0")"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

