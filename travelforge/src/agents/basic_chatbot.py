# multiagent_chatbot.py
import json
from typing import Any
from pydantic import BaseModel

# langchain / langgraph imports (assumo le stesse versioni del tuo progetto)
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# importa i modelli pydantic definiti (li hai forniti come models.py)
from core.models import (
    TravelRequest,
    TravelResponse,
    UserProfile,
    ReservationSketch,
    TravelDayItem,
    DayPlan,
    Season,
)

# --- Stato globale tipizzato come nel tuo esempio ---
class BasicChatState(dict):
    """
    Stato minimo per il grafo: contiene le messages (list of Message objects)
    e lo stato applicativo (ReservationSketch) sotto "reservation".
    """
    pass


# ---------- Helpers ----------
def get_llm_model(model_name: str = "gpt-4o-mini"):
    """
    Create the LLM instance. Assicurati di avere .env configurato.
    """
    return ChatOpenAI(model_name=model_name)


def build_agent(prompt_template: str, schema_class):
    """
    Usa create_agent come nel tuo snippet: crea un agente che restituisce
    un output strutturato (pydantic schema_class).
    """
    return create_agent(
        model=llm,
        tools=[],  # per ora nessun tool esterno nei singoli agent
        system_prompt=prompt_template,
        response_format=schema_class,
    )


def serialize_state(reservation: ReservationSketch) -> str:
    """
    Serializza lo stato pydantic in JSON per passarlo nel prompt.
    """
    return reservation.json()


def safe_update_reservation(reservation: ReservationSketch, new_data: dict):
    """
    Aggiorna il ReservationSketch con dati provenienti dall'agente (dict).
    Manteniamo la semantica: solo i campi not None vengono sovrascritti/mergeati.
    """
    rd = new_data or {}
    for k, v in rd.items():
        if v is not None:
            setattr(reservation, k, v)


# ---------- Prompt templates per gli agenti ----------
# Sono esempi: ottimizza i prompt per risultati migliori.
SUPERVISOR_PROMPT = """
Sei un supervisor LLM che orchestra moduli per costruire un piano di viaggio.
Riceverai:
- lo stato globale JSON sotto il campo "state_json"
- l'input utente (testo) sotto il campo "user_input"
- la rappresentazione dello travel_request con code (state_code)

Obiettivi:
1) Calcola quali moduli sono necessari (user_profile, travel_request, planner, housing, events).
2) Restituisci un JSON con la chiave "run_modules" contente una lista ordinata dei nomi dei moduli da eseguire.
3) Motiva brevemente (campo "why") la scelta.

Formato di ritorno: pydantic schema che il create_agent parserà (TravelRequest/TravelResponse non necessario qui) — ma per semplicità useremo un semplice dict strutturato come:
{
  "run_modules": ["user_profile","travel_request","planner"],
  "why": "motivazione breve"
}
"""

USER_PROFILE_PROMPT = """
Sei un modulo che aggiorna o costruisce il profilo utente.
Input: lo stato globale JSON e l'ultimo messaggio utente.
Output: un JSON conforme al modello UserProfile (campi: name,surname,age,address,preferences,habits,relationships)
Regole:
- Se nel testo utente ci sono indizi (es. 'mi chiamo', 'ho 35 anni'), inferiscili.
- Non inventare dati: se non presenti, lascia None.
"""

TRAVEL_REQUEST_PROMPT = """
Sei il modulo che interpreta la richiesta di viaggio.
Input: stato globale JSON e ultimo messaggio utente.
Output: JSON conforme a TravelRequest (destination, origin, period, start_date, end_date, trip_type, wants_flight_links, wants_house_links)
Regole:
- Cerca di normalizzare periodi e stagioni (usa 'winter','spring','summer','autumn' dove possibile).
- Alla fine chiama compute_state() (ma se non possibile, assicurati che il campo state_code venga impostato con la stessa logica).
"""

PLANNER_PROMPT = """
Sei il modulo planner che produce TravelResponse (title, summary, days, accommodation_suggestions, transport_suggestions, notes).
Input: stato globale JSON (incluso user_profile e travel_request) e l'ultimo messaggio utente.
Output: JSON conforme a TravelResponse.
Regole:
- Produci un piano giornaliero se la durata è data.
- Se dati incompleti, suggerisci quali info mancano (campo 'notes').
"""

HOUSING_PROMPT = """
Sei il modulo housing che suggerisce sistemazioni.
Input: stato globale JSON e travel_request.
Output: { "accommodation_suggestions": [ ... ] }
Regole: fornisci 0..5 suggerimenti testuali (titolo corto + motivo).
"""

