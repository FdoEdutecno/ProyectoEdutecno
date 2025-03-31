import openai
import os
import pyaudio
import wave
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la API Key. Asegúrate de configurar OPENAI_API_KEY en el archivo .env")

# Configuración de grabación
FORMAT = pyaudio.paInt16 # Formato de audio
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
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

# 🔹 Llamada a OpenAI Whisper
with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )

# Mostrar el texto transcrito
print("\nTexto transcrito:")
print(transcript["text"])
