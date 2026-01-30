import wave
import pyaudio
import time
import numpy as np
from io import BytesIO
from collections import deque

class AudioSystem:
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.chunk = 1024
        self.audio_buffer = deque(maxlen=10)
        
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        try:
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            for _ in range(0, int(self.sample_rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to WAV buffer
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            wav_buffer.seek(0)
            return wav_buffer
            
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return None
    
    def play_audio(self, audio_bytes):
        """Play audio from bytes"""
        try:
            if isinstance(audio_bytes, BytesIO):
                audio_bytes.seek(0)
                audio_data = audio_bytes.read()
            else:
                audio_data = audio_bytes
            
            p = pyaudio.PyAudio()
            
            # Open stream for playback
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            return True
            
        except Exception as e:
            print(f"❌ Playback failed: {e}")
            return False
    
    def generate_beep_sound(self, frequency=440, duration=1.0):
        """Generate a beep sound (compatible with previous naming)"""
        return self.generate_beep(frequency, duration)

    def generate_beep(self, frequency=440, duration=1.0):
        """Generate a beep sound"""
        try:
            samples = int(self.sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(frequency * t * 2 * np.pi)
            
            # Convert to 16-bit PCM
            audio = (tone * 32767).astype(np.int16)
            
            # Create WAV file in memory
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio.tobytes())
            
            wav_buffer.seek(0)
            return wav_buffer
            
        except Exception as e:
            print(f"❌ Beep generation failed: {e}")
            return None

    def text_to_speech(self, text, language='en'):
        """Simulate TTS with a beep for now (as in new script)"""
        return self.generate_beep()
