import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


def real_llm_response(prompt: str) -> str:
    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )
    return response.output_text.strip()