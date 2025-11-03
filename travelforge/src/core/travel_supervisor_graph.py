# travel_supervisor_graph.py

from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor

# --- Agents di dominio ---
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

travel_request_agent = create_agent(
    model=llm,
    name="travel_request_agent",
    system_prompt="Estrarre e aggiornare i dettagli del viaggio (destinazione, date, interessi, ecc.).",
)

user_profile_agent = create_agent(
    model=llm,
    name="user_profile_agent",
    system_prompt="Analizza messaggi utente e aggiorna le informazioni del profilo personale (età, preferenze, stile di viaggio).",
)

travel_description_agent = create_agent(
    model=llm,
    name="travel_description_agent",
    system_prompt="Descrivi il luogo di destinazione, principali attrazioni e cosa offre.",
)

travel_planner_agent = create_agent(
    model=llm,
    name="travel_planner_agent",
    system_prompt="Organizza un itinerario giorno per giorno in base allo stato globale del viaggio.",
)

# --- Supervisor ---
supervisor_prompt = """
Sei il supervisore di un sistema multi-agente per viaggi.
Analizza ogni messaggio dell'utente e decidi quale agente deve lavorare:
- Profiler: se ci sono info personali o preferenze
- TravelRequest: se ci sono info sul viaggio
- Description: se l'utente chiede dettagli sul luogo o cosa visitare
- Planner: se l'utente chiede un itinerario o vuole generare un piano
Aggiorna sempre lo stato globale 'reservation'.
Non rispondere direttamente all’utente, ma delega all’agente giusto.
"""

supervisor = create_supervisor(
    model=llm,
    agents=[
        travel_request_agent,
        user_profile_agent,
        travel_description_agent,
        travel_planner_agent,
    ],
    prompt=supervisor_prompt,
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()
