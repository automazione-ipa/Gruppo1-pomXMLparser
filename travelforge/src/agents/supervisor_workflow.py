# supervisor_workflow.py
import json
from langchain_openai import ChatOpenAI
from langgraph_supervisor import (
    create_supervisor,
    create_handoff_tool,
    create_forward_message_tool,
)
from langchain_core.tools import tool

from core.agents import (
    travel_request_agent,
    user_profile_agent,
    travel_response_agent,
    run_compiled_agent,
    extract_structured_response,
)
from core.config import get_openai_api_key

# ----------------------------
# LLM per supervisor/worker
# ----------------------------
model = ChatOpenAI(
    model="gpt-4o",
    api_key=get_openai_api_key()
)


# ----------------------------
# TOOL DEFINITIONS (moderni)
# ----------------------------

@tool(
    name="build_travel_request",
    description="Crea o aggiorna un TravelRequest basato sull'input utente.",
)
def travel_request_tool(user_input: str) -> str:
    """Invoca il travel_request_agent con {user_input} e restituisce un JSON serializzato."""
    state = run_compiled_agent(travel_request_agent, {"user_input": user_input})
    resp = extract_structured_response(state)
    return json.dumps(resp, default=str, ensure_ascii=False)


@tool(
    name="build_user_profile",
    description="Crea o aggiorna un UserProfile basato sull'input utente.",
)
def user_profile_tool(user_input: str) -> str:
    state = run_compiled_agent(user_profile_agent, {"user_input": user_input})
    resp = extract_structured_response(state)
    return json.dumps(resp, default=str, ensure_ascii=False)


@tool(
    name="build_travel_response",
    description="Genera un TravelResponse (itinerario) a partire da TravelRequest + UserProfile.",
)
def travel_response_tool(combined: dict) -> str:
    state = run_compiled_agent(travel_response_agent, {"combined": combined})
    resp = extract_structured_response(state)
    return json.dumps(resp, default=str, ensure_ascii=False)


# ----------------------------
# WORKER AGENTS
# ----------------------------

travel_request_worker = agent(
    model=model,
    tools=[travel_request_tool],
    name="travel_request_worker",
    system_prompt=(
        "Se l'utente vuole pianificare un viaggio, usa lo strumento "
        "'build_travel_request' per costruire un TravelRequest conforme allo schema. "
        "Usa il tool una volta e ritorna la risposta."
    ),
)

user_profile_worker = agent(
    model=model,
    tools=[user_profile_tool],
    name="user_profile_worker",
    system_prompt=(
        "Se l'utente fornisce informazioni personali (nome, cognome, età, preferenze), "
        "usa il tool 'build_user_profile' per generare un UserProfile coerente."
    ),
)

travel_response_worker = agent(
    model=model,
    tools=[travel_response_tool],
    name="travel_response_worker",
    system_prompt=(
        "Quando richiesto, crea un TravelResponse (itinerario di viaggio) usando il tool "
        "'build_travel_response' con l'input combinato fornito (TravelRequest + UserProfile)."
    ),
)


# ----------------------------
# SUPERVISOR WORKFLOW
# ----------------------------

handoff_to_travel_request = create_handoff_tool(
    agent_name="travel_request_worker",
    name="assign_to_travel_request",
    description="Assegna la conversazione al worker travel_request_worker",
)

handoff_to_user_profile = create_handoff_tool(
    agent_name="user_profile_worker",
    name="assign_to_user_profile",
    description="Assegna la conversazione al worker user_profile_worker",
)

handoff_to_travel_response = create_handoff_tool(
    agent_name="travel_response_worker",
    name="assign_to_travel_response",
    description="Assegna la conversazione al worker travel_response_worker",
)

forwarding_tool = create_forward_message_tool("supervisor_forwarded_message")


workflow = create_supervisor(
    agents=[travel_request_worker, user_profile_worker, travel_response_worker],
    model=model,
    system_prompt=(
        "Sei un supervisor che coordina tre worker:\n"
        "- travel_request_worker: gestisce la costruzione di TravelRequest;\n"
        "- user_profile_worker: gestisce la creazione di UserProfile;\n"
        "- travel_response_worker: genera TravelResponse.\n\n"
        "Instrada i messaggi in base al contenuto:\n"
        "- se il messaggio parla di 'nome', 'cognome', 'età' o 'preferenze' → chiama user_profile_worker;\n"
        "- se parla di 'destinazione', 'partenza' o 'periodo' → chiama travel_request_worker;\n"
        "- se richiede 'itinerario', 'programma' o 'pianifica' → chiama travel_response_worker.\n\n"
        "Usa gli strumenti di handoff forniti per delegare i compiti e conserva nel contesto "
        "le risposte importanti per i passi successivi."
    ),
    tools=[
        handoff_to_travel_request,
        handoff_to_user_profile,
        handoff_to_travel_response,
        forwarding_tool,
    ],
    output_mode="last_message",
    handoff_tool_prefix="delegate_to",
)

# ----------------------------
# COMPILAZIONE APP
# ----------------------------
app = workflow.compile(name="travel_supervisor")
