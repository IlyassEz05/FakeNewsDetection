# ⚠️ IMPORTANT - Vérification du Modèle

## Problème de Précision

Si vous obtenez des résultats non pertinents (articles qui contiennent les mêmes mots mais pas le même sens), cela peut être dû à :

### 1. Modèle Différent

Le modèle utilisé pour générer les embeddings de la requête **DOIT être exactement le même** que celui utilisé pour créer les embeddings dans votre collection `wydad_vector`.

**Modèle actuellement configuré :**
- `all-MiniLM-L6-v2` (384 dimensions) ✅ CORRIGÉ pour correspondre à votre script

**Vérification :**
1. Ouvrez MongoDB Compass
2. Vérifiez un document dans `wydad_vector`
3. Regardez comment les embeddings ont été créés (dans votre script d'origine)
4. Vérifiez le nom exact du modèle utilisé

### 2. Comment Changer le Modèle

Si vos embeddings ont été créés avec un modèle différent, modifiez dans `backend/vector_search.py` :

```python
MODEL_NAME = "nom-du-modele-utilise"  # Remplacez par le nom exact
```

### 3. Modèles Recommandés pour le Français

Si vous devez changer de modèle, voici des alternatives :

- **`paraphrase-multilingual-MiniLM-L12-v2`** (actuel - 384 dim) - Rapide mais moins précis
- **`paraphrase-multilingual-mpnet-base-v2`** (768 dim) - Plus précis mais plus lent
- **`distiluse-base-multilingual-cased`** (512 dim) - Bon compromis

⚠️ **ATTENTION** : Si vous changez de modèle, vous devrez recréer TOUS les embeddings dans `wydad_vector` avec le nouveau modèle !

## Solution Alternative

Si vous ne pouvez pas changer de modèle, vous pouvez améliorer la recherche en :
1. Utilisant une recherche hybride (texte + sémantique)
2. Filtrant par mots-clés avant la recherche vectorielle
3. Utilisant un meilleur modèle d'embedding

