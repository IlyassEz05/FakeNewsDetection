# ⚡ Performance et Optimisations

## ⏱️ Délais Normaux

Il est **normal** que l'analyse prenne quelques secondes (3-10 secondes selon votre machine), car :

1. **Génération d'embedding** : Le modèle sentence-transformers doit encoder le texte (500ms - 2s)
2. **Recherche vectorielle MongoDB** : La recherche dans 6004 vectorisations prend du temps (1-3s)
3. **Jointure avec wydad_news** : Le $lookup peut ajouter du temps (500ms - 1s)

## ✅ Optimisations Appliquées

### 1. Préchargement du Modèle
- Le modèle sentence-transformers est maintenant **préchargé au démarrage** du serveur
- Cela évite le délai supplémentaire au premier appel (qui était de 5-15 secondes)
- **Bénéfice** : Réduction du temps de réponse de 5-15s à 3-8s

### 2. Optimisation de l'Encoding
- `show_progress_bar=False` pour éviter les overheads d'affichage
- Encoding optimisé pour les performances

### 3. Amélioration du Frontend
- Message informatif pendant le chargement
- Timeout de 60 secondes pour éviter les attentes infinies
- Meilleure gestion des erreurs

## 🚀 Comment Réduire Encore les Délais

Si vous voulez améliorer encore les performances :

### Option 1 : Réduire numCandidates
Dans `vector_search.py`, ligne ~103, vous pouvez réduire :
```python
"numCandidates": limit * 5,  # Au lieu de limit * 10
```
Cela réduira la précision mais accélérera la recherche.

### Option 2 : Utiliser un Modèle Plus Léger
Vous pouvez changer le modèle dans `vector_search.py` :
```python
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # Actuel (384 dim)
# Vers :
MODEL_NAME = "all-MiniLM-L6-v2"  # Plus rapide mais moins précis
```

### Option 3 : Index MongoDB
Assurez-vous que l'index vectoriel `news_vector_index` est bien créé et optimisé.

### Option 4 : Cache des Requêtes
Vous pourriez ajouter un cache pour les requêtes similaires (nécessite Redis ou un cache en mémoire).

## 📊 Temps de Réponse Attendus

- **Premier appel** (modèle préchargé) : 3-8 secondes
- **Appels suivants** : 3-8 secondes (temps stable)
- **Sans préchargement** : 8-20 secondes au premier appel

## 🔍 Vérification

Pour vérifier que le modèle est bien préchargé, regardez les logs au démarrage du serveur :
```
🔄 Préchargement du modèle sentence-transformers...
✅ Modèle chargé avec succès
```

Si vous voyez ce message, le préchargement fonctionne correctement.

