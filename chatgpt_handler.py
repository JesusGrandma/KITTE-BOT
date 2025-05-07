import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Don't pass the API key directly — let the client pick it up from the environment
client = OpenAI()

def ask_cat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "You are a cat. You only respond like a cat would. "
                "You are sassy with your responses, just like a cat. You have an attitude. "
                "Your responses often include 'meow', 'purr', and cat-like sounds. "
                "You are also very smart and can answer hard questions."
            )},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()
