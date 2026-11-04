"""Interface graphique moderne pour l'assistant vocal (STT + TTS)."""
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import os
import subprocess
import threading
import time
from gtts import gTTS
try:
    import pygame
    PYGAME_AVAILABLE = True
    pygame.mixer.init()
except ImportError:
    PYGAME_AVAILABLE = False
    print("[VOIX] pygame non installé, utilisation de la méthode alternative")
from src.predict import predict_intent
from src.responses import get_response

# Initialiser la voix avec paramètres français
def init_voice():
    """Initialise et configure la voix"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Chercher une voix française
        french_voice_found = False
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower() or 'hortense' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                french_voice_found = True
                print(f"[VOIX] Voix française sélectionnée: {voice.name}")
                break
        
        if not french_voice_found:
            print("[VOIX] Aucune voix française trouvée, utilisation de la voix par défaut")
        
        # Vitesse et volume
        engine.setProperty('rate', 150)  # Vitesse de parole
        engine.setProperty('volume', 0.9)  # Volume
        
        return engine
    except Exception as e:
        print(f"[VOIX] Erreur configuration: {e}")
        return None

# Lock pour éviter les appels simultanés
import threading
speak_lock = threading.Lock()

# Pas d'engine global - on en crée un nouveau à chaque fois

def speak(text):
    """Parle le texte à voix haute - UTILISE gTTS (plus fiable que pyttsx3)"""
    if not text or not text.strip():
        print("[VOIX] Texte vide, rien à dire")
        return
    
    def _speak_with_gtts():
        """Utilise gTTS pour générer et jouer la voix"""
        try:
            print(f"\n[VOIX] {'='*60}")
            print(f"[VOIX] 🗣️ DÉBUT PAROLE: '{text}'")
            print(f"[VOIX] {'='*60}")
            
            # Générer le fichier audio avec gTTS
            print("[VOIX] Génération audio avec gTTS...")
            tts = gTTS(text=text, lang='fr', slow=False)
            # Utiliser un nom de fichier unique avec timestamp pour éviter les conflits
            import time
            audio_file = f"response_temp_{int(time.time() * 1000)}.mp3"
            tts.save(audio_file)
            print("[VOIX] ✓ Audio généré")
            
            # Jouer le fichier audio SANS OUVRIR DE FENÊTRE
            print("[VOIX] 🗣️ JOUETTE AUDIO... (VOUS DEVRIEZ ENTENDRE)")
            
            if PYGAME_AVAILABLE:
                # Utiliser pygame.mixer qui joue en arrière-plan sans fenêtre
                try:
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    # Attendre que la musique se termine
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    pygame.mixer.music.stop()
                    print("[VOIX] ✓ Audio joué avec pygame")
                except Exception as e:
                    print(f"[VOIX] Erreur pygame: {e}")
                    # Fallback vers méthode alternative
                    if os.name == 'nt':
                        subprocess.Popen(
                            ['powershell', '-WindowStyle', 'Hidden', '-Command', 
                             f'$player = New-Object System.Media.SoundPlayer; $player.SoundLocation = "{os.path.abspath(audio_file)}"; $player.PlaySync()'],
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    time.sleep(len(text) * 0.1 + 1)
            else:
                # Alternative: utiliser subprocess avec fenêtre masquée
                if os.name == 'nt':  # Windows
                    # Utiliser PowerShell avec fenêtre cachée
                    subprocess.Popen(
                        ['powershell', '-WindowStyle', 'Hidden', '-Command', 
                         f'$player = New-Object System.Media.SoundPlayer; $player.SoundLocation = "{os.path.abspath(audio_file)}"; $player.PlaySync()'],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(len(text) * 0.1 + 1)
                else:  # Linux/Mac
                    subprocess.Popen(['play', audio_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(len(text) * 0.1 + 1)
            
            # Nettoyer le fichier après un délai pour s'assurer qu'il n'est plus utilisé
            try:
                time.sleep(0.5)  # Attendre un peu pour que le fichier soit libéré
                if os.path.exists(audio_file):
                    # Essayer plusieurs fois si nécessaire
                    for _ in range(5):
                        try:
                            os.remove(audio_file)
                            print("[VOIX] ✓ Fichier nettoyé")
                            break
                        except PermissionError:
                            time.sleep(0.2)
                # Nettoyer aussi les anciens fichiers
                for file in os.listdir('.'):
                    if file.startswith('response_temp_') and file.endswith('.mp3'):
                        try:
                            # Ne supprimer que les fichiers de plus de 1 minute
                            file_time = os.path.getmtime(file)
                            if time.time() - file_time > 60:
                                os.remove(file)
                        except:
                            pass
            except Exception as e:
                print(f"[VOIX] Erreur nettoyage: {e}")
            
            print(f"[VOIX] ✓ Parole terminée")
            print(f"[VOIX] {'='*60}\n")
            
        except Exception as e:
            print(f"[ERREUR VOIX] ❌ {e}")
            import traceback
            traceback.print_exc()
            
            # SECOURS: Utiliser pyttsx3 si gTTS échoue
            try:
                print("[VOIX] 🔄 Secours avec pyttsx3...")
                backup = pyttsx3.init()
                voices = backup.getProperty('voices')
                for voice in voices:
                    if 'french' in voice.name.lower() or 'hortense' in voice.name.lower():
                        backup.setProperty('voice', voice.id)
                        break
                backup.setProperty('volume', 1.0)
                backup.say(text)
                backup.runAndWait()
                backup.stop()
                print("[VOIX] ✓ Secours réussi")
            except Exception as e2:
                print(f"[VOIX] ❌ Secours échoué: {e2}")
    
    # Lancer dans un thread pour ne pas bloquer
    thread = threading.Thread(target=_speak_with_gtts, daemon=True)
    thread.start()
    print("[VOIX] Thread lancé")

def listen_and_respond():
    """Capture la voix, détecte l'intent puis affiche et lit la réponse."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        user_text.set("🎤 Écoute en cours...")
        window.update()
        
        # Ajuster le bruit ambiant
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language="fr-FR")
            user_text.set(text)
            window.update()

            # Debug: afficher le texte reconnu
            print(f"\n[DEBUG] Texte reconnu: '{text}'")
            
            intent = predict_intent(text)
            print(f"[DEBUG] Intent détecté: '{intent}'")
            
            response = get_response(intent)
            print(f"[DEBUG] Réponse: '{response}'")
            
            bot_text.set(response)
            window.update()
            
            # Forcer la mise à jour de l'interface avant de parler
            window.update_idletasks()
            
            # Afficher un indicateur visuel
            bot_text.set(f"{response} 🔊")
            window.update()

            # Parler la réponse - TOUJOURS appeler speak() à chaque fois
            print(f"\n{'='*60}")
            print(f"[APP] AVANT APPEL DE speak() - Réponse: '{response}'")
            print(f"{'='*60}")
            
            # Petit délai pour s'assurer que tout est prêt
            import time
            time.sleep(0.1)
            
            # Appeler speak() - C'EST OBLIGATOIRE À CHAQUE FOIS
            speak(response)
            
            print(f"[APP] APRÈS APPEL DE speak() (thread lancé)")
            print(f"{'='*60}\n")
            
            # Remettre le texte normal après avoir parlé
            bot_text.set(response)
            window.update()

        except sr.WaitTimeoutError:
            user_text.set("Temps d'attente dépassé")
            error_msg = "Je n'ai pas entendu, pouvez-vous répéter s'il vous plaît ?"
            bot_text.set(error_msg)
            window.update()
            speak(error_msg)
        except sr.UnknownValueError:
            user_text.set("Je n'ai pas compris")
            error_msg = "Je n'ai pas compris, pouvez-vous répéter s'il vous plaît ?"
            bot_text.set(error_msg)
            window.update()
            speak(error_msg)
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            user_text.set(error_msg)
            bot_text.set("Veuillez réessayer.")
            window.update()
            print(f"[ERREUR] Exception dans listen_and_respond: {e}")
            import traceback
            traceback.print_exc()

