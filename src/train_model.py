"""Script d'entraînement du modèle d'intentions (TF-IDF + Naive Bayes)."""
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from .preprocess import preprocess_text

# Charger le dataset
data = pd.read_csv("data/dataset.csv")

# Nettoyer le texte
data["phrase"] = data["phrase"].apply(preprocess_text)

# Pipeline NLP : TF-IDF + Naive Bayes
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("model", MultinomialNB())
])

# Entraîner le modèle
pipeline.fit(data["phrase"], data["intent"])

# Sauvegarder le modèle
with open("models/intent_model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("Modèle entraîné et sauvegardé !")
