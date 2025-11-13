/**
 * Classificateur de titres YouTube (TF-IDF + SVM Linear)
 */

class YouTubeClassifier {
  constructor() {
    this.model = null;
    this.ready = false;
  }

  /**
   * Charge le modèle depuis le fichier JSON
   */
  async loadModel() {
    try {
      let modelUrl;
      if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getURL) {
        modelUrl = chrome.runtime.getURL('model.json');
      } else {
        // Mode fallback : chemin relatif
        modelUrl = 'model.json';
      }
      const response = await fetch(modelUrl);
      this.model = await response.json();
      this.ready = true;
      console.log('[BrainFilter] Modèle chargé:', this.model.metadata);
    } catch (error) {
      console.error('[BrainFilter] Erreur lors du chargement du modèle:', error);
    }
  }

  /**
   * Normalise un texte (lowercase, suppression accents)
   */
  normalizeText(text) {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, ''); // Supprime les accents
  }

  /**
   * Extrait les n-grams d'un texte
   */
  extractNgrams(words, n) {
    const ngrams = [];
    for (let i = 0; i <= words.length - n; i++) {
      ngrams.push(words.slice(i, i + n).join(' '));
    }
    return ngrams;
  }

  /**
   * Tokenize un texte et extrait les n-grams
   */
  tokenize(text) {
    const normalized = this.normalizeText(text);
    const words = normalized.match(/\b[\w]+\b/g) || [];

    // Extraire unigrams et bigrams
    const unigrams = words;
    const bigrams = this.extractNgrams(words, 2);

    return [...unigrams, ...bigrams];
  }

  /**
   * Convertit un texte en vecteur TF-IDF
   */
  textToTfidf(text) {
    const tokens = this.tokenize(text);
    const vocab = this.model.tfidf.vocabulary;
    const idf = this.model.tfidf.idf;

    // Compter les occurrences de chaque token
    const termFreq = {};
    for (const token of tokens) {
      if (vocab.hasOwnProperty(token)) {
        termFreq[token] = (termFreq[token] || 0) + 1;
      }
    }

    // Normaliser par la longueur du document (TF)
    const docLength = tokens.length || 1;
    for (const token in termFreq) {
      termFreq[token] /= docLength;
    }

    // Créer le vecteur TF-IDF
    const vector = new Array(this.model.metadata.n_features).fill(0);
    for (const token in termFreq) {
      const idx = vocab[token];
      vector[idx] = termFreq[token] * idf[idx];
    }

    return vector;
  }

  /**
   * Produit scalaire de deux vecteurs
   */
  dotProduct(v1, v2) {
    let sum = 0;
    for (let i = 0; i < v1.length; i++) {
      sum += v1[i] * v2[i];
    }
    return sum;
  }

  /**
   * Prédit la catégorie d'un texte avec SVM linéaire
   */
  predict(text) {
    if (!this.ready) {
      console.error('[BrainFilter] Modèle non chargé');
      return null;
    }

    // Convertir en vecteur TF-IDF
    const vector = this.textToTfidf(text);

    // Pour LinearSVC, la décision se fait par:
    // score[class] = dot(coef[class], x) + intercept[class]

    const coef = this.model.svm.coef;
    const intercept = this.model.svm.intercept;
    const classes = this.model.svm.classes;

    // Calculer le score de décision pour chaque classe
    const scores = [];

    for (let classIdx = 0; classIdx < classes.length; classIdx++) {
      const score = this.dotProduct(coef[classIdx], vector) + intercept[classIdx];
      scores.push(score);
    }

    // Trouver la classe avec le score maximal
    let maxScore = scores[0];
    let maxIdx = 0;
    for (let i = 1; i < scores.length; i++) {
      if (scores[i] > maxScore) {
        maxScore = scores[i];
        maxIdx = i;
      }
    }

    return {
      category: classes[maxIdx],
      score: maxScore,
      allScores: scores.map((s, i) => ({ category: classes[i], score: s }))
    };
  }

  /**
   * Vérifie si une vidéo doit être filtrée
   */
  async shouldFilter(title, currentHour = new Date().getHours()) {
    if (!this.ready) {
      await this.loadModel();
    }

    // Récupérer les paramètres de filtrage
    const settings = await this.getSettings();

    // Si le filtrage est désactivé
    if (!settings.enabled) {
      return false;
    }

    // Vérifier si on est dans la plage horaire autorisée
    if (currentHour >= settings.allowedHourStart && currentHour < settings.allowedHourEnd) {
      return false; // Ne pas filtrer pendant les heures autorisées
    }

    // Classifier la vidéo
    const prediction = this.predict(title);
    if (!prediction) {
      return false;
    }

    // Vérifier si la catégorie doit être filtrée
    return settings.filteredCategories.includes(prediction.category);
  }

  /**
   * Récupère les paramètres depuis le storage
   */
  async getSettings() {
    const defaults = {
      enabled: true,
      allowedHourStart: 20, // 20h
      allowedHourEnd: 21,   // 21h
      filteredCategories: ['jeux', 'divertissement', 'shorts']
    };

    // Vérifier si chrome.storage est disponible
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync) {
      return new Promise((resolve) => {
        chrome.storage.sync.get(defaults, resolve);
      });
    } else {
      // Mode fallback : retourner les valeurs par défaut
      console.log('[BrainFilter] chrome.storage non disponible, utilisation des paramètres par défaut');
      return defaults;
    }
  }
}

// Instance globale du classificateur
const classifier = new YouTubeClassifier();
