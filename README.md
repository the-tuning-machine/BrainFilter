# BrainFilter - Extension de filtrage YouTube intelligente

Extension de navigateur qui filtre automatiquement les vidéos YouTube en fonction de l'heure et de leur catégorie, en utilisant un modèle de Machine Learning.

## 🎯 Objectif

Vous aider à rester concentré en filtrant automatiquement les contenus distrayants (jeux, divertissement, shorts) pendant vos heures productives, tout en vous autorisant ces contenus pendant vos moments de détente (ex: 20h-21h).

## ✨ Fonctionnalités

- **Filtrage par heure** : Autorise certains contenus uniquement pendant les heures définies
- **Classification intelligente** : Catégorise automatiquement les vidéos par titre avec un modèle ML
- **Filtrage contextuel** : Active uniquement sur la page d'accueil et les recommandations
- **Pas de filtrage lors de recherches** : Vos recherches spécifiques ne sont jamais filtrées
- **Interface intuitive** : Configuration simple via popup

## 📊 Performance du modèle

Le modèle de classification (TF-IDF + SVM Linear) atteint :
- ✅ **100% de précision** sur le jeu de validation
- ⚡ **0.03ms pour 1000 vidéos** (temps d'inférence)
- 📦 **1.6 MB** (taille du modèle)
- 🎓 **Entraîné sur 1600 titres** répartis en 8 catégories

## 🗂️ Catégories disponibles

- 🎮 Jeux vidéo
- 😂 Divertissement
- 📱 Shorts
- 🎵 Musique
- 🔢 Mathématiques
- 🔬 Sciences
- 📺 Documentaires
- 💭 Philosophie

## 🚀 Installation rapide

### 1. Installer l'extension

**Chrome / Edge / Brave:**
```bash
# Ouvrir chrome://extensions/
# Activer "Mode développeur"
# Cliquer "Charger l'extension non empaquetée"
# Sélectionner le dossier "extension/"
```

**Firefox:**
```bash
# Ouvrir about:debugging#/runtime/this-firefox
# Cliquer "Charger un module complémentaire temporaire"
# Sélectionner manifest.json dans "extension/"
```

### 2. Configurer

1. Cliquez sur l'icône BrainFilter dans la barre d'outils
2. Activez le filtrage
3. Définissez votre plage horaire autorisée (ex: 20h-21h)
4. Sélectionnez les catégories à filtrer (recommandé : jeux, divertissement, shorts)
5. Cliquez sur "Sauvegarder"

C'est tout ! Les vidéos indésirables seront automatiquement cachées sur YouTube.

## 📁 Structure du projet

```
BrainFilter/
├── extension/              # Extension navigateur
│   ├── manifest.json       # Configuration
│   ├── classifier.js       # Modèle ML en JavaScript
│   ├── content.js         # Script de filtrage
│   ├── popup.html/js      # Interface de configuration
│   ├── model.json         # Modèle exporté (1.6 MB)
│   └── icons/             # Icônes
├── ml/                    # Machine Learning
│   ├── dataset/           # Génération du dataset
│   │   └── generate_dataset.py
│   ├── models/            # Modèles et entraînement
│   │   ├── embeddings.py
│   │   ├── test_all_models.py
│   │   └── export_simple_model.py
│   └── evaluation/        # Évaluation et benchmark
│       └── benchmark.py
├── data/                  # Données générées
│   ├── raw/               # Dataset brut (1600 titres)
│   ├── evaluation_results/ # Résultats du benchmark
│   └── models/            # Modèles Python sauvegardés
├── requirements.txt       # Dépendances Python
└── README.md             # Ce fichier
```

## 🔬 Approche Machine Learning

### 1. Génération du dataset

Script : `ml/dataset/generate_dataset.py`

- **1600 titres** générés automatiquement
- **200 titres par catégorie** (équilibré)
- Templates réalistes basés sur de vrais titres YouTube
- Support du français

### 2. Benchmark de modèles

Script : `ml/models/test_all_models.py`

**42 combinaisons testées :**
- **Embeddings** : TF-IDF (500, 1000, 2000 features), BOW, Keywords, Hybrid
- **Classificateurs** : KNN (k=5, 10, 15), SVM (Linear, RBF), GMM (2, 3 composantes)

**Métriques mesurées :**
- Accuracy, F1 Score (macro et weighted)
- Temps d'entraînement
- Temps d'inférence (total et par échantillon)

### 3. Résultats

**Top 3 modèles :**

| Modèle | Accuracy | Temps inférence (1000 samples) |
|--------|----------|-------------------------------|
| TF-IDF-500 + SVM-Linear | 100% | 0.030ms ⚡ |
| TF-IDF-500 + SVM-RBF | 100% | 0.097ms |
| TF-IDF-500 + KNN-15-weighted | 99.7% | 0.023ms |

**Modèle sélectionné : TF-IDF-500 + SVM-Linear**
- Performance parfaite
- Le plus rapide parmi les modèles à 100%
- Taille raisonnable (1.6 MB après export JSON)

### 4. Export et intégration

Script : `ml/models/export_simple_model.py`

Le modèle Python (scikit-learn) est exporté en JSON avec :
- Vocabulaire TF-IDF (500 mots/n-grams)
- Valeurs IDF
- Support vectors du SVM
- Coefficients duaux
- Intercepts

Puis réimplémenté en JavaScript pur dans `extension/classifier.js` pour fonctionner dans le navigateur sans dépendances externes.

## 🛠️ Développement

### Prérequis

```bash
python3 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

### Regénérer le dataset

```bash
python ml/dataset/generate_dataset.py
```

### Relancer le benchmark

```bash
python ml/models/test_all_models.py
```

Les résultats seront dans `data/evaluation_results/` :
- `benchmark_results.csv` : Tableau comparatif
- `model_comparison.png` : Graphiques
- `confusion_matrix_*.png` : Matrices de confusion

### Réentraîner et exporter le modèle

```bash
python ml/models/export_simple_model.py
```

Le modèle sera sauvegardé dans `extension/model.json`.

### Modifier l'extension

1. Éditez les fichiers dans `extension/`
2. Rechargez l'extension dans le navigateur
3. Actualisez YouTube pour tester

## 🐛 Dépannage

**L'extension ne filtre pas :**
- Vérifiez que le filtrage est activé
- Vérifiez que vous n'êtes pas dans la plage horaire autorisée
- Vérifiez les catégories sélectionnées
- Actualisez la page (F5)

**Mauvaise classification :**
- Le modèle est optimisé pour le français
- Les titres ambigus peuvent être mal classés
- Vous pouvez régénérer le dataset avec plus d'exemples

**Extension trop lente :**
- Le modèle (1.6 MB) peut prendre quelques secondes à charger
- Une fois chargé, l'inférence est quasi-instantanée

## 📈 Améliorations possibles

- [ ] Support multilingue (anglais, espagnol, etc.)
- [ ] Dataset plus large (10k+ titres)
- [ ] Analyse des miniatures en plus des titres
- [ ] Mode "liste blanche" (autoriser uniquement certaines catégories)
- [ ] Statistiques de filtrage détaillées
- [ ] Synchronisation des paramètres entre appareils
- [ ] Optimisation de la taille du modèle (compression, quantization)

## 📝 Licence

Ce projet est à but éducatif. Utilisez-le librement !
