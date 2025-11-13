"""
Entraîne et sauvegarde le modèle final pour l'extension.
"""
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

sys.path.append(str(Path(__file__).parent.parent))

from models.embeddings import TfidfEmbedding


def train_and_save_model():
    """Entraîne le meilleur modèle et le sauvegarde."""
    print("="*70)
    print("ENTRAÎNEMENT DU MODÈLE FINAL")
    print("="*70)

    # Charger tout le dataset (on utilise tout pour le modèle final)
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "youtube_titles.csv"
    print(f"\nChargement des données: {data_path}")

    df = pd.read_csv(data_path)
    X = df['title'].values
    y = df['category'].values

    print(f"  ✓ {len(X)} échantillons")
    print(f"  ✓ {len(df['category'].unique())} catégories")

    # Créer le pipeline (meilleur modèle du benchmark)
    print("\nCréation du pipeline: TF-IDF-500 + SVM-Linear")
    model = Pipeline([
        ('embedding', TfidfEmbedding(max_features=500, ngram_range=(1, 2))),
        ('classifier', SVC(kernel='linear', C=1.0, random_state=42, probability=True))
    ])

    # Entraîner
    print("\nEntraînement sur l'ensemble du dataset...")
    model.fit(X, y)
    print("  ✓ Entraînement terminé")

    # Sauvegarder
    output_dir = Path(__file__).parent.parent.parent / "data" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "youtube_classifier.pkl"
    print(f"\nSauvegarde du modèle: {model_path}")
    joblib.dump(model, model_path)
    print("  ✓ Modèle sauvegardé")

    # Sauvegarder également les catégories
    categories = sorted(df['category'].unique())
    categories_path = output_dir / "categories.pkl"
    joblib.dump(categories, categories_path)
    print(f"  ✓ Catégories sauvegardées: {categories_path}")

    # Tester le modèle
    print("\n" + "="*70)
    print("TEST DU MODÈLE")
    print("="*70)

    test_titles = [
        "Minecraft gameplay FR #1",
        "Beethoven - Symphony No. 5",
        "Les dérivées expliquées simplement",
        "Comment fonctionne un trou noir ?",
        "Documentaire sur l'Égypte ancienne",
        "Introduction à la philosophie de Kant",
        "TOP 10 FAILS COMPILATION",
        "Incroyable astuce #shorts"
    ]

    predictions = model.predict(test_titles)
    probas = model.predict_proba(test_titles)

    for title, pred, proba in zip(test_titles, predictions, probas):
        confidence = max(proba) * 100
        print(f"\n  Titre: {title}")
        print(f"  → Catégorie: {pred} (confiance: {confidence:.1f}%)")

    print("\n" + "="*70)
    print("TERMINÉ")
    print("="*70)
    print(f"\nLe modèle est prêt à être intégré dans l'extension !")
    print(f"Fichiers générés:")
    print(f"  - {model_path}")
    print(f"  - {categories_path}")


if __name__ == "__main__":
    train_and_save_model()
