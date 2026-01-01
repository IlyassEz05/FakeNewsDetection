#!/bin/bash
# Script pour démarrer le backend et le frontend ensemble

echo "🚀 Démarrage de l'application Fake News Detection"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "🌐 Site Web: http://localhost:8080"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"
echo ""

# Dossier du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Fonction pour arrêter les processus à la sortie
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Démarrer le backend
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Attendre un peu pour que le backend démarre
sleep 2

# Démarrer le frontend
cd "$SCRIPT_DIR/frontend"
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "✅ Serveurs démarrés !"
echo "🌐 Ouvrez http://localhost:8080 dans votre navigateur"
echo ""

# Attendre que les processus se terminent
wait