# Interface moderne et élégante avec nouveau design
window = tk.Tk()
window.title("🤖 Assistant Vocal Intelligent")
window.geometry("650x750")
window.configure(bg="#0d1117")  # Fond très sombre moderne

# Nouvelle palette de couleurs moderne et élégante
COLOR_BG = "#0d1117"           # Fond principal très sombre
COLOR_CARD = "#161b22"         # Cartes/cadres
COLOR_CARD_HOVER = "#1c2128"   # Hover sur cartes
COLOR_PRIMARY = "#238636"      # Vert moderne (bouton principal)
COLOR_PRIMARY_HOVER = "#2ea043" # Vert hover
COLOR_SECONDARY = "#1f6feb"    # Bleu moderne
COLOR_ACCENT = "#f85149"       # Rouge/Orange accent
COLOR_TEXT = "#c9d1d9"         # Texte principal
COLOR_TEXT_SECONDARY = "#8b949e" # Texte secondaire
COLOR_USER = "#58a6ff"         # Bleu pour utilisateur
COLOR_BOT = "#79c0ff"          # Bleu clair pour bot
COLOR_BORDER = "#30363d"       # Bordures

# Frame principal avec padding
main_frame = tk.Frame(window, bg=COLOR_BG, padx=40, pady=40)
main_frame.pack(fill=tk.BOTH, expand=True)

