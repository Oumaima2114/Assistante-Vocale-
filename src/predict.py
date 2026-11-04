"""Chargement et prédiction d'intentions via le modèle entraîné."""
import pickle
import os
from .preprocess import preprocess_text

# Charger le modèle une seule fois au démarrage
model_path = "models/intent_model.pkl"
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
else:
    model = None
    print(" ATTENTION: Le modèle n'existe pas! Exécutez: python -m src.train_model")

def predict_intent(text):
    """Prédit l'intention à partir d'un texte brut nettoyé."""
    if model is None:
        return "unknown"
    
    if not text or not text.strip():
        return "unknown"
    
    try:
        text_processed = preprocess_text(text)
        print(f"[DEBUG] Texte préprocessé: {text_processed}")

        proba = model.predict_proba([text_processed])[0]
        max_proba = max(proba)
        predicted_intent = model.predict([text_processed])[0]
        
        print(f"[DEBUG] Probabilités: {dict(zip(model.classes_, proba))}")
        print(f"[DEBUG] Probabilité max: {max_proba:.3f}, Intent: {predicted_intent}")

        # Seuil réduit pour être plus tolérant avec un petit dataset
        # Avec un petit dataset, on accepte même des probabilités faibles
        if max_proba < 0.10:
            print(f"[DEBUG] Probabilité trop faible ({max_proba:.3f}), retourne 'unknown'")
            return "unknown"

        return predicted_intent
    except Exception as e:
        print(f"[DEBUG] Erreur lors de la prédiction: {e}")
        return "unknown"
