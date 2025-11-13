"""
Entraîne un modèle simple et l'exporte directement en JSON.
"""
import json
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


def train_and_export():
    """Entraîne le modèle et l'exporte directement en JSON."""
    print("="*70)
    print("ENTRAÎNEMENT ET EXPORT DU MODÈLE")
    print("="*70)

    # Charger les données
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "youtube_titles.csv"
    print(f"\nChargement des données: {data_path}")

    df = pd.read_csv(data_path)
    X = df['title'].values
    y = df['category'].values

    print(f"  ✓ {len(X)} échantillons")

    # Créer et entraîner TF-IDF
    print("\nEntraînement TF-IDF...")
    tfidf = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),
        lowercase=True,
        strip_accents='unicode'
    )
    X_tfidf = tfidf.fit_transform(X)
    print("  ✓ TF-IDF entraîné")

    # Créer et entraîner SVM
    print("\nEntraînement SVM...")
    svm = LinearSVC(C=1.0, random_state=42, max_iter=10000)
    svm.fit(X_tfidf, y)
    print("  ✓ SVM entraîné")

    # Extraire les paramètres
    # Convertir le vocabulaire en dict Python natif (pas numpy)
    vocabulary = {word: int(idx) for word, idx in tfidf.vocabulary_.items()}
    idf_values = tfidf.idf_.tolist()

    # Pour LinearSVC, on a directement coef_ et intercept_
    coef = svm.coef_.tolist()  # shape: (n_classes, n_features)
    intercept = svm.intercept_.tolist()  # shape: (n_classes,)
    classes = svm.classes_.tolist()
    categories = sorted(df['category'].unique())

    # Créer le dictionnaire d'export
    model_data = {
        "tfidf": {
            "vocabulary": vocabulary,
            "idf": idf_values,
            "max_features": 500,
            "ngram_range": [1, 2]
        },
        "svm": {
            "coef": coef,
            "intercept": intercept,
            "classes": classes
        },
        "categories": categories,
        "metadata": {
            "model_type": "TF-IDF + LinearSVC",
            "n_features": len(vocabulary),
            "n_classes": len(categories)
        }
    }

    # Sauvegarder en JSON
    output_path = Path(__file__).parent.parent.parent / "extension" / "model.json"
    print(f"\nSauvegarde en JSON: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(model_data, f, ensure_ascii=False)

    file_size = output_path.stat().st_size
    print(f"  ✓ Export terminé ({file_size / 1024:.1f} KB)")

    # Test rapide
    print("\n" + "="*70)
    print("TEST DU MODÈLE")
    print("="*70)

    test_titles = [
        "Minecraft gameplay FR #1",
        "Les dérivées expliquées simplement",
        "TOP 10 FAILS COMPILATION",
        "Incroyable astuce #shorts"
    ]

    X_test = tfidf.transform(test_titles)
    predictions = svm.predict(X_test)

    for title, pred in zip(test_titles, predictions):
        print(f"  • {title}")
        print(f"    → {pred}")

    print("\n✓ Le modèle est prêt à être utilisé dans l'extension !")


if __name__ == "__main__":
    train_and_export()