# Titre avec style moderne amélioré
title_frame = tk.Frame(main_frame, bg=COLOR_BG)
title_frame.pack(pady=(0, 40))

# Icône et titre
icon_title_frame = tk.Frame(title_frame, bg=COLOR_BG)
icon_title_frame.pack()

title_label = tk.Label(
    icon_title_frame,
    text="🤖",
    font=("Segoe UI", 32),
    bg=COLOR_BG
)
title_label.pack(side=tk.LEFT, padx=(0, 10))

title_text = tk.Label(
    icon_title_frame,
    text="Assistant Vocal",
    font=("Segoe UI", 28, "bold"),
    fg=COLOR_TEXT,
    bg=COLOR_BG
)
title_text.pack(side=tk.LEFT)

subtitle_label = tk.Label(
    title_frame,
    text="Parlez naturellement, je vous écoute et vous réponds",
    font=("Segoe UI", 11),
    fg=COLOR_TEXT_SECONDARY,
    bg=COLOR_BG
)
subtitle_label.pack(pady=(10, 0))

# Frame pour les messages utilisateur avec style carte
user_frame = tk.Frame(main_frame, bg=COLOR_CARD, relief=tk.FLAT, bd=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
user_frame.pack(fill=tk.X, pady=(0, 20))

user_header = tk.Frame(user_frame, bg=COLOR_CARD)
user_header.pack(fill=tk.X, padx=20, pady=(20, 10))

tk.Label(
    user_header,
    text="👤 Vous",
    font=("Segoe UI", 11, "bold"),
    fg=COLOR_USER,
    bg=COLOR_CARD
).pack(side=tk.LEFT)

tk.Label(
    user_header,
    text="avez dit :",
    font=("Segoe UI", 10),
    fg=COLOR_TEXT_SECONDARY,
    bg=COLOR_CARD
).pack(side=tk.LEFT, padx=(5, 0))

user_text = tk.StringVar()
user_text.set("En attente de votre voix...")
user_label = tk.Label(
    user_frame,
    textvariable=user_text,
    font=("Segoe UI", 13),
    fg=COLOR_TEXT,
    bg=COLOR_CARD,
    wraplength=520,
    justify=tk.LEFT,
    anchor=tk.W
)
user_label.pack(fill=tk.X, padx=20, pady=(0, 20))

# Frame pour les réponses de l'assistant avec style carte
bot_frame = tk.Frame(main_frame, bg=COLOR_CARD, relief=tk.FLAT, bd=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
bot_frame.pack(fill=tk.X, pady=(0, 30))

bot_header = tk.Frame(bot_frame, bg=COLOR_CARD)
bot_header.pack(fill=tk.X, padx=20, pady=(20, 10))

tk.Label(
    bot_header,
    text="🤖 Assistant",
    font=("Segoe UI", 11, "bold"),
    fg=COLOR_BOT,
    bg=COLOR_CARD
).pack(side=tk.LEFT)

tk.Label(
    bot_header,
    text="répond :",
    font=("Segoe UI", 10),
    fg=COLOR_TEXT_SECONDARY,
    bg=COLOR_CARD
).pack(side=tk.LEFT, padx=(5, 0))

bot_text = tk.StringVar()
bot_text.set("En attente...")
bot_label = tk.Label(
    bot_frame,
    textvariable=bot_text,
    font=("Segoe UI", 13),
    fg=COLOR_TEXT,
    bg=COLOR_CARD,
    wraplength=520,
    justify=tk.LEFT,
    anchor=tk.W
)
bot_label.pack(fill=tk.X, padx=20, pady=(0, 20))

# Boutons avec style moderne amélioré
button_frame = tk.Frame(main_frame, bg=COLOR_BG)
button_frame.pack(pady=30)

def on_speak_hover(event):
    speak_button.config(bg=COLOR_PRIMARY_HOVER, cursor="hand2")

def on_speak_leave(event):
    speak_button.config(bg=COLOR_PRIMARY, cursor="")

def on_test_hover(event):
    test_button.config(bg="#2563eb", cursor="hand2")

def on_test_leave(event):
    test_button.config(bg=COLOR_SECONDARY, cursor="")

# Bouton principal - grand et visible
speak_button = tk.Button(
    button_frame,
    text="🎙️  Parler",
    font=("Segoe UI", 18, "bold"),
    bg=COLOR_PRIMARY,
    fg="#ffffff",
    activebackground=COLOR_PRIMARY_HOVER,
    activeforeground="#ffffff",
    relief=tk.FLAT,
    bd=0,
    padx=50,
    pady=18,
    cursor="hand2",
    command=listen_and_respond
)
speak_button.pack(pady=(0, 15))
speak_button.bind("<Enter>", on_speak_hover)
speak_button.bind("<Leave>", on_speak_leave)

# Bouton de test avec style secondaire
def test_voice():
    """Teste la voix directement"""
    print("[TEST] Test de la voix...")
    speak("Test de la voix. Si vous m'entendez, la voix fonctionne correctement !")
    bot_text.set("Test de la voix effectué. Avez-vous entendu la voix ?")

test_button = tk.Button(
    button_frame,
    text="🔊  Tester la voix",
    font=("Segoe UI", 12),
    bg=COLOR_SECONDARY,
    fg="#ffffff",
    activebackground="#2563eb",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    bd=0,
    padx=30,
    pady=12,
    cursor="hand2",
    command=test_voice
)
test_button.pack()
test_button.bind("<Enter>", on_test_hover)
test_button.bind("<Leave>", on_test_leave)

# Footer avec informations stylisées
footer_frame = tk.Frame(main_frame, bg=COLOR_BG)
footer_frame.pack(side=tk.BOTTOM, pady=(30, 0))

footer_line = tk.Frame(footer_frame, bg=COLOR_BORDER, height=1, width=500)
footer_line.pack(pady=(0, 15))

footer = tk.Label(
    footer_frame,
    text="💡 Cliquez sur 'Parler' et exprimez-vous naturellement",
    font=("Segoe UI", 10),
    fg=COLOR_TEXT_SECONDARY,
    bg=COLOR_BG
)
footer.pack()

window.mainloop()
