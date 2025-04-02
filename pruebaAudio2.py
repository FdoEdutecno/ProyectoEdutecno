# Versión 02/04/2025
import openai  # Librería para interactuar con la API de OpenAI
import os  # Módulo para manejar archivos y variables de entorno
import wave  # Para manejar archivos de audio en formato WAV
import pyaudio  # Para grabar y reproducir audio en tiempo real
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
RECORD_SECONDS = 7  # Duración de la grabación en segundos
WAVE_OUTPUT_FILENAME = "audio.wav"  # Nombre del archivo donde se guardará la grabación

# Inicializa PyAudio
audio = pyaudio.PyAudio()  

while True:  # Bucle para mantener la conversación activa
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("\nHabla ahora...")  
    frames = []  # Lista para almacenar los fragmentos de audio grabado

# Capturar el audio durante el tiempo especificado
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)  # Leer un fragmento de audio
        frames.append(data)  

    print("Grabación finalizada")

    # Detener y cerrar el stream de audio
    stream.stop_stream()
    stream.close()

    # Guardar el audio grabado en un archivo WAV
    wavefile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  
    wavefile.setnchannels(CHANNELS)  
    wavefile.setsampwidth(audio.get_sample_size(FORMAT))  
    wavefile.setframerate(RATE)  
    wavefile.writeframes(b''.join(frames))  
    wavefile.close()  

    # Transcribir audio a texto con whisper
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",   # Modelo de OpenAI de reconocimiento de voz
            file=audio_file,  
            response_format="text"
        )
#Se mostrara la consulta que se hizo en texto
    print("\nTú consulta es:")
    print(transcript)

    # Enviar la pregunta a ChatGPT (GPT-4 Turbo)
    response = openai.chat.completions.create(
        model="gpt-4-turbo",  # Modelo de OpenAI
        messages=[{"role": "user", "content": transcript}]
    )

    respuesta_texto = response.choices[0].message.content  
    print("\nRespuesta de la IA:")
    print(respuesta_texto)  
    
    # Convertir la respuesta de IA en un archivo de audio con TTS
    tts_response = openai.audio.speech.create(
        model="tts-1",  # Modelo de OpenAI para síntesis de voz
        voice="alloy",  # Voz utilizada para la respuesta (hay varias)
        input=respuesta_texto  
    )

    AUDIO_OUTPUT_FILENAME = "respuesta.mp3"
    with open(AUDIO_OUTPUT_FILENAME, "wb") as audio_file:
        audio_file.write(tts_response.content)  # Mostrar por consola la respuesta

    # Reproducir el archivo de audio generado
    playsound(AUDIO_OUTPUT_FILENAME)  

    # Eliminar archivos temporales
    os.remove(WAVE_OUTPUT_FILENAME)  
    os.remove(AUDIO_OUTPUT_FILENAME)  

    # Preguntar al usuario si quiere hacer otra pregunta
    continuar = input("\n¿Quieres hacer otra pregunta? (s/n): ").strip().lower()
    if continuar != "s":
        print("Saliendo del programa...")
        break  

# Finaliza PyAudio
audio.terminate()
