# 🚀 Guide de Démarrage - Application Web Fake News Detection

## Application Web Complète ✅

Vous avez une **application web complète** (pas seulement une API) avec :
- ✅ **Interface utilisateur** (site web)
- ✅ **API Backend** (FastAPI)
- ✅ **Base de données** (MongoDB)

## 📍 Comment Accéder au Site Web

### Option 1 : Démarrage Automatique (Recommandé)

Démarrez **les deux serveurs** (backend + frontend) en une seule commande :

```bash
cd /Users/ilyassez/Documents/fakenewsdetection
./start_all.sh
```

Puis ouvrez votre navigateur à l'adresse :
👉 **http://localhost:8080**

### Option 2 : Démarrage Manuel

**Terminal 1 - Backend :**
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend :**
```bash
cd frontend
python3 -m http.server 8080
```

Puis ouvrez votre navigateur à l'adresse :
👉 **http://localhost:8080**

### Option 3 : Scripts Individuels

**Backend :**
```bash
cd backend
./start_server.sh
```

**Frontend :**
```bash
cd frontend
./start_frontend.sh
```

Puis ouvrez votre navigateur à l'adresse :
👉 **http://localhost:8080**

## 🎯 Utilisation de l'Application Web

1. **Ouvrez** http://localhost:8080 dans votre navigateur
2. **Collez ou tapez** le texte que vous voulez vérifier
3. **Cliquez** sur le bouton "Analyser"
4. **Consultez** les résultats :
   - Verdict (vraie/douteuse/fausse)
   - Score de similarité
   - Article le plus proche trouvé
   - URL de la source

## 🔧 Arrêter les Serveurs

Pour arrêter les serveurs, appuyez sur **Ctrl+C** dans le terminal.

Ou utilisez le script d'arrêt pour le backend :
```bash
cd backend
./kill_server.sh
```

## 📝 Structure de l'Application

```
fakenewsdetection/
├── backend/          # API FastAPI (port 8000)
│   ├── main.py       # Serveur API
│   ├── db.py         # Connexion MongoDB
│   └── vector_search.py  # Recherche vectorielle
├── frontend/         # Site Web (port 8080)
│   ├── index.html    # Page principale
│   ├── style.css     # Styles
│   └── script.js     # Logique JavaScript
└── start_all.sh      # Script de démarrage complet
```

## ⚠️ Prérequis

- MongoDB doit être démarré localement
- Les deux serveurs (backend + frontend) doivent être en cours d'exécution

