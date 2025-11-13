# BrainFilter - Extension Chrome/Firefox

Extension de navigateur qui filtre intelligemment les vidéos YouTube selon l'heure et leur catégorie.

## Installation

### Chrome / Edge / Brave

1. Ouvrez Chrome et allez sur `chrome://extensions/`
2. Activez le "Mode développeur" (coin supérieur droit)
3. Cliquez sur "Charger l'extension non empaquetée"
4. Sélectionnez le dossier `extension/`
5. L'extension est maintenant installée !

### Firefox

1. Ouvrez Firefox et allez sur `about:debugging#/runtime/this-firefox`
2. Cliquez sur "Charger un module complémentaire temporaire"
3. Sélectionnez le fichier `manifest.json` dans le dossier `extension/`
4. L'extension est maintenant installée !

## Icônes manquantes

Pour le moment, les icônes ne sont pas incluses. Vous pouvez :

1. Créer vos propres icônes PNG (16x16, 48x48, 128x128) et les placer dans `extension/icons/`
2. Ou utiliser un outil comme https://www.favicon-generator.org/ pour générer des icônes à partir d'un logo

Nommez les fichiers :
- `icon16.png`
- `icon48.png`
- `icon128.png`

En attendant, l'extension fonctionnera sans icônes, mais avec un message d'avertissement.

## Utilisation

1. Cliquez sur l'icône de l'extension dans la barre d'outils
2. Configurez :
   - Activez/désactivez le filtrage
   - Définissez la plage horaire autorisée (ex: 20h-21h)
   - Sélectionnez les catégories à filtrer
3. Cliquez sur "Sauvegarder"
4. Naviguez sur YouTube - les vidéos indésirables seront automatiquement cachées !

## Catégories disponibles

- 🎮 Jeux vidéo
- 😂 Divertissement
- 📱 Shorts
- 🎵 Musique
- 🔢 Mathématiques
- 🔬 Sciences
- 📺 Documentaires
- 💭 Philosophie

## Comment ça marche ?

L'extension utilise un modèle de Machine Learning (TF-IDF + SVM) entraîné sur 1600 titres de vidéos YouTube pour classifier automatiquement chaque vidéo selon son titre.

Le modèle atteint **100% de précision** sur le jeu de validation avec un temps d'inférence de **0.03ms pour 1000 vidéos**.

## Structure des fichiers

```
extension/
├── manifest.json       # Configuration de l'extension
├── classifier.js       # Modèle de classification (TF-IDF + SVM)
├── content.js         # Script qui filtre les vidéos sur YouTube
├── popup.html         # Interface de configuration
├── popup.js           # Logique du popup
├── model.json         # Modèle ML exporté (1.6 MB)
└── icons/            # Icônes de l'extension
```

## Dépannage

### L'extension ne filtre pas les vidéos

1. Vérifiez que le filtrage est activé dans le popup
2. Vérifiez que vous n'êtes pas dans la plage horaire autorisée
3. Vérifiez que vous avez sélectionné des catégories à filtrer
4. Actualisez la page YouTube (F5)

### Les vidéos se chargent puis disparaissent

C'est normal ! L'extension analyse les titres des vidéos après leur chargement et les cache si elles correspondent aux catégories filtrées.

### Certaines vidéos ne sont pas filtrées correctement

Le modèle a été entraîné sur un dataset limité. Il peut parfois se tromper, surtout sur des titres ambigus ou en anglais.

## Développement

Pour modifier l'extension :

1. Modifiez les fichiers dans le dossier `extension/`
2. Rechargez l'extension dans `chrome://extensions/`
3. Actualisez la page YouTube pour tester les changements

## Limites connues

- Le modèle est optimisé pour les titres en français
- Taille du modèle : 1.6 MB (peut ralentir le chargement initial)
- Ne filtre pas les vidéos en cours de lecture
- Ne filtre pas dans les résultats de recherche (par design)
