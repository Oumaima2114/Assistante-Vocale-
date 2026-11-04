"""Script de test pour vérifier que la voix fonctionne"""
import pyttsx3

print("Initialisation du moteur de voix...")
engine = pyttsx3.init()

print("Récupération des voix disponibles...")
voices = engine.getProperty('voices')
print(f"Nombre de voix: {len(voices)}")

# Chercher la voix française
french_voice = None
for voice in voices:
    print(f"  - {voice.name}")
    if 'french' in voice.name.lower() or 'fr' in voice.id.lower() or 'hortense' in voice.name.lower():
        french_voice = voice
        print(f"    [OK] Voix francaise trouvee!")

if french_voice:
    engine.setProperty('voice', french_voice.id)
    print(f"\nVoix sélectionnée: {french_voice.name}")
else:
    print("\nAucune voix française trouvée, utilisation de la voix par défaut")

# Configuration
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

print("\n" + "="*50)
print("TEST DE LA VOIX")
print("="*50)
print("Vous devriez entendre: 'Bonjour, je suis votre assistant vocal'")
print("Si vous n'entendez rien, vérifiez:")
print("  1. Le volume de votre système Windows")
print("  2. Que les haut-parleurs/casque sont branchés")
print("  3. Que le volume n'est pas en mode muet")
print("="*50 + "\n")

try:
    engine.say("Bonjour, je suis votre assistant vocal. Si vous m'entendez, la voix fonctionne correctement !")
    engine.runAndWait()
    print("\n[OK] Test termine! Avez-vous entendu la voix?")
except Exception as e:
    print(f"\n[ERREUR] {e}")
    import traceback
    traceback.print_exc()

