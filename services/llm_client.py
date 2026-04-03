import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=api_key)


def real_llm_response(prompt: str) -> str:
    client = get_client()

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )
    return response.output_text.strip()