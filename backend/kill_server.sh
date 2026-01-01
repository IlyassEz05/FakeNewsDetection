#!/bin/bash
# Script pour arrêter le serveur sur le port 8000

PORT=8000
PID=$(lsof -ti:$PORT)

if [ -z "$PID" ]; then
    echo "Aucun processus n'utilise le port $PORT"
else
    echo "Arrêt du processus $PID sur le port $PORT..."
    kill -9 $PID 2>/dev/null
    echo "✅ Serveur arrêté"
fi

