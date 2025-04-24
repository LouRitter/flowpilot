from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run(params: dict, context: dict) -> str:
    text = params.get("text", "")
    print("🧠 [AI] Summarizing text...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        temperature=0.2
    )
    return response.choices[0].message.content
