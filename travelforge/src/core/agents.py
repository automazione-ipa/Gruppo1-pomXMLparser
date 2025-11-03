# agents.py
import json
from core.config import OPENAI_API_KEY
from core.models import (
    TravelRequest,
    UserProfile,
    TravelResponse,
)
from core.prompts import (
    travel_request_prompt,
    travel_response_prompt,
    user_profile_prompt,
)
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

# Init LLM via factory (langchain_openai provider must be installed)
llm = init_chat_model(
    model="openai:gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0
)


def build_agent(prompt_template: str, schema_class):
    return create_agent(
        model=llm,
        tools=[],  # senza tools per ora; possiamo aggiungerli dopo
        system_prompt=prompt_template,
        response_format=schema_class,  # importante: la CLASSE pydantic
    )


travel_request_agent = build_agent(travel_request_prompt, TravelRequest)
user_profile_agent = build_agent(user_profile_prompt, UserProfile)
travel_response_agent = build_agent(travel_response_prompt, TravelResponse)


# ---------- helpers per eseguire e parsare risultati agent ----------
def run_compiled_agent(agent, payload: dict):
    """
    Esegue un CompiledStateGraph sincrono con .invoke() e ritorna lo stato risultante.
    """
    # .invoke esegue la graph synchronously
    state = agent.invoke(payload)
    return state


def extract_structured_response(state):
    """
    Estrae il campo structured_response dallo state restituito da create_agent.
    Supporta i formati comuni: dict con 'structured_response', dict con 'messages',
    o simple content string che contenga JSON.
    """
    # caso dict con structured_response
    if isinstance(state, dict):
        if "structured_response" in state:
            return state["structured_response"]
        # some versions might return 'response' or 'result'
        for k in ("response", "result", "output"):
            if k in state:
                return state[k]
        # messages è spesso la lista di messaggi finali
        if "messages" in state and isinstance(state["messages"], list):
            # cerchiamo l'ultimo messaggio con content
            msgs = state["messages"]
            for m in reversed(msgs):
                if isinstance(m, dict) and "content" in m:
                    content = m["content"]
                    # prova a decode JSON
                    if isinstance(content, str):
                        try:
                            return json.loads(content)
                        except Exception:
                            return content
                    return content
            return state["messages"]
    # fallback: se è stringa json
    if isinstance(state, str):
        try:
            return json.loads(state)
        except Exception:
            return state
    return state
