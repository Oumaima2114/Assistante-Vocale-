"""Nettoyage basique du texte avant vectorisation."""
import nltk
import re
from nltk.tokenize import word_tokenize

# Télécharger le tokenizer Punkt (une seule fois)
nltk.download('punkt')

def preprocess_text(text):
    """
    Nettoie une phrase pour le NLP.
    - Minuscules
    - Suppression de la ponctuation
    - Découpage en mots (tokenisation)
    - Normalisation des accents et caractères spéciaux
    - Gestion des variations de la reconnaissance vocale
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    
    # Normaliser les variations communes de la reconnaissance vocale
    # "est-il" -> "est il", "est-ce" -> "est ce", etc.
    text = text.replace("-", " ")
    text = text.replace("'", " ")
    text = text.replace("'", " ")
    text = text.replace('"', " ")
    
    # Supprimer la ponctuation mais garder les espaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    try:
        tokens = word_tokenize(text, language='french')
        result = " ".join(tokens)
        return result
    except:
        # Fallback si tokenization échoue
        return text

# Test rapide
if __name__ == "__main__":
    print(preprocess_text("Bonjour, quelle heure est-il ?"))
