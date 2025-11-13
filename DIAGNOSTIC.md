# 🔍 Guide de diagnostic - BrainFilter

## Problème : 0 vidéos filtrées

Vous voyez dans la console :
```
[BrainFilter] Trouvé 40 vidéos (ytd-rich-item-renderer)
[BrainFilter] Stats: 0/40 vidéos filtrées
```

Cela signifie que les vidéos sont détectées mais pas filtrées.

## Étape 1 : Vérifier que le modèle est chargé

Dans la console Chrome (F12), vérifiez que vous voyez :
```
[BrainFilter] Extension chargée
[BrainFilter] Modèle chargé: { model_type: "TF-IDF + SVM-Linear", n_features: 500, ... }
```

**Si vous ne voyez PAS "Modèle chargé" :**
- Le fichier `model.json` est peut-être manquant ou corrompu
- Vérifiez : `ls -lh extension/model.json` (devrait faire ~1.6 MB)

## Étape 2 : Tester le classificateur directement

Ouvrez le fichier de test dans votre navigateur :
```bash
# Depuis votre navigateur, ouvrir :
file:///home/alan-tuning/Documents/BrainFilter/extension/test-classifier.html
```

Vous devriez voir :
- ✅ Modèle chargé
- Une liste de titres avec leurs catégories prédites

**Si ça ne marche pas :**
- Le modèle a un problème
- Voir "Régénérer le modèle" ci-dessous

## Étape 3 : Vérifier l'heure actuelle

Le filtrage est peut-être désactivé car vous êtes dans la plage horaire autorisée.

```bash
# Voir l'heure actuelle
date +%H
```

**Si vous êtes entre 20h et 21h** (ou votre plage configurée) :
- Le filtrage est **désactivé** par design
- C'est votre moment de détente !

**Solution pour tester :**
1. Ouvrez le popup BrainFilter
2. Changez les heures à : `2` h à `3` h
3. Cliquez sur "Sauvegarder"
4. Actualisez YouTube (F5)
5. Maintenant ça devrait filtrer !

## Étape 4 : Vérifier les catégories sélectionnées

