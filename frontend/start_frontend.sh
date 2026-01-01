#!/bin/bash
# Script pour démarrer le serveur frontend

echo "🌐 Démarrage du serveur frontend..."
echo "📡 Le site web sera accessible sur http://localhost:8080"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8080

