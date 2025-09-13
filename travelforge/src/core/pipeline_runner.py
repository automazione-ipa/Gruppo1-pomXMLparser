# pipeline_runner.py
import json
from pydantic import ValidationError
from ..resources.utils.logger import get_logger
from ..resources.utils.pydantic_utils import to_serializable_v2, to_pydantic_v2
from ..agents.agents import (
    travel_request_agent,
    user_profile_agent,
    travel_response_agent,
    run_compiled_agent,
    extract_structured_response,
)
from ..agents.models import TravelRequest, UserProfile, TravelResponse

logger = get_logger("travel_pipeline")


def run_pipeline(user_input: str, conversation_id: str, user_id: str):
    """
    Esegue l'intera pipeline di generazione viaggio (request, profile, response).
    Adatta la versione CLI ma pronta anche per API o frontend.
    """
    logger.info(f"[{user_id} | {conversation_id}] Avvio pipeline viaggio per input utente.")
    if not user_input.strip():
        user_input = "Voglio fare un viaggio a Berlino di 3 giorni, arte e cibo."

    # --- TRAVEL REQUEST ---
    logger.info("🧩 Generazione TravelRequest...")
    payload = {"messages": [{"role": "user", "content": user_input}], "user_input": user_input}
    state_tr = run_compiled_agent(travel_request_agent, payload)
    sr_tr = extract_structured_response(state_tr)

    try:
        tr_obj = to_pydantic_v2(TravelRequest, sr_tr)
        tr_serializable = to_serializable_v2(tr_obj)
    except ValidationError as e:
        logger.warning(f"TravelRequest non valido: {e}")
        tr_serializable = to_serializable_v2(sr_tr)
        tr_obj = None

    logger.info("✅ TravelRequest generato:")
    logger.safe_info(tr_serializable, indent=2)

    # --- USER PROFILE ---
    logger.info("🧬 Generazione UserProfile...")
    state_up = run_compiled_agent(user_profile_agent, payload)
    sr_up = extract_structured_response(state_up)

    try:
        up_obj = to_pydantic_v2(UserProfile, sr_up)
        up_serializable = to_serializable_v2(up_obj)
    except ValidationError as e:
        logger.warning(f"UserProfile non valido: {e}")
        up_serializable = to_serializable_v2(sr_up)
        up_obj = None

    logger.info("✅ UserProfile generato:")
    logger.safe_info(up_serializable, indent=2)

    # --- TRAVEL RESPONSE ---
    logger.info("🗺️ Generazione TravelResponse...")
    combined = {"travel_request": tr_serializable, "user_profile": up_serializable}
    payload_resp = {
        "messages": [{"role": "user", "content": "Crea un itinerario dettagliato"}],
        "combined": combined,
    }
    state_resp = run_compiled_agent(travel_response_agent, payload_resp)
    sr_resp = extract_structured_response(state_resp)

    try:
        resp_obj = to_pydantic_v2(TravelResponse, sr_resp)
        resp_serializable = to_serializable_v2(resp_obj)
    except ValidationError as e:
        logger.warning(f"TravelResponse non valido: {e}")
        resp_serializable = to_serializable_v2(sr_resp)
        resp_obj = None

    logger.info("✅ TravelResponse generato:")
    logger.safe_info(resp_serializable, indent=2)

    return resp_serializable
