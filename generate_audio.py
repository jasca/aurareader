from gtts import gTTS
import os

os.makedirs('frontend/assets', exist_ok=True)

texts = {
    'inicio.mp3': 'Comencemos. Ubícate en el centro y relájate.',
    'inhala.mp3': 'Inhala',
    'exhala.mp3': 'Exhala'
}

for filename, text in texts.items():
    tts = gTTS(text=text, lang='es', slow=False)
    tts.save(f'frontend/assets/{filename}')
    print(f'Generated {filename}')
