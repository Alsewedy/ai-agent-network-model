import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
WEB_SEARCH_CONTEXT_SIZE = os.getenv("WEB_SEARCH_CONTEXT_SIZE", "medium")


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=api_key)


def _should_enable_web_search(prompt: str) -> bool:
    """
    Enable web search only when the prompt explicitly indicates that:
    - external guidance is requested,
    - external verification is required,
    - or local standards / local KB are insufficient for the evaluative answer.
    """
    lower = prompt.lower()

    external_signals = [
        "external trusted guidance",
        "external guidance",
        "broader external guidance",
        "outside my kb",
        "not in my files",
        "trusted external guidance",
        '"mode": "internal_plus_external"',
        '"mode": "external_verification"',
        "external_verification",
        "internal_plus_external",
        "official guidance",
        "vendor guidance",
        "from the internet",
        "trusted external",
        "confirm externally",
        "validate externally",
        "verify externally",
        "local standards are missing",
        "local standards missing",
        "local control references are missing",
        "local control references are insufficient",
        "local kb is insufficient",
        "full local documented knowledge base",
    ]

    return any(signal in lower for signal in external_signals)


def real_llm_response(prompt: str, allow_web_search: bool = True) -> str:
    client = get_client()

    use_web_search = (
        allow_web_search
        and ENABLE_WEB_SEARCH
        and _should_enable_web_search(prompt)
    )

    tools = []
    if use_web_search:
        tools.append(
            {
                "type": "web_search",
                "search_context_size": WEB_SEARCH_CONTEXT_SIZE,
            }
        )

    try:
        response = client.responses.create(
            model=MODEL,
            input=prompt,
            tools=tools if tools else None,
        )
        return response.output_text.strip()

    except Exception as e:
        if use_web_search:
            fallback_response = client.responses.create(
                model=MODEL,
                input=prompt,
            )
            return fallback_response.output_text.strip()

        raise RuntimeError(f"LLM request failed: {e}") from e