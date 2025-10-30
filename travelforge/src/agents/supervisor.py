# supervisor_workflow.py
import json
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor, create_handoff_tool, create_forward_message_tool
from langgraph.prebuilt import create_tool_from_callable

from .config import OPENAI_API_KEY
from .agents import travel_request_agent, user_profile_agent, travel_response_agent
from .agents import run_compiled_agent, extract_structured_response

# LLM usato dal supervisor/worker (usiamo ChatOpenAI helper come da quickstart)
model = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)


# ----------------------------
# TOOL WRAPPERS per i worker
# ----------------------------
# Questi tool sono funzioni che il create_react_agent può chiamare.
# Ogni tool invoca il compiled agent che abbiamo definito in agents.py
def travel_request_tool(user_input: str) -> str:
    """
    wrapper che invoca travel_request_agent con payload {user_input}.
    Ritorna stringa JSON (per semplicità e compatibilità con tools che
    si aspettano stringhe).
    """
    state = run_compiled_agent(travel_request_agent, {"user_input": user_input})
    resp = extract_structured_response(state)
    # Assicuriamoci di serializzare eventuali Enum a stringhe
    return json.dumps(resp, default=str, ensure_ascii=False)


def user_profile_tool(user_input: str) -> str:
    state = run_compiled_agent(user_profile_agent, {"user_input": user_input})
    resp = extract_structured_response(state)
    return json.dumps(resp, default=str, ensure_ascii=False)


def travel_response_tool(combined: dict) -> str:
    # combined è un dict con travel_request + user_profile
    state = run_compiled_agent(travel_response_agent, {"combined": combined})
    resp = extract_structured_response(state)
    return json.dumps(resp, default=str, ensure_ascii=False)


# Create tools that LangGraph can pass to agents
# create_tool_from_callable è comodo per trasformare qualsiasi funzione in tool
travel_request_tool_wrapped = create_tool_from_callable(
    travel_request_tool, name="build_travel_request", description="Crea/aggiorna TravelRequest da input utente"
)
user_profile_tool_wrapped = create_tool_from_callable(
    user_profile_tool, name="build_user_profile", description="Crea/aggiorna UserProfile dall'input utente"
)
travel_response_tool_wrapped = create_tool_from_callable(
    travel_response_tool, name="build_travel_response", description="Genera TravelResponse da TravelRequest+UserProfile"
)


# ----------------------------
# Worker agents (create_react_agent)
# ----------------------------
travel_request_worker = create_react_agent(
    model=model,
    tools=[travel_request_tool_wrapped],
    name="travel_request_worker",
    prompt=(
        "Se l'utente vuole pianificare un viaggio, usa lo strumento build_travel_request "
        "per costruire un TravelRequest conforme allo schema. Usa il tool una volta e ritorna la risposta."
    )
)

user_profile_worker = create_react_agent(
    model=model,
    tools=[user_profile_tool_wrapped],
    name="user_profile_worker",
    prompt=(
        "Se l'utente fornisce informazioni personali, usa il tool build_user_profile per generare un UserProfile coerente."
    )
)

travel_response_worker = create_react_agent(
    model=model,
    tools=[travel_response_tool_wrapped],
    name="travel_response_worker",
    prompt=(
        "Quando richiesto, crea un TravelResponse (itinerario) usando il tool build_travel_response "
        "con l'input combinato fornito."
    )
)


# ----------------------------
# Supervisor: crea il workflow e compila
# ----------------------------
# Possiamo aggiungere tool di handoff e forwarding (opzionale)
handoff_to_travel_request = create_handoff_tool(
    agent_name="travel_request_worker",
    name="assign_to_travel_request",
    description="Assegna la conversazione al worker travel_request_worker"
)
handoff_to_user_profile = create_handoff_tool(
    agent_name="user_profile_worker",
    name="assign_to_user_profile",
    description="Assegna la conversazione al worker user_profile_worker"
)
handoff_to_travel_response = create_handoff_tool(
    agent_name="travel_response_worker",
    name="assign_to_travel_response",
    description="Assegna la conversazione al worker travel_response_worker"
)

forwarding_tool = create_forward_message_tool("supervisor_forwarded_message")


workflow = create_supervisor(
    agents=[travel_request_worker, user_profile_worker, travel_response_worker],
    model=model,
    prompt=(
        "Sei un supervisor che coordina tre worker: travel_request_worker (gestisce la costruzione della TravelRequest), "
        "user_profile_worker (gestisce UserProfile) e travel_response_worker (genera TravelResponse). "
        "Decidi quale worker chiamare in base al contenuto del messaggio: se il messaggio parla di 'nome', 'cognome', 'età' o preferenze chiama user_profile_worker; "
        "se il messaggio parla di 'destinazione', 'partenza', 'periodo' chiama travel_request_worker; "
        "se l'utente richiede 'itinerario', 'programma' o 'pianifica' chiama travel_response_worker. "
        "Usa gli handoff tools forniti per delegare il compito e aggiungi al history le risposte importanti."
    ),
    tools=[
        handoff_to_travel_request,
        handoff_to_user_profile,
        handoff_to_travel_response,
        forwarding_tool,
    ],
    # output_mode può essere "full_history" o "last_message"
    output_mode="last_message",
    handoff_tool_prefix="delegate_to",
)

# Compila e esporta l'app (lo stato graph compilato)
app = workflow.compile(name="travel_supervisor")
