import openai  # Librería para interactuar con la API de OpenAI
import os  # Módulo para manejar archivos y variables de entorno
import wave  # Para manejar archivos de audio en formato WAV
import pyaudio  # Para grabar y reproducir audio en tiempo real
import simpleaudio as sa  # (No se usa en la versión actual, antes se usaba para reproducir audio)
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from playsound import playsound  # Para reproducir archivos de audio en formato MP3

# Cargar variables de entorno desde el archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # Obtener la clave de API de OpenAI desde el entorno

# Verificar si la API Key está presente
if not api_key:
    raise ValueError("No se encontró la API Key.")

# Configuración de la grabación de audio
FORMAT = pyaudio.paInt16  # Formato de audio: 16 bits
CHANNELS = 1  # Audio en un solo canal (mono)
RATE = 44100  # Frecuencia de muestreo en Hz (calidad estándar)
CHUNK = 1024  # Tamaño del buffer de audio
RECORD_SECONDS = 5  # Duración de la grabación en segundos
WAVE_OUTPUT_FILENAME = "audio.wav"  # Nombre del archivo donde se guardará la grabación

# Iniciar la grabación de audio
audio = pyaudio.PyAudio()  # Inicializa la interfaz de PyAudio
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Habla ahora...")  # Mensaje para el usuario
frames = []  # Lista para almacenar los fragmentos de audio grabado

# Capturar el audio durante el tiempo especificado
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)  # Leer un fragmento de audio
    frames.append(data)  # Agregarlo a la lista de frames

print("Grabación finalizada")

# Detener y cerrar el stream de audio
stream.stop_stream()
stream.close()
audio.terminate() 

# Guardar el audio grabado en un archivo WAV
wavefile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  # Crear archivo WAV en modo escritura binaria
wavefile.setnchannels(CHANNELS)  # Configurar canales
wavefile.setsampwidth(audio.get_sample_size(FORMAT))  # Configurar profundidad de bits
wavefile.setframerate(RATE)  # Configurar la frecuencia de muestreo
wavefile.writeframes(b''.join(frames))  # Escribir los datos de audio en el archivo
wavefile.close()  # Cerrar el archivo WAV

# Enviar el archivo de audio a OpenAI Whisper para transcripción de voz a texto
with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",  # Modelo de OpenAI para reconocimiento de voz
        file=audio_file,  # Archivo de audio a transcribir
        response_format="text"  # Obtener la transcripción como texto plano
    )

# Mostrar la transcripción del audio
print("\n Texto transcrito:")
print(transcript)

# Enviar la pregunta transcrita a GPT-4 Turbo para obtener una respuesta
response = openai.chat.completions.create(
    model="gpt-4-turbo",  # Modelo de OpenAI utilizado
    messages=[{"role": "user", "content": transcript}]  # Mensaje con la pregunta transcrita
)

respuesta_texto = response.choices[0].message.content  # Obtener la respuesta de GPT
print("\nRespuesta de GPT-4 Turbo:")
print(respuesta_texto)  # Mostrar la respuesta en la consola

# Convertir la respuesta en un archivo de audio usando TTS (Text-to-Speech)
tts_response = openai.audio.speech.create(
    model="tts-1",  # Modelo de OpenAI para síntesis de voz
    voice="alloy",  # Voz utilizada para la respuesta
    input=respuesta_texto  # Texto que será convertido en voz
)

# Guardar el audio de la respuesta en un archivo MP3
AUDIO_OUTPUT_FILENAME = "respuesta.mp3"
with open(AUDIO_OUTPUT_FILENAME, "wb") as audio_file:
    audio_file.write(tts_response.content)  # Escribir el contenido de audio en el archivo

# Reproducir el archivo de audio generado
playsound(AUDIO_OUTPUT_FILENAME)  # Reproduce el archivo MP3 con la respuesta de GPT

# Eliminar los archivos temporales después de su uso
os.remove(WAVE_OUTPUT_FILENAME)  # Eliminar el archivo de grabación original
os.remove(AUDIO_OUTPUT_FILENAME)  # Eliminar el archivo de respuesta en audio

print("Archivos temporales eliminados.")  # Mensaje de confirmación
