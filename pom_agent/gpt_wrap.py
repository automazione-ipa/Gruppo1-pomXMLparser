import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def chat_functions(
        user_message=None,
        system_message=None,
        assistant_message=None,
        function_message=None,
        model='gpt-4o-mini',
        temperature=0.7,
        functions=None,
        function_call="auto",
        **kwargs
):
    """
    Sends a chat message to the OpenAI API and returns the assistant's reply.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    messages = []
    if system_message:
        messages.append({'role': 'system', 'content': system_message})

    if assistant_message:
        messages.append(assistant_message)

    if function_message:
        messages.append(function_message)

    if user_message:
        messages.append({'role': 'user', 'content': user_message})

    data = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
    }

    if functions:
        data['functions'] = functions
        data['function_call'] = function_call

    # Merge di eventuali altri parametri esterni
    data.update(kwargs)

    resp = requests.post(
        url='https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )

    if resp.status_code != 200:
        raise Exception(f"Request failed {resp.status_code}: {resp.text}")

    return resp.json()


def get_embedding(text, model='text-embedding-ada-002'):
    """Funzione per ottenere l'embedding di un testo."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY non trovato nelle variabili d'ambiente.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'input': text
    }

    response = requests.post(
        url='https://api.openai.com/v1/embeddings',
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        response_json = response.json()
        embedding = response_json['data'][0]['embedding']
        return embedding
    else:
        raise Exception(f"Richiesta fallita con codice di stato {response.status_code}: {response.text}")


def gpt_choice_message(response_json):
    return response_json['choices'][0]['message']


def gpt_choice_content(response_json):
    return response_json['choices'][0]['message']['content']


def build_queries(deps):
    """Usa GPT (placeholder) per identificare ricerche CVE. Generi stringhe per ciascuna dipendenza. """
    return [f"{d['artifactId']} {d['version']} CVE" for d in deps]
