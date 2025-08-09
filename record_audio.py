import sounddevice as sd
import numpy as np
import wave
import time
import os
import requests
from pydub import AudioSegment
import tempfile

def record_audio(filename, duration=5, samplerate=44100):
    print(f"Grabando durante {duration} segundos...")
    
    # Mostrar dispositivos disponibles
    print("\nDispositivos de audio disponibles:")
    print(sd.query_devices())
    
    # Grabar audio
    recording = sd.rec(
        int(samplerate * duration),
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )
    
    # Esperar hasta que la grabación termine
    sd.wait()
    
    # Convertir a int16
    audio_data = (recording * 32767).astype(np.int16)
    
    # Guardar como WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    print(f"Audio guardado como {filename}")
    return filename

def convert_to_mp3(wav_file, mp3_file):
    print("Convirtiendo a MP3...")
    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format="mp3")
    print(f"MP3 guardado como {mp3_file}")

def send_to_webhook(mp3_file):
    print("Enviando audio al webhook...")
    try:
        with open(mp3_file, 'rb') as f:
            files = {'data': ('audio.mp3', f, 'audio/mpeg')}
            response = requests.post(
                'http://localhost:5678/webhook-test/transcribir-audio',
                files=files
            )
            print(f"Respuesta del servidor: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar el audio: {e}")

def main():
    try:
        # Crear directorio temporal si no existe
        temp_dir = "temp_audio"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        while True:
            input("\nPresiona Enter para comenzar a grabar (5 segundos) o Ctrl+C para salir...")
            
            # Nombres de archivos temporales
            wav_file = os.path.join(temp_dir, "temp_recording.wav")
            mp3_file = os.path.join(temp_dir, "temp_recording.mp3")
            
            try:
                # Grabar audio
                record_audio(wav_file)
                
                # Convertir a MP3
                convert_to_mp3(wav_file, mp3_file)
                
                # Enviar al webhook
                send_to_webhook(mp3_file)
                
                # Limpiar archivos temporales
                if os.path.exists(wav_file):
                    os.remove(wav_file)
                if os.path.exists(mp3_file):
                    os.remove(mp3_file)
                    
            except Exception as e:
                print(f"\nError durante el proceso: {e}")
                print("Asegúrate de que:")
                print("1. Tienes un micrófono conectado y funcionando")
                print("2. FFmpeg está instalado correctamente")
                print("3. El servidor webhook está funcionando")
    
    except KeyboardInterrupt:
        print("\nGrabación finalizada.")
        # Limpiar archivos temporales al salir
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)

if __name__ == "__main__":
    main()
