
import openai
import openai
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=api_key)
response = client.images.generate(
 model="dall-e-3",
 prompt="un gato negro.",
 n=1,
 size="1024x1024"
)
print(response.data[0].url)
