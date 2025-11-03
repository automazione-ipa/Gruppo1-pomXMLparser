import os


def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("Bisogna impostare OPENAI_API_KEY nel file .env")
    return key
