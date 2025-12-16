# Scraper Keur-Immo.com - Version Complète

Un système de scraping avancé pour extraire **tous les détails** des propriétés immobilières du site keur-immo.com au Sénégal.

## 🚀 Fonctionnalités

### Extraction Complète
- **Données de base** : titre, prix, localisation, surface, description
- **Détails avancés** : coordonnées GPS, galerie d'images, informations légales
- **Contact** : agent, téléphone, email
- **Métadonnées** : date de publication, dernière mise à jour, ID unique
- **Caractéristiques** : viabilisation, titre foncier, équipements
- **Analyse qualité** : score de complétude des données (0-100%)

### Formats de Sortie
- **JSON** : données complètes avec structure hiérarchique
- **CSV** : format tabulaire pour analyse
- **Excel** : fichier multi-feuilles avec statistiques

### Intelligence Artificielle
- **Extraction adaptative** : s'adapte automatiquement à la structure du site
- **Recherche multi-sélecteurs** : utilise plusieurs stratégies pour trouver les données
- **Extraction numérique** : convertit automatiquement prix et surfaces en nombres
- **Détection de pagination** : trouve automatiquement toutes les pages

## 📦 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Ou installer manuellement
pip install requests beautifulsoup4 lxml pandas openpyxl
```

## 🎯 Utilisation

### 1. Scraper Simple (Recommandé pour débuter)

```bash
# Test de la structure du site
python test_scraper.py

# Scraping basique
python keur_immo_scraper.py

# Scraping sans détails complets (plus rapide)
python keur_immo_scraper.py --no-details

# Limiter le nombre de propriétés
python keur_immo_scraper.py --max-properties 50
```

### 2. Scraper Avancé (Extraction Maximale)

```bash
# Terrains à Dakar (par défaut)
python advanced_scraper.py

# Autres types de propriétés
python advanced_scraper.py --type maisons_dakar
python advanced_scraper.py --type appartements_dakar
python advanced_scraper.py --type terrains_thies
python advanced_scraper.py --type terrains_senegal

# Options avancées
python advanced_scraper.py --max 100 --no-details
```

## 📊 Types de Données Extraites

### Informations de Base
```json
{
  "titre": "Terrain de 500m² à Almadies",
  "prix_texte": "75 000 000 FCFA",
  "prix_numerique": 75000000,
  "localisation": "Almadies, Dakar",
  "surface_texte": "500 m²",
  "surface_numerique": 500.0,
  "description": "Beau terrain viabilisé..."
}
```

### Détails Complets
```json
{
  "images": ["https://keur-immo.com/img1.jpg", "..."],
  "nombre_images": 5,
  "caracteristiques": ["viabilisé", "titre foncier", "électricité"],
  "coordonnees": {"latitude": "14.7167", "longitude": "-17.4677"},
  "contact_detaille": {
    "nom_agent": "Amadou Diallo",
    "telephone_agent": "+221 77 123 45 67",
    "email_agent": "agent@keur-immo.com"
  },
  "informations_legales": {
    "titre foncier": ["Titre foncier disponible"],
    "zone": ["Zone résidentielle R2"]
  },
  "qualite_donnees": 85
}
```

### Métadonnées
```json
{
  "id_unique": "terrain_500m_almadies_dakar",
  "timestamp_scraping": "2024-12-10T15:30:00",
  "source_url": "https://keur-immo.com/senegal/terrains-a-vendre-dakar/",
  "type_recherche": "terrains_dakar",
  "est_page_detail": true,
  "qualite_donnees": 85
}
```

## ⚙️ Configuration

Le fichier `config.py` permet de personnaliser :

- **URLs cibles** : différents types de propriétés
- **Sélecteurs CSS** : adaptation à la structure du site
- **Mots-clés** : extraction intelligente par contenu
- **Paramètres de scraping** : délais, retry, limites
- **Formats de sortie** : noms des fichiers

## 📁 Fichiers Générés

```
keur_immo_terrains_complet.json    # Données complètes JSON
keur_immo_terrains_complet.csv     # Format tabulaire
keur_immo_terrains_complet.xlsx    # Excel multi-feuilles
page_sample.html                   # Échantillon HTML pour debug
scraping.log                       # Journal détaillé
```

## 🔧 Scripts Disponibles

| Script | Usage | Avantages |
|--------|-------|-----------|
| `test_scraper.py` | Test et analyse | Comprendre la structure du site |
| `keur_immo_scraper.py` | Scraping standard | Simple, fiable, bien documenté |
| `advanced_scraper.py` | Scraping maximal | Extraction complète, IA adaptative |
| `config.py` | Configuration | Personnalisation avancée |

## 📈 Analyse des Données

Le scraper génère automatiquement :

- **Statistiques de prix** : min, max, moyenne
- **Répartition géographique** : top des localisations
- **Analyse des surfaces** : distribution des tailles
- **Caractéristiques populaires** : équipements les plus fréquents
- **Score de qualité** : complétude des données par propriété

## 🚨 Bonnes Pratiques

### Respect du Site
- Délais entre requêtes (1-2 secondes)
- Retry automatique avec backoff exponentiel
- Headers HTTP réalistes
- Limitation du nombre de propriétés par session

### Gestion d'Erreurs
- Logging détaillé de toutes les opérations
- Sauvegarde des échantillons HTML pour debug
- Scores de qualité pour identifier les données incomplètes
- Continuation en cas d'erreur sur une propriété

### Performance
- Session HTTP réutilisée
- Évitement des doublons d'URLs
- Extraction adaptative selon la structure
- Formats de sortie optimisés

## 🛠️ Dépannage

### Aucune donnée récupérée
```bash
# 1. Tester la structure du site
python test_scraper.py

# 2. Vérifier les sélecteurs dans config.py
# 3. Examiner page_sample.html
# 4. Ajuster les sélecteurs CSS
```

### Données incomplètes
- Vérifier le score `qualite_donnees` dans les résultats
- Ajuster les sélecteurs dans `config.py`
- Utiliser `--no-details` pour tester plus rapidement

### Erreurs de connexion
- Vérifier la connexion internet
- Le site peut être temporairement indisponible
- Augmenter les délais dans `config.py`

## 📞 Support

Pour toute question ou amélioration :
1. Examiner les logs dans `scraping.log`
2. Vérifier la structure HTML dans `page_sample.html`
3. Ajuster la configuration dans `config.py`

## 🎯 Exemples d'Usage

```bash
# Scraping rapide pour test
python advanced_scraper.py --max 10 --no-details

# Extraction complète terrains Dakar
python advanced_scraper.py --type terrains_dakar

# Maisons avec tous les détails
python advanced_scraper.py --type maisons_dakar

# Analyse de tout le Sénégal (attention: très long)
python advanced_scraper.py --type terrains_senegal --max 500
```

Le système est conçu pour extraire **le maximum de détails possibles** tout en restant respectueux du site web et robuste face aux changements de structure.