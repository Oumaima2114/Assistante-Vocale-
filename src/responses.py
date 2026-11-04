"""Réponses textuelles statiques pour chaque intention détectée."""
from datetime import datetime
import random

def get_response(intent):
    """
    Retourne une réponse selon l'intention détectée
    """
    if intent == "greeting":
        responses = [
            "Bonjour, comment puis-je vous aider ?",
            "Salut ! Que puis-je faire pour vous ?",
            "Bonjour ! Je suis là pour vous aider.",
            "Salut, comment allez-vous ?"
        ]
        return random.choice(responses)
    
    elif intent == "time":
        return datetime.now().strftime("Il est %H:%M")
    
    elif intent == "date":
        return datetime.now().strftime("Nous sommes le %d/%m/%Y")
    
    elif intent == "weather":
        responses = [
            "Je ne peux pas accéder à la météo en temps réel, mais je peux vous aider autrement !",
            "Désolé, je n'ai pas accès aux informations météorologiques pour le moment.",
            "Je ne peux pas vous donner la météo, mais je peux vous donner l'heure ou la date !"
        ]
        return random.choice(responses)
    
    elif intent == "joke":
        jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau !",
            "Qu'est-ce qui est jaune et qui attend ? Jonathan !",
            "Pourquoi les poissons n'aiment-ils pas l'informatique ? Parce qu'ils ont peur de l'Internet !",
            "Qu'est-ce qui est petit, marron et qui monte et descend ? Un marron dans un ascenseur !",
            "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que sinon ils tombent dans le bateau !"
        ]
        return random.choice(jokes)
    
    elif intent == "how_are_you":
        responses = [
            "Je vais très bien, merci ! Et vous ?",
            "Ça va super bien, merci de demander !",
            "Je suis en pleine forme ! Comment allez-vous ?",
            "Parfaitement bien, merci !"
        ]
        return random.choice(responses)
    
    elif intent == "who_are_you":
        responses = [
            "Je suis votre assistant vocal intelligent ! Je peux vous aider avec diverses tâches.",
            "Je suis un assistant virtuel créé pour vous aider. Mon nom n'est pas important, mais je suis là pour vous !",
            "Je suis votre assistant personnel. Je peux répondre à vos questions et vous aider !"
        ]
        return random.choice(responses)
    
    elif intent == "help":
        return "Je peux vous donner l'heure, la date, raconter des blagues, répondre à vos questions et bien plus encore ! Que souhaitez-vous savoir ?"
    
    elif intent == "thanks":
        responses = [
            "De rien, c'est un plaisir !",
            "Je vous en prie !",
            "Avec plaisir !",
            "Pas de problème, content de vous aider !"
        ]
        return random.choice(responses)
    
    elif intent == "youre_welcome":
        return "C'est normal, je suis là pour ça !"
    
    elif intent == "love":
        responses = [
            "Merci beaucoup, c'est très gentil !",
            "Vous êtes très aimable, merci !",
            "C'est adorable de votre part, merci !"
        ]
        return random.choice(responses)
    
    elif intent == "compliment":
        responses = [
            "Merci beaucoup, c'est très gentil !",
            "Vous êtes très aimable !",
            "Merci, ça me fait plaisir !"
        ]
        return random.choice(responses)
    
    elif intent == "goodbye":
        responses = [
            "Au revoir, à bientôt !",
            "À très bientôt !",
            "Au revoir, passez une bonne journée !",
            "Salut, à plus tard !"
        ]
        return random.choice(responses)
    
    else:
        return "Désolé, je n'ai pas compris votre demande. Pouvez-vous reformuler ?"