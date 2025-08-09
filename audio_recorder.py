import sounddevice as sd
import numpy as np
import webrtcvad
import wave
import time
import os
import requests
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from queue import Queue
import threading

class AudioRecorder:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # ms
        self.frame_length = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(3)  # Aggressiveness level 3 (max)
        self.audio_queue = Queue()
        self.is_recording = False
        self.silence_timeout = 1.0  # seconds of silence before stopping
        self.last_speech_detected = 0
        self.recorded_frames = []
        
    def is_speech(self, buffer):
        """Check if the audio buffer contains speech."""
        return self.vad.is_speech(buffer.tobytes(), self.sample_rate)
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream to process incoming audio data."""
        if status:
            print(f"Audio callback status: {status}")
        
        # Convert float32 audio data to int16 for VAD
        audio_data = (indata * 32767).astype(np.int16)
        self.audio_queue.put(audio_data.copy())
    
    def process_audio(self):
        """Process audio data from the queue and detect speech."""
        while self.is_recording:
            if not self.audio_queue.empty():
                audio_data = self.audio_queue.get()
                
                # Check for speech
                if self.is_speech(audio_data):
                    self.last_speech_detected = time.time()
                    self.recorded_frames.append(audio_data)
                else:
                    # If we have recorded something and silence threshold is exceeded
                    if self.recorded_frames and \
                       (time.time() - self.last_speech_detected) > self.silence_timeout:
                        self.stop_recording()
                        break
                    elif self.recorded_frames:
                        self.recorded_frames.append(audio_data)
    
    def save_and_send_audio(self):
        """Save recorded audio to MP3 and send it to the webhook."""
        if not self.recorded_frames:
            print("No audio recorded")
            return
        
        # Save as WAV first
        with NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            with wave.open(wav_file.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
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
    
    def start_recording(self):
        """Start recording audio from microphone."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recorded_frames = []
        self.last_speech_detected = 0
        
        # Start audio processing thread
        self.process_thread = threading.Thread(target=self.process_audio)
        self.process_thread.start()
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=self.audio_callback,
            dtype=np.float32,
            blocksize=self.frame_length
        )
        self.stream.start()
        print("Started recording... Speak now!")
    
    def stop_recording(self):
        """Stop recording and process the audio."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.process_thread.join()
        
        print("Recording stopped. Processing audio...")
        self.save_and_send_audio()

if __name__ == "__main__":
    recorder = AudioRecorder()
    try:
        recorder.start_recording()
        # Keep the main thread running
        while recorder.is_recording:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.stop_recording()
