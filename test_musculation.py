import json
from sklearn.feature_extraction.text import TfidfVectorizer

# Charger le modèle
with open('extension/model.json', 'r') as f:
    model = json.load(f)

print("Classes:", model['svm']['classes'])
print("Nombre de classes:", len(model['svm']['classes']))

# Tester avec des titres de musculation
test_titles = [
    "SQUAT - Technique parfaite",
    "PROGRAMME PRISE DE MASSE",
    "10 exercices pour les PECS",
    "ENTRAÎNEMENT DOS INTENSE 💪",
    "MA TRANSFORMATION 6 MOIS",
]

# Créer le vectorizer avec le vocabulaire du modèle
vocab = model['tfidf']['vocabulary']
idf = model['tfidf']['idf']

# Simuler la prédiction (version simplifiée)
print("\n--- Test de titres musculation ---")
for title in test_titles:
    print(f"  • {title}")
    # Le modèle devrait classer ces titres en "musculation"