EVENTS_PROMPT = """
Sei il modulo events che suggerisce eventi/attività per la destinazione e le date.
Input: stato globale JSON e travel_request.
Output: { "events": [ { "title":"", "date":"", "why":"" }, ... ] }
Regole: suggerisci poche attività rilevanti.
"""


# ---------- NODI / AGENT FUNCTIONS ----------
def make_agent_and_run(prompt_template: str, schema_class: Any, state_reservation: ReservationSketch, user_message: str):
    """
    Costruisce un agente (create_agent via build_agent) e lo invoca passando come HumanMessage
    un JSON con stato e user_message. Restituisce il dict (parse del pydantic model).
    """
    prompt = prompt_template + "\n\nSTATE_JSON:\n" + serialize_state(state_reservation) + "\n\nUSER_INPUT:\n" + user_message

    # build an agent that returns the schema_class
    agent = build_agent(prompt_template=prompt, schema_class=schema_class)

    try:
        result = agent.invoke([HumanMessage(content=prompt)])
    except Exception as e:
        raise RuntimeError(f"Agent invocation failed: {e}.")

    # L'oggetto result potrebbe essere già un pydantic model o una dict.
    if isinstance(result, BaseModel):
        return json.loads(result.json())
    elif isinstance(result, dict):
        return result
    elif isinstance(result, str):
        try:
            return json.loads(result)
        except Exception:
            return {"raw": result}
    else:
        return {"raw": str(result)}


# Nodi specifici (wrap di make_agent_and_run con schema appropriato)
def run_user_profile_module(reservation: ReservationSketch, user_message: str):
    out = make_agent_and_run(USER_PROFILE_PROMPT, UserProfile, reservation, user_message)
    return out


def run_travel_request_module(reservation: ReservationSketch, user_message: str):
    out = make_agent_and_run(TRAVEL_REQUEST_PROMPT, TravelRequest, reservation, user_message)
    return out


def run_planner_module(reservation: ReservationSketch, user_message: str):
    out = make_agent_and_run(PLANNER_PROMPT, TravelResponse, reservation, user_message)
    return out


def run_housing_module(reservation: ReservationSketch, user_message: str):
    # schema semplice (dict)
    out = make_agent_and_run(HOUSING_PROMPT, dict, reservation, user_message)
    return out


def run_events_module(reservation: ReservationSketch, user_message: str):
    out = make_agent_and_run(EVENTS_PROMPT, dict, reservation, user_message)
    return out


# ---------- Supervisor ----------
def run_supervisor(reservation: ReservationSketch, user_message: str) -> dict:
    """
    Invoca il supervisor LLM che decide quali moduli eseguire.
    Ritorna dict con 'run_modules' e 'why'.
    """
    # build a quick agent that returns a small dict (lista di moduli)
    agent = build_agent(prompt_template=SUPERVISOR_PROMPT, schema_class=dict)

    prompt = SUPERVISOR_PROMPT + "\n\nSTATE_JSON:\n" + serialize_state(reservation) + "\n\nUSER_INPUT:\n" + user_message

    try:
        result = agent.invoke([HumanMessage(content=prompt)])
    except Exception:
        result = agent.invoke(prompt)

    # normalizza
    if isinstance(result, BaseModel):
        res = json.loads(result.json())
    elif isinstance(result, dict):
        res = result
    elif isinstance(result, str):
        try:
            res = json.loads(result)
        except Exception:
            res = {"run_modules": ["travel_request", "planner"], "why": result}
    else:
        res = {"run_modules": ["travel_request", "planner"], "why": str(result)}

    # assicurati che la lista contenga nomi validi
    allowed = {"user_profile", "travel_request", "planner", "housing", "events"}
    run_modules = [m for m in res.get("run_modules", []) if m in allowed]
    if not run_modules:
        # default safe flow
        run_modules = ["travel_request", "planner"]

    return {"run_modules": run_modules, "why": res.get("why", "")}


