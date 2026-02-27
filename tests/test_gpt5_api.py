from openai import OpenAI
from dotenv import load_dotenv
import os 

load_dotenv()
client = OpenAI()

response = client.responses.create(
    model="gpt-5.4-nano-2026-03-17",
    input="Hi !"
)

print(response.output_text)
