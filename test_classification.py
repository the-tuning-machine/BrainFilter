import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

# Charger les données
df = pd.read_csv('data/raw/youtube_titles.csv')

# Entraîner TF-IDF
tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2), lowercase=True, strip_accents='unicode')
X = tfidf.fit_transform(df['title'].values)
y = df['category'].values

# Entraîner SVM
svm = LinearSVC(C=1.0, random_state=42, max_iter=10000)
svm.fit(X, y)

# Tester avec des titres
test_titles = [
    "Incroyable astuce #shorts",
    "Wait for it... #shorts",
    "POV: Tu es étudiant #shorts",
    "Minecraft gameplay FR #1",
    "TOP 10 FAILS COMPILATION",
    "SQUAT - Technique parfaite",
    "Les dérivées expliquées simplement"
]

print("--- Test de classification ---")
for title in test_titles:
    X_test = tfidf.transform([title])
    pred = svm.predict(X_test)[0]
    print(f"{title:50s} → {pred}")
