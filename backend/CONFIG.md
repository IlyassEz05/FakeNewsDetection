# Configuration MongoDB

## Informations de connexion

- **Base de données** : `elbotola`
- **Collection des actualités** : `wydad_news` (3000 articles)
- **Collection des vectorisations** : `wydad_vector` (6004 vectorisations - titres FR et EN)

## Structure des données

### Collection wydad_vector (vectorisations)

Chaque document contient :
- `_id` : ObjectId
- `url` : string - URL de l'article (lien avec wydad_news)
- `language` : "fr" ou "en" - langue du titre vectorisé
- `text` : string - texte du titre vectorisé
- `embedding` : Array[384] - le vecteur d'embedding
- `created_at` : ISODate - date de création

### Collection wydad_news (actualités)

Chaque document contient :
- `_id` : ObjectId
- `title_ar` : string - titre en arabe
- `title_fr` : string - titre en français
- `title_en` : string - titre en anglais
- `url` : string - URL de l'article (lien avec wydad_vector)
- `pub_date` : number - date de publication
- `image` : string - URL de l'image
- `tags` : string - tags de l'article
- `scraped_at` : string - date de scraping

### Lien entre les collections

Les deux collections sont liées par le champ **`url`** (pas par `_id` ou `article_id`).

## Recherche Vectorielle

**Note importante** : Cette application utilise une recherche vectorielle manuelle (calcul de similarité cosinus en Python) car `$vectorSearch` n'est disponible que sur MongoDB Atlas, pas sur MongoDB local.

- **Méthode** : Calcul de similarité cosinus en Python avec NumPy
- **Champ vectoriel** : `embedding`
- **Dimensions** : 384
- **Similarité** : cosine

La recherche charge tous les embeddings et calcule la similarité pour chacun. Pour de meilleures performances avec de très grandes collections, considérez :
- Utiliser MongoDB Atlas avec `$vectorSearch`
- Implémenter un cache des embeddings
- Utiliser une bibliothèque d'indexation vectorielle comme FAISS

