"""
Différentes méthodes d'embedding pour les titres de vidéos.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.base import BaseEstimator, TransformerMixin


class TfidfEmbedding(BaseEstimator, TransformerMixin):
    """Embedding TF-IDF simple et rapide."""

    def __init__(self, max_features=1000, ngram_range=(1, 2)):
        """
        Args:
            max_features: Nombre maximum de features
            ngram_range: Range des n-grams (ex: (1,2) pour unigrams et bigrams)
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = None

    def fit(self, X, y=None):
        """Entraîne le vectorizer TF-IDF."""
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            lowercase=True,
            strip_accents='unicode'
        )
        self.vectorizer.fit(X)
        return self

    def transform(self, X):
        """Transforme les textes en vecteurs TF-IDF."""
        return self.vectorizer.transform(X).toarray()


class BOWEmbedding(BaseEstimator, TransformerMixin):
    """Embedding Bag of Words simple."""

    def __init__(self, max_features=1000, ngram_range=(1, 2)):
        """
        Args:
            max_features: Nombre maximum de features
            ngram_range: Range des n-grams
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = None

    def fit(self, X, y=None):
        """Entraîne le vectorizer BOW."""
        self.vectorizer = CountVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            lowercase=True,
            strip_accents='unicode'
        )
        self.vectorizer.fit(X)
        return self

    def transform(self, X):
        """Transforme les textes en vecteurs BOW."""
        return self.vectorizer.transform(X).toarray()


class KeywordEmbedding(BaseEstimator, TransformerMixin):
    """
    Embedding basé sur des mots-clés par catégorie.
    Approche simple mais efficace pour ce cas d'usage.
    """

    def __init__(self):
        """Initialise avec des mots-clés par catégorie."""
        self.keywords = {
            'jeux': [
                'gameplay', 'game', 'gaming', 'minecraft', 'fortnite', 'gta',
                'play', 'joue', 'teste', 'let\'s play', 'speedrun', 'build',
                'kill', 'ranked', 'battle royale', 'league', 'valorant',
                'tuto', 'tricks', 'fifa', 'rocket league', 'among us'
            ],
            'musique': [
                'music', 'song', 'lyrics', 'cover', 'acoustic', 'live',
                'official', 'remix', 'mix', 'playlist', 'tutorial',
                'guitar', 'piano', 'drum', 'violin', 'rock', 'pop', 'jazz'
            ],
            'math': [
                'math', 'equation', 'calcul', 'dérivée', 'intégrale',
                'théorème', 'démonstration', 'exercice', 'corrigé',
                'fonction', 'suite', 'limite', 'matrice', 'probabilité',
                'géométrie', 'terminale', 'première', 'licence', 'prépa'
            ],
            'sciences': [
                'science', 'physique', 'chimie', 'biologie', 'expérience',
                'pourquoi', 'comment', 'fonctionne', 'expliqué', 'découverte',
                'atome', 'cellule', 'adn', 'quantique', 'relativité',
                'univers', 'cerveau', 'évolution', 'trou noir'
            ],
            'documentaires': [
                'documentaire', 'histoire', 'documentary', 'enquête',
                'mystère', 'secret', 'voyage', 'découverte', 'coulisses',
                'civilisation', 'guerre', 'égypte', 'romain', 'maya',
                'biographie', 'événement', 'monde'
            ],
            'philosophie': [
                'philosophie', 'philosopher', 'platon', 'aristote', 'kant',
                'nietzsche', 'sartre', 'descartes', 'éthique', 'morale',
                'existence', 'liberté', 'conscience', 'vérité', 'justice',
                'stoïcisme', 'existentialisme', 'débat'
            ],
            'divertissement': [
                'incroyable', 'wtf', 'omg', 'mdr', 'fou', 'choquant',
                'fail', 'prank', 'défi', 'vlog', 'test', 'réagis',
                'drôle', 'marrant', 'compilation', 'best of', '24h',
                'storytime', 'tiktok', 'routine'
            ],
            'shorts': [
                'shorts', '#shorts', 'pov', 'astuce', 'life hack',
                'saviez-vous', 'wait for it', 'trick', 'conseil'
            ]
        }
        self.categories = list(self.keywords.keys())
        self.feature_names = []

    def fit(self, X, y=None):
        """Construit la liste de features."""
        # Créer une feature par mot-clé
        for category in self.categories:
            for keyword in self.keywords[category]:
                self.feature_names.append(f"{category}_{keyword}")
        return self

    def transform(self, X):
        """
        Transforme les textes en vecteurs basés sur les mots-clés.

        Pour chaque titre, crée un vecteur où chaque dimension représente
        la présence (ou le nombre d'occurrences) d'un mot-clé.
        """
        vectors = []

        for text in X:
            text_lower = text.lower()
            vector = []

            for category in self.categories:
                for keyword in self.keywords[category]:
                    # Compter les occurrences du mot-clé
                    count = text_lower.count(keyword.lower())
                    vector.append(count)

            vectors.append(vector)

        return np.array(vectors)


class HybridEmbedding(BaseEstimator, TransformerMixin):
    """
    Combine plusieurs embeddings (ex: TF-IDF + Keywords).
    """

    def __init__(self, embeddings):
        """
        Args:
            embeddings: Liste d'embeddings à combiner
        """
        self.embeddings = embeddings

    def fit(self, X, y=None):
        """Entraîne tous les embeddings."""
        for emb in self.embeddings:
            emb.fit(X, y)
        return self

    def transform(self, X):
        """Concatène les vecteurs de tous les embeddings."""
        vectors = [emb.transform(X) for emb in self.embeddings]
        return np.hstack(vectors)


# Tentative d'import de sentence-transformers (optionnel)
try:
    from sentence_transformers import SentenceTransformer

    class SentenceTransformerEmbedding(BaseEstimator, TransformerMixin):
        """
        Embedding avec Sentence Transformers (BERT-like).
        Plus lent mais potentiellement plus performant.
        """

        def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
            """
            Args:
                model_name: Nom du modèle à utiliser
                           (multilingual pour supporter le français)
            """
            self.model_name = model_name
            self.model = None

        def fit(self, X, y=None):
            """Charge le modèle pré-entraîné."""
            print(f"Chargement du modèle {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            return self

        def transform(self, X):
            """Encode les textes avec Sentence Transformers."""
            return self.model.encode(X, show_progress_bar=False)

    SENTENCE_TRANSFORMERS_AVAILABLE = True

except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers non disponible")
