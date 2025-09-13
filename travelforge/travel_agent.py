# src/travel_agent.py
from src.resources.db import crud
from src.agents.models import TravelRequest as PydTravelRequest, UserProfile as PydUserProfile, TravelResponse as PydTravelResponse
from src.resources.utils.pydantic_utils import to_serializable_v2, to_pydantic_v2
from src.resources.utils.logger import get_logger
from src.agents.agents import (
    travel_request_agent, user_profile_agent, travel_response_agent,
    run_compiled_agent, extract_structured_response
)
from pydantic import ValidationError
import uuid
import json

# travel_agent.py
def safe_json_dumps(obj, **kwargs):
    """Wrapper universale per serializzare Pydantic v2, dict, ecc."""
    try:
        return json.dumps(to_serializable_v2(obj), ensure_ascii=False, **kwargs)
    except Exception:
        return json.dumps(str(obj), ensure_ascii=False, **kwargs)


logger = get_logger(__name__)

class TravelChatAgent:
    """
    Agente principale che orchestra la pipeline Langchain con persistenza DB.
    - Crea/resume TravelRequest (conversation ID).
    - Persiste messaggi e output strutturati.
    - Esegue agenti Langchain per TravelRequest, UserProfile, TravelResponse.
    - Supporta sub-agenti/tools per raffinamenti (es. ristoranti, alloggi).
    """

    def __init__(self, db, user_id: str, travel_id: str = None, model: str = "gpt-4o-mini", agent: str = "default-agent"):
        self.db = db
        self.user_id = user_id
        self.model = model
        self.agent = agent

        # Ensure user exists
        crud.create_user(self.db, self.user_id)

        # Use or create TravelRequest
        if travel_id:
            tr = crud.get_travel_request(self.db, travel_id)
            if tr is None:
                self.travel_id = travel_id
                crud.create_travel_request(self.db, self.travel_id, self.user_id)
            else:
                self.travel_id = travel_id
        else:
            self.travel_id = f"tr-{uuid.uuid4().hex[:12]}"
            crud.create_travel_request(self.db, self.travel_id, self.user_id)

        # Create LLM session and attach
        self.llm_session = crud.create_llm_session(self.db, self.travel_id, model=self.model, agent=self.agent)

    def run(self, query: str) -> str:
        # Persist user message
        crud.append_message_to_travel(self.db, self.travel_id, "user", query)
        logger.info(f"[{self.user_id} | {self.travel_id}] user: {query}")

        # Load history for context
        tr = crud.get_travel_request(self.db, self.travel_id)
        history_messages = [{"role": m["role"], "content": m["content"]} for m in (tr.messages or [])]
        payload = {
            "messages": history_messages + [{"role": "user", "content": query}],
            "user_input": query,
            "user_id": self.user_id,  # For DB tools
            "travel_id": self.travel_id
        }

        try:
            # Step 1: TravelRequest Agent
            state_tr = run_compiled_agent(travel_request_agent, payload)
            sr_tr = extract_structured_response(state_tr)
            tr_obj = to_pydantic_v2(PydTravelRequest, sr_tr)
            tr_serial = to_serializable_v2(tr_obj)
            # Persist to DB
            crud.update_structured_output(self.db, self.travel_id, tr_serial)
            # Update specific fields for querying
            tr.origin = tr_serial.get('origin')
            tr.destination = tr_serial.get('destination')
            tr.start_date = tr_serial.get('start_date')
            tr.end_date = tr_serial.get('end_date')
            tr.interests = tr_serial.get('interests', [])
            self.db.commit()
            crud.append_message_to_travel(self.db, self.travel_id, "system", f"TravelRequest updated: {json.dumps(tr_serial)}")

            # Step 2: UserProfile Agent (uses DB tools for history/profile)
            state_up = run_compiled_agent(user_profile_agent, payload)
            sr_up = extract_structured_response(state_up)
            up_obj = to_pydantic_v2(PydUserProfile, sr_up)
            up_serial = to_serializable_v2(up_obj)
            # Persist to PersonalProfile
            crud.update_personal_profile(self.db, self.user_id, up_serial)
            crud.append_message_to_travel(self.db, self.travel_id, "system", f"UserProfile updated: {json.dumps(up_serial)}")

            # Step 3: TravelResponse Agent (if triggered, uses sub-tools for Restaurant, Housing, etc.)
            response = "Dati elaborati. Usa '/generate' o parole chiave come 'itinerario' per generare la response completa."
            if "generate" in query.lower() or "itiner" in query.lower():
                combined = {"travel_request": tr_serial, "user_profile": up_serial}
                payload_resp = {"messages": payload["messages"], "combined": combined}
                state_resp = run_compiled_agent(travel_response_agent, payload_resp)
                sr_resp = extract_structured_response(state_resp)
                raw_resp = json.dumps(sr_resp, ensure_ascii=False)  # Save raw for debug
                resp_obj = to_pydantic_v2(PydTravelResponse, sr_resp)
                resp_serial = to_serializable_v2(resp_obj)
                # Persist to TravelResponse table
                crud.create_travel_response(self.db, self.travel_id, resp_serial, raw_llm_response=raw_resp)
                response = safe_json_dumps(resp_serial, indent=2, ensure_ascii=False)

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            response = f"Errore di validazione: {str(e)}. Riprova con dettagli più chiari."
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            response = f"Errore interno: {str(e)}. Controlla logs o riprova."

        # Persist assistant response
        crud.append_message_to_travel(self.db, self.travel_id, "assistant", response)
        logger.info(f"[{self.user_id} | {self.travel_id}] assistant: {response}")

        return response