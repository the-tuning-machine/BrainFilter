/**
 * Script de diagnostic pour BrainFilter sur YouTube
 *
 * Comment utiliser:
 * 1. Aller sur youtube.com
 * 2. Ouvrir la console (F12)
 * 3. Copier-coller ce script entier
 * 4. Appuyer sur Entrée
 */

console.log('🔍 === DIAGNOSTIC BRAINFILTER ===\n');

// 1. Vérifier que le classificateur existe
console.log('1️⃣ Vérification du classificateur...');
if (typeof classifier !== 'undefined') {
  console.log('   ✅ Classificateur détecté');
  console.log('   - Ready:', classifier.ready);
  if (classifier.model) {
    console.log('   - Modèle:', classifier.model.metadata);
  }
} else {
  console.log('   ❌ Classificateur non trouvé!');
  console.log('   → L\'extension n\'est peut-être pas chargée');
}

// 2. Vérifier les paramètres
console.log('\n2️⃣ Vérification des paramètres...');
chrome.storage.sync.get({
  enabled: true,
  allowedHourStart: 20,
  allowedHourEnd: 21,
  filteredCategories: ['jeux', 'divertissement', 'shorts']
}, (settings) => {
  console.log('   Settings:', settings);

  // Vérifier l'heure
  const now = new Date();
  const currentHour = now.getHours();
  console.log('   - Heure actuelle:', currentHour + 'h');
  console.log('   - Plage autorisée:', settings.allowedHourStart + 'h -', settings.allowedHourEnd + 'h');

  if (currentHour >= settings.allowedHourStart && currentHour < settings.allowedHourEnd) {
    console.log('   ⚠️  VOUS ÊTES DANS LA PLAGE HORAIRE AUTORISÉE');
    console.log('   → Le filtrage est DÉSACTIVÉ (c\'est normal!)');
    console.log('   → Pour tester, changez les heures dans le popup à 2h-3h');
  } else {
    console.log('   ✅ En dehors de la plage horaire');
    console.log('   → Le filtrage devrait être actif');
  }

  console.log('   - Catégories filtrées:', settings.filteredCategories.join(', '));
});

// 3. Trouver des vidéos
console.log('\n3️⃣ Recherche de vidéos...');
const videos = document.querySelectorAll('ytd-rich-item-renderer');
console.log('   Trouvé', videos.length, 'vidéos (ytd-rich-item-renderer)');

if (videos.length > 0) {
  console.log('\n4️⃣ Test d\'extraction de titre sur 3 vidéos...');

  for (let i = 0; i < Math.min(3, videos.length); i++) {
    const video = videos[i];
    console.log(`\n   Vidéo ${i + 1}:`);

    // Essayer différents sélecteurs
    const selectors = [
      '#video-title',
      'a#video-title',
      'h3 a#video-title-link',
      'a#video-title-link',
      'yt-formatted-string'
    ];

    let titleFound = false;
    for (const selector of selectors) {
      const elem = video.querySelector(selector);
      if (elem) {
        const title = elem.getAttribute('title') ||
                     elem.getAttribute('aria-label') ||
                     elem.textContent.trim();
        if (title && title.length > 5) {
          console.log(`   ✅ ${selector}:`);
          console.log(`      "${title}"`);
          titleFound = true;

          // Tester la classification si le classificateur est prêt
          if (typeof classifier !== 'undefined' && classifier.ready) {
            const pred = classifier.predict(title);
            if (pred) {
              console.log(`      → Catégorie: ${pred.category} (score: ${pred.score.toFixed(2)})`);

              // Tester shouldFilter
              classifier.shouldFilter(title).then(should => {
                console.log(`      → Filtrer? ${should ? 'OUI ✅' : 'NON ❌'}`);
              });
            }
          }

          break;
        }
      }
    }

    if (!titleFound) {
      console.log('   ❌ Aucun titre trouvé avec les sélecteurs connus');
      console.log('   → Inspectez manuellement la vidéo pour trouver le bon sélecteur');
    }
  }
}

// 5. Test manuel du classificateur
console.log('\n5️⃣ Test manuel du classificateur...');
if (typeof classifier !== 'undefined' && classifier.ready) {
  const testTitles = [
    "Minecraft gameplay FR #1",
    "Les dérivées expliquées simplement",
    "TOP 10 FAILS COMPILATION"
  ];

  console.log('   Tests sur des titres connus:');
  for (const title of testTitles) {
    const pred = classifier.predict(title);
    console.log(`   - "${title}"`);
    console.log(`     → ${pred.category}`);
  }
} else {
  console.log('   ❌ Classificateur pas prêt');
  console.log('   → Attendez quelques secondes ou rechargez la page');
}

console.log('\n✅ Diagnostic terminé!\n');
console.log('📋 Résumé:');
console.log('   - Si vous voyez "DANS LA PLAGE HORAIRE AUTORISÉE" → changez les heures à 2h-3h dans le popup');
console.log('   - Si les titres ne sont pas trouvés → il faut ajouter le bon sélecteur CSS');
console.log('   - Si le classificateur n\'est pas prêt → attendez ou rechargez la page');
console.log('');
