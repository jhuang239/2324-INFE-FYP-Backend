import os
import openai
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
async def chat(promt: list):
    print(promt)
    openai.api_key = SECRET_KEY
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = promt,
    )
    print(response)
    return response