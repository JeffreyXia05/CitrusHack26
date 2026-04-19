
import io
import pygame
import threading
from elevenlabs.client import ElevenLabs

class VoiceManager:
    def __init__(self, api_key):
        self.client = ElevenLabs(api_key=api_key)
        #initialize mixer with error handling
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
            print("Mixer initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize mixer: {e}")

    def say(self, text):
        """Generic method to speak any text provided."""
        threading.Thread(target=self._generate_and_play, args=(text,), daemon=True).start()

    def _generate_and_play(self, text):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            audio_gen = self.client.text_to_speech.convert(
                text=text,
                voice_id="pFZP5JQG7iQjIQuC4Bku",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            audio_bytes = b"".join(list(audio_gen))
            
            if not audio_bytes:
                return

            sound_file = io.BytesIO(audio_bytes)
            sound_file.seek(0)
            
            # enable mixer to run from memory
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except Exception as e:
            print(f"ElevenLabs Error: {e}")
    