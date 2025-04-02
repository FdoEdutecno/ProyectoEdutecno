from os import getenv
import openai
import time
from dotenv import load_dotenv  # Cargar API Key desde .env
from pathlib import Path
 
# Cargar variables de entorno y configurar cliente de OpenAI
load_dotenv()
api_key = getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


#Se envía un archivo de audio y se transcribe
audio_file= open("./recordings/voice_4.m4a", "rb")

start_time = time.time()
transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
)

transcription_time = (time.time() - start_time)

print("\n", transcription.text)
print("TRANSCRIPCIÓN %s segundos" % transcription_time,"\n")


#Se recibe el texto y se utiliza chatGPT para responder el query

start_time = time.time()
response = client.responses.create(
    model="gpt-4o-mini",
    instructions="Eres un asistente a la educación. Da respuestas claras y concisas. Si tienes que explicar matemáticamente algo intenta no hacerlo con LaTEX.",
    input=transcription.text,
)

query_time = (time.time() - start_time)

print(response.output_text)
print("QUERY %s segundos" % query_time,"\n")

#Se toma el query y se vuelve a transformar en audio para escucharlo

speech_file_path = Path(__file__).parent / "respuesta.wav"

start_time = time.time()

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=response.output_text,
    instructions="Eres un asistente de educación, habla con autoridad pero de manera entusiasta por enseñar",
    response_format="wav",
) as response:
    response.stream_to_file(speech_file_path)

TTS_time = (time.time() - start_time)

print("Text-To-Speech %s segundos" % TTS_time,"\n")

print("Tiempo total de ejecución: ", transcription_time + query_time + TTS_time, "segundos")