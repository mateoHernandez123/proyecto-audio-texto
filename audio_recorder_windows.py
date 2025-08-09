import sounddevice as sd
import numpy as np
import wave
import time
import os
import requests
from pydub import AudioSegment
from tempfile import NamedTemporaryFile

class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.channels = 1
        self.is_recording = False
        self.recorded_frames = []
        
        # List available audio devices
        print("\nDispositivos de audio disponibles:")
        print(sd.query_devices())
        
        # Try to find the default input device
        try:
            device_info = sd.query_devices(kind='input')
            print(f"\nDispositivo de entrada por defecto: {device_info['name']}")
        except Exception as e:
            print(f"\nError al buscar dispositivo por defecto: {e}")
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream to process incoming audio data."""
        if status:
            print(f"Audio callback status: {status}")
        
        # Convert float32 audio data to int16
        audio_data = (indata * 32767).astype(np.int16)
        self.recorded_frames.append(audio_data.copy())
    
    def save_and_send_audio(self):
        """Save recorded audio to MP3 and send it to the webhook."""
        if not self.recorded_frames:
            print("No audio recorded")
            return
        
        try:
            # Save as WAV first
            with NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                with wave.open(wav_file.name, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 2 bytes for int16
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(np.concatenate(self.recorded_frames).tobytes())
            
            # Convert to MP3
            with NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
                audio = AudioSegment.from_wav(wav_file.name)
                audio.export(mp3_file.name, format="mp3")
                
                # Send to webhook
                try:
                    with open(mp3_file.name, 'rb') as f:
                        files = {'data': ('audio.mp3', f, 'audio/mpeg')}
                        response = requests.post(
                            'http://localhost:5678/webhook-test/transcribir-audio',
                            files=files
                        )
                        print(f"Audio sent to webhook. Response: {response.status_code}")
                except Exception as e:
                    print(f"Error sending audio to webhook: {e}")
                
            # Cleanup temporary files
            os.unlink(wav_file.name)
            os.unlink(mp3_file.name)
            
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def record(self, duration=5):
        """Record audio for a specified duration in seconds."""
        print(f"Recording for {duration} seconds...")
        
        self.is_recording = True
        self.recorded_frames = []
        
        try:
            with sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                dtype=np.float32
            ):
                sd.sleep(int(duration * 1000))  # Convert to milliseconds
            
            print("Recording finished. Processing audio...")
            self.save_and_send_audio()
            
        except Exception as e:
            print(f"Error during recording: {e}")
            print("Asegúrate de que tienes un micrófono conectado y funcionando")

if __name__ == "__main__":
    recorder = AudioRecorder()
    try:
        while True:
            input("\nPresiona Enter para comenzar a grabar (5 segundos) o Ctrl+C para salir...")
            recorder.record(5)
    except KeyboardInterrupt:
        print("\nGrabación finalizada.")