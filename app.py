from flask import Flask, request, jsonify  # Importamos Flask para crear la API
import os  
from dotenv import load_dotenv  # Para cargar variables desde un archivo .env
from openai import OpenAI  

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key de OpenAI desde las variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verificar si la API Key está configurada correctamente
if not OPENAI_API_KEY:
    raise ValueError("No se encontró la API Key de OpenAI.")

# Inicializar el cliente de OpenAI con la API Key
client = OpenAI(api_key=OPENAI_API_KEY)

# Creación la aplicación Flask
app = Flask(__name__)

# Definir el endpoint "/chat" que acepta solicitudes POST
@app.route('/chat', methods=['POST'])
def chat():
    # Obtener los datos JSON de la solicitud
    data = request.get_json()
    
    # Obtener la pregunta del usuario
    question = data.get("question", "")

    # Verificar si se proporcionó una pregunta
    if not question:
        return jsonify({"error": "No se proporcionó una pregunta"}), 400

    try:
        # Enviar la pregunta al modelo de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modelo de lenguaje a usar
            messages=[{"role": "user", "content": question}]
        )

        # Extraer la respuesta del modelo
        answer = response.choices[0].message.content

        # Imprimir la pregunta y la respuesta en la terminal
        print(f"Pregunta: {question}\nRespuesta: {answer}")

        # Devolver la respuesta en formato JSON
        return jsonify({"answer": answer})

    except Exception as e:
        # Manejo de errores y respuesta en caso de falla
        return jsonify({"error": str(e)}), 500

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
