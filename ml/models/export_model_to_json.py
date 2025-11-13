"""
Exporte le modèle TF-IDF + SVM en format JSON pour JavaScript.
"""
import json
from pathlib import Path
import joblib
import numpy as np


def export_model_to_json():
    """Exporte le modèle en format JSON."""
    print("="*70)
    print("EXPORT DU MODÈLE EN JSON")
    print("="*70)

    # Charger le modèle
    model_path = Path(__file__).parent.parent.parent / "data" / "models" / "youtube_classifier.pkl"
    categories_path = Path(__file__).parent.parent.parent / "data" / "models" / "categories.pkl"

    print(f"\nChargement du modèle: {model_path}")
    model = joblib.load(model_path)
    categories = joblib.load(categories_path)

    # Extraire les composants
    tfidf = model.named_steps['embedding'].vectorizer
    svm = model.named_steps['classifier']

    print("  ✓ Modèle chargé")

    # Extraire les paramètres TF-IDF
    vocabulary = tfidf.vocabulary_
    idf_values = tfidf.idf_.tolist()

    # Extraire les paramètres SVM
    # Pour un SVM linéaire, on a besoin de:
    # - support_vectors: les vecteurs de support
    # - dual_coef: les coefficients duaux
    # - intercept: le biais
    # - classes: les classes

    support_vectors = svm.support_vectors_.tolist()
    dual_coef = svm.dual_coef_.tolist()
    intercept = svm.intercept_.tolist()
    classes = svm.classes_.tolist()

    # Créer le dictionnaire d'export
    model_data = {
        "tfidf": {
            "vocabulary": vocabulary,
            "idf": idf_values,
            "max_features": 500,
            "ngram_range": [1, 2]
        },
        "svm": {
            "support_vectors": support_vectors,
            "dual_coef": dual_coef,
            "intercept": intercept,
            "classes": classes
        },
        "categories": categories,
        "metadata": {
            "model_type": "TF-IDF + SVM-Linear",
            "n_features": len(vocabulary),
            "n_classes": len(categories),
            "n_support_vectors": len(support_vectors)
        }
    }

    # Sauvegarder en JSON
    output_path = Path(__file__).parent.parent.parent / "extension" / "model.json"
    print(f"\nSauvegarde en JSON: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(model_data, f, ensure_ascii=False, indent=2)

    print("  ✓ Export terminé")

    # Afficher les statistiques
    print("\n" + "="*70)
    print("STATISTIQUES")
    print("="*70)
    print(f"  - Vocabulaire: {len(vocabulary)} mots")
    print(f"  - Vecteurs de support: {len(support_vectors)}")
    print(f"  - Classes: {len(categories)}")
    print(f"  - Taille du fichier: {output_path.stat().st_size / 1024:.1f} KB")

    print("\n✓ Le modèle est prêt à être utilisé dans l'extension !")


if __name__ == "__main__":
    export_model_to_json()
