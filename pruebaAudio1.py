import openai
import os
import wave
import pyaudio
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la API Key. Asegúrate de configurar OPENAI_API_KEY en el archivo .env")

# Crear cliente OpenAI
client = OpenAI(api_key=api_key)

# Configuración de grabación
FORMAT = pyaudio.paInt16  # Formato de audio
CHANNELS = 1  # Mono
RATE = 44100  # Frecuencia de muestreo
CHUNK = 1024  # Tamaño del buffer
RECORD_SECONDS = 5  # Duración de la grabación
WAVE_OUTPUT_FILENAME = "audio.wav"

# Iniciar grabación
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Grabando audio...")
frames = []

for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Grabación finalizada")

# Detener y cerrar el stream
stream.stop_stream()
stream.close()
audio.terminate()

# Guardar el audio en un archivo WAV
wavefile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wavefile.setnchannels(CHANNELS)
wavefile.setsampwidth(audio.get_sample_size(FORMAT))
wavefile.setframerate(RATE)
wavefile.writeframes(b''.join(frames))
wavefile.close()

# Enviar el archivo de audio a OpenAI Whisper
with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

# Mostrar el texto transcrito
print("\nTexto transcrito:")
print(transcript)

# Eliminar el archivo WAV después de la transcripción
os.remove(WAVE_OUTPUT_FILENAME)
print(f"Archivo {WAVE_OUTPUT_FILENAME} eliminado.")