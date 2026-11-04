"""Boucle principale en mode texte pour l'assistant NLP."""
from .predict import predict_intent
from .responses import get_response

# Interaction console simple
print("Assistant NLP prêt ! Tapez 'exit' pour quitter.")

while True:
    user_input = input("Vous : ")
    if user_input.lower() == "exit":
        print("Assistant : Au revoir !")
        break
    
    intent = predict_intent(user_input)
    response = get_response(intent)
    print("Assistant :", response)
