"""
Script principal pour tester toutes les combinaisons embedding + classificateur.
"""
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Ajouter le dossier parent au path
sys.path.append(str(Path(__file__).parent.parent))

from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import LabelEncoder
import numpy as np

from models.embeddings import (
    TfidfEmbedding,
    BOWEmbedding,
    KeywordEmbedding,
    HybridEmbedding,
    SENTENCE_TRANSFORMERS_AVAILABLE
)

if SENTENCE_TRANSFORMERS_AVAILABLE:
    from models.embeddings import SentenceTransformerEmbedding

from evaluation.benchmark import BenchmarkRunner, load_data


class GMMClassifier:
    """
    Wrapper pour GMM qui le rend compatible avec l'API sklearn.
    GMM n'est pas un classificateur au sens strict, on utilise un GMM par classe.
    """

    def __init__(self, n_components=2, random_state=42):
        self.n_components = n_components
        self.random_state = random_state
        self.gmms = {}
        self.classes_ = None

    def fit(self, X, y):
        """Entraîne un GMM pour chaque classe."""
        self.classes_ = np.unique(y)
        for label in self.classes_:
            X_class = X[y == label]
            gmm = GaussianMixture(
                n_components=self.n_components,
                random_state=self.random_state,
                covariance_type='diag'  # Plus simple et plus rapide
            )
            gmm.fit(X_class)
            self.gmms[label] = gmm
        return self

    def predict(self, X):
        """Prédit la classe en choisissant le GMM avec la plus haute likelihood."""
        predictions = []
        for x in X:
            x = x.reshape(1, -1)
            scores = {label: gmm.score(x) for label, gmm in self.gmms.items()}
            predictions.append(max(scores, key=scores.get))
        return np.array(predictions)


def create_models():
    """
    Crée toutes les combinaisons embedding + classificateur à tester.

    Returns:
        Liste de tuples (pipeline, nom)
    """
    models = []

    # === Embeddings à tester ===
    embeddings = [
        (TfidfEmbedding(max_features=500, ngram_range=(1, 2)), "TF-IDF-500"),
        (TfidfEmbedding(max_features=1000, ngram_range=(1, 2)), "TF-IDF-1000"),
        (TfidfEmbedding(max_features=2000, ngram_range=(1, 3)), "TF-IDF-2000-trigram"),
        (BOWEmbedding(max_features=500, ngram_range=(1, 2)), "BOW-500"),
        (KeywordEmbedding(), "Keywords"),
        (HybridEmbedding([
            TfidfEmbedding(max_features=500, ngram_range=(1, 2)),
            KeywordEmbedding()
        ]), "Hybrid-TFIDF+Keywords"),
    ]

    # Ajouter Sentence Transformers si disponible
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        embeddings.append((
            SentenceTransformerEmbedding('paraphrase-multilingual-MiniLM-L12-v2'),
            "SentenceTransformer"
        ))

    # === Classificateurs à tester ===
    classifiers = [
        (KNeighborsClassifier(n_neighbors=5), "KNN-5"),
        (KNeighborsClassifier(n_neighbors=10), "KNN-10"),
        (KNeighborsClassifier(n_neighbors=15, weights='distance'), "KNN-15-weighted"),
        (SVC(kernel='linear', C=1.0, random_state=42), "SVM-Linear"),
        (SVC(kernel='rbf', C=1.0, random_state=42), "SVM-RBF"),
        (GMMClassifier(n_components=2, random_state=42), "GMM-2"),
        (GMMClassifier(n_components=3, random_state=42), "GMM-3"),
    ]

    # === Créer toutes les combinaisons ===
    for embedding, emb_name in embeddings:
        for classifier, clf_name in classifiers:
            # Créer un pipeline
            pipeline = Pipeline([
                ('embedding', embedding),
                ('classifier', classifier)
            ])

            model_name = f"{emb_name} + {clf_name}"
            models.append((pipeline, model_name))

    return models


def main():
    """Exécute le benchmark complet."""
    print("="*70)
    print("BENCHMARK COMPLET - CLASSIFICATION DE TITRES YOUTUBE")
    print("="*70)

    # Charger les données
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "youtube_titles.csv"
    print(f"\nChargement des données depuis: {data_path}")

    X_train, X_val, y_train, y_val, label_names = load_data(data_path)

    # Créer tous les modèles à tester
    print("\nCréation des modèles à tester...")
    models = create_models()
    print(f"  ✓ {len(models)} combinaisons à tester")

    # Afficher la liste des modèles
    print("\nModèles à benchmarker:")
    for i, (_, name) in enumerate(models, 1):
        print(f"  {i:2d}. {name}")

    # Lancer le benchmark
    output_dir = Path(__file__).parent.parent.parent / "data" / "evaluation_results"
    runner = BenchmarkRunner(output_dir)

    print("\n" + "="*70)
    print("DÉBUT DU BENCHMARK")
    print("="*70)

    runner.run(models, X_train, X_val, y_train, y_val)

    print("\n" + "="*70)
    print("BENCHMARK TERMINÉ")
    print("="*70)
    print(f"\nRésultats sauvegardés dans: {output_dir}")


if __name__ == "__main__":
    main()
