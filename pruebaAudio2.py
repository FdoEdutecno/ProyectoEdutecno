import openai
import os
import wave
import pyaudio
import simpleaudio as sa
from dotenv import load_dotenv
from playsound import playsound

# Cargar variables de entorno (.env)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la API Key. Asegúrate de configurar OPENAI_API_KEY en el archivo .env")

# Configuración de grabación
FORMAT = pyaudio.paInt16  # Formato de audio
CHANNELS = 1  # Mono
RATE = 44100  # Frecuencia de muestreo
CHUNK = 1024  # Tamaño del buffer
RECORD_SECONDS = 5  # Duración de la grabación
WAVE_OUTPUT_FILENAME = "audio.wav"

# Iniciar grabación
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Habla ahora...")
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

# Enviar el audio a OpenAI Whisper para transcripción
with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

print("\n Texto transcrito:")
print(transcript)

# Enviar la pregunta transcrita a GPT-4 Turbo
response = openai.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": transcript}]
)

respuesta_texto = response.choices[0].message.content
print("\nRespuesta de GPT-4 Turbo:")
print(respuesta_texto)

# Convertir la respuesta en audio con TTS (Text-to-Speech)
tts_response = openai.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=respuesta_texto
)

# Guardar el audio de la respuesta
AUDIO_OUTPUT_FILENAME = "respuesta.mp3"
with open(AUDIO_OUTPUT_FILENAME, "wb") as audio_file:
    audio_file.write(tts_response.content)

# Reproducir la respuesta en audio
#wave_obj = sa.WaveObject.from_wave_file(AUDIO_OUTPUT_FILENAME)
#play_obj = wave_obj.play()
#play_obj.wait_done()
#playsound("respuesta.mp3")
playsound(AUDIO_OUTPUT_FILENAME)

# Eliminar archivos temporales
os.remove(WAVE_OUTPUT_FILENAME)
os.remove(AUDIO_OUTPUT_FILENAME)

print("Archivos temporales eliminados.")
