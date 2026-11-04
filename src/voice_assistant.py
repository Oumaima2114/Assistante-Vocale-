"""Assistant vocal en ligne de commande (STT + TTS + intents)."""
import speech_recognition as sr
from gtts import gTTS
import os
from .predict import predict_intent
from .responses import get_response

recognizer = sr.Recognizer()

def speak(text):
    """
    Transforme le texte en voix (Text-To-Speech)
    """
    tts = gTTS(text=text, lang='fr')
    tts.save("response.mp3")
    os.system("start response.mp3")  # Windows

def listen():
    """
    Écoute la voix de l'utilisateur et retourne du texte (Speech-To-Text)
    """
    with sr.Microphone() as source:
        print("🎙️ Parlez...")
        # Ajuster le bruit ambiant
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )
            text = recognizer.recognize_google(audio, language="fr-FR")
            print("Tu as dit :", text)
            return text
        except sr.WaitTimeoutError:
            print("Temps d'attente dépassé")
            return ""
        except sr.UnknownValueError:
            print("Je n'ai pas compris")
            return ""
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return ""

print("Assistant vocal prêt ! Dites 'quitter' pour arrêter.")

while True:
    user_text = listen()
    
    if user_text.lower() == "quitter":
        speak("Au revoir")
        break
    
    intent = predict_intent(user_text)
    response = get_response(intent)
    
    print("Assistant :", response)
    speak(response)