1. Ouvrez le popup BrainFilter (cliquez sur l'icône)
2. Vérifiez que des catégories sont **cochées** :
   - [x] Jeux vidéo
   - [x] Divertissement
   - [x] Shorts
3. Cliquez sur "Sauvegarder"

## Étape 5 : Vérifier l'extraction des titres

J'ai ajouté des logs de debug. Rechargez l'extension :

1. Allez sur `chrome://extensions/`
2. Trouvez BrainFilter
3. Cliquez sur le bouton refresh 🔄
4. Retournez sur YouTube
5. Ouvrez la console (F12)

Vous devriez maintenant voir :
```
[BrainFilter] Analyse: Minecraft gameplay FR #1...
[BrainFilter] Vidéo filtrée (jeux): Minecraft gameplay FR #1
```

**Si vous voyez "Titre non trouvé pour:" :**
- Les sélecteurs CSS ne fonctionnent pas
- YouTube a peut-être changé son HTML
- Voir "Inspecter le HTML" ci-dessous

## Étape 6 : Inspecter le HTML de YouTube

Pour comprendre pourquoi les titres ne sont pas extraits :

1. Sur YouTube, faites **clic droit** sur une vidéo
2. Choisir **"Inspecter"**
3. Regardez la structure HTML
4. Trouvez où est le titre de la vidéo

Exemple de ce que vous cherchez :
```html
<ytd-rich-item-renderer>
  ...
  <h3>
    <a id="video-title-link" title="Le titre de la vidéo">
      Le titre de la vidéo
    </a>
  </h3>
  ...
</ytd-rich-item-renderer>
```

**Notez le sélecteur CSS** qui pointe vers le titre, par exemple :
- `a#video-title-link`
- `h3 a[title]`
- etc.

Si ce n'est pas dans la liste des sélecteurs de `content.js`, il faut l'ajouter.

## Étape 7 : Tester manuellement dans la console

Sur YouTube, dans la console Chrome (F12), tapez :

```javascript
// Tester l'extraction de titre sur la première vidéo
const video = document.querySelector('ytd-rich-item-renderer');
console.log('Élément vidéo:', video);

// Essayer différents sélecteurs
const selectors = [
  '#video-title',
  'a#video-title',
  'h3 a#video-title-link',
  'a#video-title-link'
];

for (const sel of selectors) {
  const elem = video.querySelector(sel);
  if (elem) {
    console.log(`✅ ${sel}:`, elem.getAttribute('title') || elem.textContent);
  } else {
    console.log(`❌ ${sel}: non trouvé`);
  }
}
```

Cela vous dira quel sélecteur fonctionne.

## Étape 8 : Tester le classificateur manuellement

Dans la console sur YouTube :

```javascript
// Charger le modèle (si pas déjà fait)
await classifier.loadModel();

// Tester quelques titres
const testTitles = [
  "Minecraft gameplay FR #1",
  "Les dérivées expliquées",
  "TOP 10 FAILS"
];

for (const title of testTitles) {
  const pred = classifier.predict(title);
  console.log(`"${title}" → ${pred.category} (score: ${pred.score.toFixed(2)})`);
}

// Tester shouldFilter
for (const title of testTitles) {
  const should = await classifier.shouldFilter(title);
  console.log(`"${title}" → filtrer? ${should}`);
}
```

**Si shouldFilter retourne toujours false :**
- Vérifiez les paramètres dans le popup
- Vérifiez l'heure actuelle vs plage autorisée

## Solutions rapides

### Solution 1 : Recharger l'extension

```bash
# 1. Aller sur chrome://extensions/
# 2. Trouver BrainFilter
# 3. Cliquer sur refresh 🔄
# 4. Retourner sur YouTube et actualiser (F5)
```

### Solution 2 : Forcer le filtrage (debug)

Modifiez temporairement les heures pour forcer le filtrage :
- Popup → Heures : `2` à `3`
- Sauvegarder
- Actualiser YouTube

### Solution 3 : Vérifier le fichier model.json

```bash
cd /home/alan-tuning/Documents/BrainFilter/extension
ls -lh model.json

# Devrait afficher environ 1.6M
# Si absent ou trop petit, régénérer :
cd ..
source venv/bin/activate
python ml/models/export_simple_model.py
```

### Solution 4 : Réinstaller complètement

```bash
# 1. Désinstaller l'extension (chrome://extensions/)
# 2. Vérifier que model.json existe et est correct
# 3. Réinstaller (Charger l'extension non empaquetée)
# 4. Reconfigurer le popup
```

## Régénérer le modèle

Si le classificateur ne fonctionne pas du tout :

```bash
cd /home/alan-tuning/Documents/BrainFilter
source venv/bin/activate

# Régénérer le modèle
python ml/models/export_simple_model.py

# Vérifier la taille
ls -lh extension/model.json

# Devrait afficher ~1.6M
```

## Logs détaillés

Pour avoir encore plus de logs, modifiez `classifier.js` :

```javascript
// Dans la fonction predict(), ajouter :
console.log('[Classifier] Prédiction pour:', text);
console.log('[Classifier] Résultat:', result);
```

## Support avancé

Si rien ne fonctionne, envoyez-moi :

1. **Sortie de la console complète** (F12 → Console → copier tout)
2. **Paramètres du popup** (capture d'écran)
3. **Heure actuelle** : `date +%H`
4. **Taille du modèle** : `ls -lh extension/model.json`
5. **HTML d'une vidéo** (Inspecter → copier l'élément)

## Vérification finale

Checklist complète :

- [ ] Modèle chargé (voir console)
- [ ] Heure actuelle en dehors de la plage autorisée
- [ ] Catégories cochées dans le popup (jeux, divertissement, shorts)
- [ ] Extension rechargée
- [ ] YouTube actualisé (F5)
- [ ] Logs de debug visibles dans la console

Si tout est coché et ça ne marche toujours pas, c'est probablement un problème d'extraction de titres (voir Étape 6 et 7).
