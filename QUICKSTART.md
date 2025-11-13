# 🚀 Guide de démarrage rapide - BrainFilter

## Installation en 5 minutes

### Étape 1 : Vérifier les fichiers

Assurez-vous que vous avez tous les fichiers nécessaires :

```bash
cd BrainFilter
ls extension/
```

Vous devriez voir :
- ✅ `manifest.json`
- ✅ `model.json` (1.6 MB)
- ✅ `classifier.js`
- ✅ `content.js`
- ✅ `popup.html` et `popup.js`
- ✅ `icons/` (avec icon16.png, icon48.png, icon128.png)

### Étape 2 : Installer l'extension dans Chrome

1. Ouvrez Chrome
2. Tapez `chrome://extensions/` dans la barre d'adresse
3. Activez le **"Mode développeur"** (toggle en haut à droite)
4. Cliquez sur **"Charger l'extension non empaquetée"**
5. Sélectionnez le dossier `BrainFilter/extension/`
6. L'extension est installée ! 🎉

### Étape 3 : Configurer

1. Cliquez sur l'icône BrainFilter (🅱️ bleu) dans la barre d'outils
2. Dans le popup :
   - ✅ Activez le filtrage (toggle en haut)
   - ⏰ Définissez votre plage horaire autorisée (ex: 20 à 21)
   - 📂 Sélectionnez les catégories à filtrer :
     - [x] Jeux vidéo
     - [x] Divertissement
     - [x] Shorts
3. Cliquez sur **"Sauvegarder"**

### Étape 4 : Tester

1. Allez sur https://www.youtube.com
2. Attendez 2-3 secondes (chargement du modèle)
3. Les vidéos filtrées disparaissent automatiquement ! ✨

**Ouvrez la console** (F12) pour voir les logs :
```
[BrainFilter] Extension chargée
[BrainFilter] Modèle chargé: { n_features: 500, n_classes: 8, ... }
[BrainFilter] Trouvé 30 vidéos (ytd-video-renderer)
[BrainFilter] Vidéo filtrée (jeux): "Minecraft gameplay FR #1"
[BrainFilter] Stats: 12/30 vidéos filtrées
```

## 🧪 Test de classification manuelle

Pour tester le classificateur sans l'installer :

1. Ouvrez la console Chrome sur YouTube (F12)
2. Copiez-collez ce code :

```javascript
// Charger le classificateur
fetch(chrome.runtime.getURL('model.json'))
  .then(r => r.json())
  .then(model => {
    console.log('Modèle chargé !');

    // Tester quelques titres
    const titles = [
      "Minecraft gameplay FR #1",
      "Les dérivées expliquées simplement",
      "TOP 10 FAILS COMPILATION",
      "Incroyable astuce #shorts"
    ];

    // (Implémentez la fonction de prédiction ici)
  });
```

## 🔧 Dépannage rapide

### Problème : L'extension ne se charge pas

**Solution :**
- Vérifiez que tous les fichiers sont présents
- Vérifiez la console pour les erreurs (F12)
- Rechargez l'extension : `chrome://extensions/` → bouton refresh

### Problème : Les vidéos ne sont pas filtrées

**Solutions possibles :**

1. **Vérifiez l'heure actuelle**
   - Si vous êtes entre 20h et 21h (ou votre plage définie), le filtrage est désactivé
   - Changez temporairement la plage horaire pour tester

2. **Vérifiez les catégories sélectionnées**
   - Ouvrez le popup
   - Assurez-vous que des catégories sont cochées
   - Cliquez sur "Sauvegarder"

3. **Actualisez la page YouTube**
   - Appuyez sur F5
   - Attendez 2-3 secondes que le modèle se charge

4. **Vérifiez la console**
   ```
   F12 → Console
   ```
   Vous devriez voir :
   ```
   [BrainFilter] Extension chargée
   [BrainFilter] Modèle chargé
   ```

### Problème : L'extension est trop lente

**Solutions :**
- Le premier chargement du modèle (1.6 MB) prend 2-3 secondes
- Une fois chargé, l'inférence est instantanée
- Si c'est toujours lent, vérifiez votre connexion Internet

### Problème : Certaines vidéos sont mal classées

**C'est normal !**
- Le modèle a été entraîné sur un dataset limité (1600 titres)
- Il peut se tromper sur des titres ambigus
- Vous pouvez améliorer le modèle :
  ```bash
  # Ajouter plus d'exemples dans generate_dataset.py
  # Puis réentraîner
  python ml/models/export_simple_model.py
  ```

## 📊 Voir les statistiques

Ouvrez la console (F12) pendant que vous naviguez sur YouTube :

```
[BrainFilter] Stats: 12/30 vidéos filtrées
```

Cela vous indique combien de vidéos ont été cachées.

## 🎯 Configuration recommandée

### Pour la productivité maximale :

- **Heures autorisées** : 20h - 21h (ou votre moment de détente)
- **Catégories filtrées** :
  - [x] Jeux vidéo
  - [x] Divertissement
  - [x] Shorts
- **Catégories autorisées** :
  - [ ] Math
  - [ ] Sciences
  - [ ] Documentaires
  - [ ] Philosophie
  - [ ] Musique

### Pour un filtrage modéré :

- **Heures autorisées** : 18h - 22h
- **Catégories filtrées** :
  - [x] Shorts uniquement

## 🔄 Mettre à jour le modèle

Si vous voulez améliorer le modèle :

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Regénérer le dataset avec plus d'exemples
# (Éditez ml/dataset/generate_dataset.py pour augmenter samples_per_category)
python ml/dataset/generate_dataset.py

# 3. Réentraîner et exporter
python ml/models/export_simple_model.py

# 4. Recharger l'extension dans Chrome
# chrome://extensions/ → bouton refresh
```

## 📞 Support

En cas de problème :

1. Consultez les logs dans la console (F12)
2. Vérifiez le fichier README.md pour plus de détails
3. Vérifiez que le fichier `extension/model.json` existe et fait ~1.6 MB

## 🎉 Profitez !

Vous êtes maintenant prêt à reprendre le contrôle de votre navigation YouTube ! 🧠✨
