import wave
import math
import struct
import os

os.makedirs('frontend/assets', exist_ok=True)

def generate_bowl_sound(filename="frontend/assets/campana.wav", duration=4.0, sample_rate=44100):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(int(duration * sample_rate)):
            t = float(i) / sample_rate
            
            # Envelope (Fast attack, long exponential decay)
            if t < 0.05:
                env = t / 0.05
            else:
                env = math.exp(-1.2 * (t - 0.05))
                
            # Mix of frequencies for Tibetan bowl (Fundamental + Overtones)
            freq1 = 216.0 # A note
            freq2 = 216.0 * 2.82 # Overtone
            freq3 = 216.0 * 5.4  # High shimmer
            
            val = (math.sin(2 * math.pi * freq1 * t) * 0.6 + 
                   math.sin(2 * math.pi * freq2 * t) * 0.3 + 
                   math.sin(2 * math.pi * freq3 * t) * 0.1)
            
            # Apply envelope and master volume
            sample = val * env * 20000
            
            # Clipping prevention
            sample = max(-32767, min(32767, int(sample)))
            wav_file.writeframes(struct.pack('h', sample))

generate_bowl_sound()
print("Campana generada exitosamente.")
