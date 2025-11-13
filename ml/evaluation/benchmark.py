"""
Script de benchmark pour comparer différentes méthodes de classification.
Mesure à la fois la performance (accuracy, F1) et le temps d'inférence.
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


class ModelBenchmark:
    """Classe pour benchmarker un modèle de classification."""

    def __init__(self, model, name):
        """
        Args:
            model: Modèle sklearn-compatible avec fit() et predict()
            name: Nom du modèle pour l'affichage
        """
        self.model = model
        self.name = name
        self.metrics = {}

    def train(self, X_train, y_train):
        """Entraîne le modèle et mesure le temps d'entraînement."""
        print(f"\n[{self.name}] Entraînement...")
        start = time.time()
        self.model.fit(X_train, y_train)
        train_time = time.time() - start
        self.metrics['train_time'] = train_time
        print(f"  ✓ Temps d'entraînement: {train_time:.3f}s")

    def evaluate(self, X_val, y_val):
        """Évalue le modèle et mesure le temps d'inférence."""
        print(f"[{self.name}] Évaluation...")

        # Mesurer le temps d'inférence total
        start = time.time()
        y_pred = self.model.predict(X_val)
        inference_time = time.time() - start

        # Calculer le temps moyen par échantillon
        avg_inference_time = inference_time / len(X_val)

        # Calculer les métriques de performance
        accuracy = accuracy_score(y_val, y_pred)
        f1_macro = f1_score(y_val, y_pred, average='macro')
        f1_weighted = f1_score(y_val, y_pred, average='weighted')

        # Stocker les métriques
        self.metrics.update({
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
            'inference_time_total': inference_time,
            'inference_time_avg': avg_inference_time,
            'inference_time_per_1000': avg_inference_time * 1000,
        })

        print(f"  ✓ Accuracy: {accuracy:.4f}")
        print(f"  ✓ F1 (macro): {f1_macro:.4f}")
        print(f"  ✓ F1 (weighted): {f1_weighted:.4f}")
        print(f"  ✓ Temps inférence total: {inference_time:.3f}s")
        print(f"  ✓ Temps moyen par sample: {avg_inference_time*1000:.2f}ms")
        print(f"  ✓ Temps pour 1000 samples: {self.metrics['inference_time_per_1000']:.2f}ms")

        return y_pred

    def get_classification_report(self, y_val, y_pred):
        """Génère un rapport de classification détaillé."""
        return classification_report(y_val, y_pred)

    def plot_confusion_matrix(self, y_val, y_pred, output_dir):
        """Crée une matrice de confusion."""
        cm = confusion_matrix(y_val, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Matrice de confusion - {self.name}')
        plt.ylabel('Vraie classe')
        plt.xlabel('Classe prédite')

        output_path = output_dir / f'confusion_matrix_{self.name.replace(" ", "_")}.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Matrice de confusion sauvegardée: {output_path}")


class BenchmarkRunner:
    """Gère l'exécution de benchmarks pour plusieurs modèles."""

    def __init__(self, output_dir):
        """
        Args:
            output_dir: Dossier pour sauvegarder les résultats
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def run(self, models, X_train, X_val, y_train, y_val):
        """
        Exécute le benchmark sur tous les modèles.

        Args:
            models: Liste de tuples (model, name)
            X_train, X_val: Features d'entraînement et validation
            y_train, y_val: Labels d'entraînement et validation
        """
        print("="*70)
        print("BENCHMARK DE CLASSIFICATION")
        print("="*70)

        for model, name in models:
            benchmark = ModelBenchmark(model, name)

            # Entraînement
            benchmark.train(X_train, y_train)

            # Évaluation
            y_pred = benchmark.evaluate(X_val, y_val)

            # Rapport détaillé
            print(f"\n[{name}] Rapport de classification:")
            print(benchmark.get_classification_report(y_val, y_pred))

            # Matrice de confusion
            benchmark.plot_confusion_matrix(y_val, y_pred, self.output_dir)

            # Stocker les résultats
            self.results.append({
                'model': name,
                **benchmark.metrics
            })

        # Créer un rapport comparatif
        self._create_comparison_report()

    def _create_comparison_report(self):
        """Crée un rapport comparatif de tous les modèles."""
        df = pd.DataFrame(self.results)

        # Trier par F1 score (weighted)
        df = df.sort_values('f1_weighted', ascending=False)

        print("\n" + "="*70)
        print("RAPPORT COMPARATIF")
        print("="*70)
        print(df.to_string(index=False))

        # Sauvegarder en CSV
        csv_path = self.output_dir / 'benchmark_results.csv'
        df.to_csv(csv_path, index=False)
        print(f"\n✓ Résultats sauvegardés: {csv_path}")

        # Créer un graphique comparatif
        self._plot_comparison(df)

        # Identifier le meilleur modèle
        self._recommend_model(df)

    def _plot_comparison(self, df):
        """Crée un graphique comparatif des modèles."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Accuracy
        axes[0, 0].barh(df['model'], df['accuracy'])
        axes[0, 0].set_xlabel('Accuracy')
        axes[0, 0].set_title('Accuracy par modèle')
        axes[0, 0].set_xlim([0, 1])

        # F1 Score (weighted)
        axes[0, 1].barh(df['model'], df['f1_weighted'])
        axes[0, 1].set_xlabel('F1 Score (weighted)')
        axes[0, 1].set_title('F1 Score par modèle')
        axes[0, 1].set_xlim([0, 1])

        # Temps d'entraînement
        axes[1, 0].barh(df['model'], df['train_time'])
        axes[1, 0].set_xlabel('Temps (secondes)')
        axes[1, 0].set_title('Temps d\'entraînement')

        # Temps d'inférence (pour 1000 samples)
        axes[1, 1].barh(df['model'], df['inference_time_per_1000'])
        axes[1, 1].set_xlabel('Temps (ms)')
        axes[1, 1].set_title('Temps d\'inférence (1000 samples)')

        plt.tight_layout()
        output_path = self.output_dir / 'model_comparison.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Graphique comparatif sauvegardé: {output_path}")

    def _recommend_model(self, df):
        """Recommande le meilleur modèle en fonction des métriques."""
        print("\n" + "="*70)
        print("RECOMMANDATION")
        print("="*70)

        # Le meilleur modèle par F1 score
        best_f1 = df.iloc[0]
        print(f"\n🏆 Meilleur F1 Score: {best_f1['model']}")
        print(f"   - F1 (weighted): {best_f1['f1_weighted']:.4f}")
        print(f"   - Accuracy: {best_f1['accuracy']:.4f}")
        print(f"   - Temps inférence (1000 samples): {best_f1['inference_time_per_1000']:.2f}ms")

        # Le modèle le plus rapide avec performance acceptable
        # On considère "acceptable" comme étant au moins 95% du meilleur F1
        threshold = best_f1['f1_weighted'] * 0.95
        acceptable_models = df[df['f1_weighted'] >= threshold]
        fastest = acceptable_models.sort_values('inference_time_per_1000').iloc[0]

        if fastest['model'] != best_f1['model']:
            print(f"\n⚡ Modèle le plus rapide (performance acceptable):")
            print(f"   Modèle: {fastest['model']}")
            print(f"   - F1 (weighted): {fastest['f1_weighted']:.4f} ({(fastest['f1_weighted']/best_f1['f1_weighted']*100):.1f}% du meilleur)")
            print(f"   - Temps inférence (1000 samples): {fastest['inference_time_per_1000']:.2f}ms")
            print(f"   - Gain de vitesse: {(best_f1['inference_time_per_1000']/fastest['inference_time_per_1000']):.1f}x")

        # Analyse du rapport performance/vitesse
        print(f"\n💡 Analyse:")
        for _, row in df.iterrows():
            perf_ratio = row['f1_weighted'] / best_f1['f1_weighted']
            speed_ratio = fastest['inference_time_per_1000'] / row['inference_time_per_1000']

            if perf_ratio < 0.90:
                print(f"   - {row['model']}: Performance insuffisante ({perf_ratio*100:.1f}% du meilleur)")
            elif speed_ratio < 0.5:
                print(f"   - {row['model']}: Trop lent ({speed_ratio*100:.1f}% de la vitesse du plus rapide)")
            else:
                print(f"   - {row['model']}: Bon équilibre performance/vitesse ✓")


def load_data(data_path):
    """
    Charge le dataset et le divise en train/val.

    Args:
        data_path: Chemin vers le fichier CSV

    Returns:
        X_train, X_val, y_train, y_val, label_names
    """
    df = pd.read_csv(data_path)

    # Split train/val (80/20)
    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df['category']
    )

    # Extraire les titres et les catégories
    X_train = train_df['title'].values
    y_train = train_df['category'].values
    X_val = val_df['title'].values
    y_val = val_df['category'].values

    label_names = sorted(df['category'].unique())

    print(f"Dataset chargé:")
    print(f"  - Train: {len(X_train)} échantillons")
    print(f"  - Validation: {len(X_val)} échantillons")
    print(f"  - Catégories: {len(label_names)}")

    return X_train, X_val, y_train, y_val, label_names


if __name__ == "__main__":
    # Ce fichier sera importé par les scripts de test spécifiques
    pass