# ---------- Orchestrator: costruisce/aggiorna lo stato globale ----------
def orchestrate(reservation: ReservationSketch, user_message: str):
    """
    1) Chiama il supervisor per avere la lista dei moduli da lanciare.
    2) Lancia i moduli nell'ordine richiesto.
    3) Aggiorna reservation con i risultati strutturati.
    4) Restituisce una short response testuale per l'utente (sintesi).
    """
    supervisor_decision = run_supervisor(reservation, user_message)
    run_modules = supervisor_decision["run_modules"]

    debug_log = {"supervisor": supervisor_decision}

    # Esegui i moduli
    for module_name in run_modules:
        if module_name == "user_profile":
            out = run_user_profile_module(reservation, user_message)
            # merge in reservation.user_profile
            try:
                # convert dict -> UserProfile pydantic e sostituisci
                up = UserProfile(**out)
                reservation.user_profile = up
            except Exception:
                # merge parziale
                safe_update_reservation(reservation, {"user_profile": out})

            debug_log["user_profile"] = out

        elif module_name == "travel_request":
            out = run_travel_request_module(reservation, user_message)
            try:
                tr = TravelRequest(**out)
                # compute state
                tr.compute_state()
                reservation.travel_request = tr
            except Exception:
                safe_update_reservation(reservation, {"travel_request": out})
            debug_log["travel_request"] = out

        elif module_name == "planner":
            out = run_planner_module(reservation, user_message)
            try:
                trp = TravelResponse(**out)
                reservation.travel_response = trp
            except Exception:
                safe_update_reservation(reservation, {"travel_response": out})
            debug_log["planner"] = out

        elif module_name == "housing":
            out = run_housing_module(reservation, user_message)
            # housing suggerito come dict
            reservation.housing = out
            debug_log["housing"] = out

        elif module_name == "events":
            out = run_events_module(reservation, user_message)
            # events è una list di dict
            reservation.events = out.get("events", [])
            debug_log["events"] = out

    # Costruisci una sintesi per l'utente
    resp_lines = []
    if reservation.travel_request and reservation.travel_request.destination:
        rd = reservation.travel_request
        resp_lines.append(f"Richiesta di viaggio per {rd.destination}.")
    if reservation.travel_response and reservation.travel_response.summary:
        resp_lines.append(reservation.travel_response.summary)
    if reservation.housing:
        resp_lines.append("Ho suggerito alcune possibili sistemazioni.")
    if reservation.events:
        resp_lines.append(f"Ho trovato {len(reservation.events)} eventi/attività rilevanti.")

    if not resp_lines:
        resp_lines = ["Ho aggiornato lo stato: fammi sapere altro o chiedi di generare il piano."]

    return {"text": " ".join(resp_lines), "debug": debug_log}


# ---------- Montaggio grafo e loop principale ----------
def mount_multiagent_graph():
    """
    Costruisce un grafo semplice con un solo entry node 'orchestrator' che esegue orchestrate().
    Se vuoi, puoi espandere e fare nodi separati per ogni agente.
    """
    graph = StateGraph(BasicChatState)
    # definisci il nodo 'orchestrator' che useremo per eseguire orchestration
    def orchestrator_node(state):
        """
        Questo nodo si aspetta state['messages'] come lista di HumanMessage/AIMessage.
        L'ultimo messaggio umano è quello usato per guidare l'orchestrazione.
        """
        messages = state["messages"]
        last_msg = None
        if isinstance(messages, list) and len(messages) > 0:
            last_msg = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
        else:
            last_msg = ""

        # recupera o crea lo state reservation
        reservation = state.get("reservation")
        if reservation is None:
            reservation_obj = ReservationSketch()
        else:
            reservation_obj = reservation

        out = orchestrate(reservation_obj, last_msg)

        # Aggiorna lo stato condiviso
        state["reservation"] = reservation_obj

        # prepara la risposta da mettere in messages
        ai_msg = AIMessage(content=out["text"])
        state["messages"].append(ai_msg)

        # opzionale: aggiungi debug per ispezione (non in produzione)
        state["_debug_last_orchestrator"] = out["debug"]

        return state

    graph.add_node("orchestrator", orchestrator_node)
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", END)
    return graph


def run_multiagent_chatbot(with_memory=False):
    """
    Loop interactive: l'utente inserisce messaggi, il grafo invoca il nodo orchestrator
    che aggiorna lo stato globale.
    """
    global llm
    llm = get_llm_model(model_name="gpt-4o-mini")

    graph = mount_multiagent_graph()

    config = None
    if with_memory:
        memory = MemorySaver()
        app = graph.compile(checkpointer=memory)
    else:
        app = graph.compile()

    print("Multi-agent chatbot avviato. Digita 'exit' per uscire.")
    while True:
        user_input = input("User: ")
        if user_input.strip().lower() == "exit":
            break

        # invoca il grafo: estado iniziale
        init_state = {
            "messages": [HumanMessage(content=user_input)]
        }

        result_state = app.invoke(init_state)
        # stampa risposta LLM appena aggiunta
        # l'ultima message è la AIMessage che abbiamo inserito
        messages = result_state.get("messages", [])
        ai_responses = [m for m in messages if isinstance(m, AIMessage)]
        if ai_responses:
            print("Bot:", ai_responses[-1].content)

        # opzionale: mostra stato debug interno
        debug = result_state.get("_debug_last_orchestrator")
        if debug:
            print("DEBUG:", json.dumps(debug, indent=2, ensure_ascii=False))

        # se vuoi persistere lo stato tra messaggi, puoi salvare result_state['reservation'] da qualche parte
