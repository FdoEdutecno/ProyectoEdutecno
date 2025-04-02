import openai  # Importar la librería OpenAI
import os  # Manejo de variables de entorno
from dotenv import load_dotenv  # Cargar API Key desde .env
 
# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
 
# Verificar si la API Key está presente
if not api_key:
    raise ValueError("No se encontró la API")
 
# Configurar el cliente de OpenAI
client = openai.OpenAI(api_key="")

def chat_with_gpt():
    print("Iniciado, 'salir' para terminar.")
   
    conversation = []  # Historial de la conversación
   
    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ["salir", "no"]:
            break
       
        # Agregar mensaje del usuario al historial
        conversation.append({"role": "user", "content": user_input})
       
        # Enviar la consulta a OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=conversation
        )
       
        # Obtener y mostrar la respuesta
        answer = response.choices[0].message.content
        print("\n", answer)
       
        # Agregar respuesta del asistente al historial
        conversation.append({"role": "assistant", "content": answer})
       
        # Preguntar si el usuario quiere continuar
        continue_chat = input("\n¿Quieres hacer otra pregunta? (sí/no): ").strip().lower()
        if continue_chat not in ["sí", "si", "s"]:
            print("\nSesión terminada")
            break
 
# Ejecutar el chat
chat_with_gpt()