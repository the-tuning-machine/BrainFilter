/**
 * Content script pour filtrer les vidéos YouTube
 */

(async function() {
  'use strict';

  console.log('[BrainFilter] Extension chargée');

  // Charger le modèle au démarrage
  await classifier.loadModel();

  // Statistiques de filtrage
  let stats = {
    filtered: 0,
    total: 0
  };

  /**
   * Vérifie si on est sur une page où le filtrage doit être actif
   */
  function shouldActivateFiltering() {
    const hostname = window.location.hostname;
    const path = window.location.pathname;
    const searchParams = new URLSearchParams(window.location.search);

    // Mode test : activer sur localhost
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return true;
    }

    // Ne PAS filtrer sur les pages de recherche
    if (searchParams.has('search_query')) {
      return false;
    }

    // Filtrer sur la page d'accueil
    if (path === '/' || path === '/feed/subscriptions' || path === '/feed/trending') {
      return true;
    }

    // Filtrer sur les pages de vidéos (recommandations à droite)
    if (path.startsWith('/watch')) {
      return true;
    }

    return false;
  }

  /**
   * Extrait le titre d'un élément vidéo YouTube
   */
  function getVideoTitle(element) {
    // Stratégie 1 : Chercher n'importe quel élément avec attribut "title"
    const elemWithTitle = element.querySelector('[title]');
    if (elemWithTitle) {
      const title = elemWithTitle.getAttribute('title');
      if (title && title.length > 10) { // Titre significatif
        return title;
      }
    }

    // Stratégie 2 : Sélecteurs spécifiques
    const selectors = [
      'a#video-title-link',             // Rich items (priorité)
      'ytd-rich-grid-media a',          // Rich grid
      'h3 a',                           // Tout lien dans h3
      '#video-title',                   // Vidéos normales
      'a#video-title',                  // Variante
      'h3.title-and-badge a',           // Shorts
      'span#video-title',               // Autre variante
      'yt-formatted-string'             // Texte formaté (fallback)
    ];

    for (const selector of selectors) {
      const titleElement = element.querySelector(selector);
      if (titleElement) {
        const title = titleElement.getAttribute('title') ||
                     titleElement.getAttribute('aria-label') ||
                     titleElement.textContent.trim();
        if (title && title.length > 5) {
          return title;
        }
      }
    }

    return null;
  }

  /**
   * Filtre (cache) un élément vidéo
   */
  function filterVideo(element, category) {
    element.style.display = 'none';
    element.setAttribute('data-brainfilter-filtered', category);
    stats.filtered++;
  }

  /**
   * Détecte si un élément est un Short YouTube
   */
  function isShort(element) {
    // Méthode 1 : Vérifier la structure HTML spécifique aux Shorts
    if (element.querySelector('ytm-shorts-lockup-view-model') ||
        element.querySelector('ytm-shorts-lockup-view-model-v2')) {
      return true;
    }

    // Méthode 2 : Vérifier l'URL
    const link = element.querySelector('a[href*="/shorts/"]');
    if (link) {
      return true;
    }

    return false;
  }

  /**
   * Traite un élément vidéo
   */
  async function processVideoElement(element) {
    // Éviter de traiter plusieurs fois le même élément
    if (element.hasAttribute('data-brainfilter-processed')) {
      return;
    }

    element.setAttribute('data-brainfilter-processed', 'true');
    stats.total++;

    // Détection spéciale pour les Shorts
    if (isShort(element)) {
      // Filtrer directement tous les Shorts
      const settings = await classifier.getSettings();
      if (settings.enabled && settings.filteredCategories.includes('shorts')) {
        // Vérifier l'heure
        const currentHour = new Date().getHours();
        if (currentHour < settings.allowedHourStart || currentHour >= settings.allowedHourEnd) {
          filterVideo(element, 'shorts');
          return;
        }
      }
      return;
    }

    const title = getVideoTitle(element);
    if (!title) {
      // Titre non trouvé - skip silencieusement
      return;
    }

    // Log réduit (commenté pour production)
    // console.log('[BrainFilter] Analyse:', title.substring(0, 50) + '...');

    // Vérifier si la vidéo doit être filtrée
    const shouldFilter = await classifier.shouldFilter(title);

    if (shouldFilter) {
      const prediction = classifier.predict(title);
      filterVideo(element, prediction.category);
    }
  }

  /**
   * Trouve et traite toutes les vidéos sur la page
   */
  async function processAllVideos() {
    if (!shouldActivateFiltering()) {
      return;
    }

    // Sélecteurs pour les différents types de conteneurs de vidéos
    const selectors = [
      'ytd-video-renderer',              // Vidéos normales (feed)
      'ytd-grid-video-renderer',         // Grille de vidéos
      'ytd-compact-video-renderer',      // Recommandations (sidebar)
      'ytd-rich-item-renderer',          // Feed enrichi
      'ytd-reel-item-renderer'           // Shorts
    ];

    for (const selector of selectors) {
      const videos = document.querySelectorAll(selector);
      for (const video of videos) {
        await processVideoElement(video);
      }
    }

    // Afficher les stats uniquement si des vidéos ont été filtrées
    if (stats.filtered > 0) {
      console.log(`[BrainFilter] ${stats.filtered}/${stats.total} vidéos filtrées`);
    }
  }

  /**
   * Observer pour détecter les nouvelles vidéos (scroll infini)
   */
  function setupObserver() {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Vérifier si c'est un conteneur de vidéo
            const selectors = [
              'ytd-video-renderer',
              'ytd-grid-video-renderer',
              'ytd-compact-video-renderer',
              'ytd-rich-item-renderer',
              'ytd-reel-item-renderer'
            ];

            for (const selector of selectors) {
              if (node.matches && node.matches(selector)) {
                processVideoElement(node);
              }

              // Vérifier les enfants aussi
              const children = node.querySelectorAll(selector);
              for (const child of children) {
                processVideoElement(child);
              }
            }
          }
        }
      }
    });

    // Observer le contenu principal
    let target = document.querySelector('ytd-app');
    if (!target) {
      // Fallback pour localhost : observer le body
      target = document.body;
    }

    if (target) {
      observer.observe(target, {
        childList: true,
        subtree: true
      });
    }
  }

  /**
   * Réinitialise le filtrage quand on change de page
   */
  function setupNavigationListener() {
    // Ne pas configurer sur localhost (pas de navigation SPA)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return;
    }

    const ytdApp = document.querySelector('ytd-app');
    if (!ytdApp) {
      return;
    }

    let lastUrl = location.href;

    new MutationObserver(() => {
      const currentUrl = location.href;
      if (currentUrl !== lastUrl) {
        lastUrl = currentUrl;

        // Réinitialiser les stats
        stats = { filtered: 0, total: 0 };

        // Réinitialiser les marqueurs
        document.querySelectorAll('[data-brainfilter-processed]').forEach(el => {
          el.removeAttribute('data-brainfilter-processed');
          el.removeAttribute('data-brainfilter-filtered');
          el.style.display = '';
        });

        // Re-traiter la page
        setTimeout(processAllVideos, 1000);
      }
    }).observe(ytdApp, {
      subtree: true,
      childList: true
    });
  }

  // Attendre que la page soit complètement chargée
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  async function init() {
    // Traiter les vidéos existantes
    await processAllVideos();

    // Configurer l'observer pour les nouvelles vidéos
    setupObserver();

    // Configurer le listener de navigation
    setupNavigationListener();

    // Re-traiter régulièrement (au cas où)
    setInterval(processAllVideos, 5000);
  }
})();
