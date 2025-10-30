# main.py
from agents import travel_request_agent, user_profile_agent, travel_response_agent, run_compiled_agent, extract_structured_response
from pydantic_utils import to_serializable_v2, to_pydantic_v2
from models import TravelRequest, UserProfile, TravelResponse
import json
from pydantic import ValidationError


def run_pipeline():
    user_input = input("Ciao! Raccontami il tuo viaggio desiderato: ").strip()
    if not user_input:
        user_input = "Voglio fare un viaggio a Berlino di 3 giorni, arte e cibo."

    # --- TravelRequest ---
    print("\n--- TravelRequest ---")
    payload = {"messages": [{"role": "user", "content": user_input}], "user_input": user_input}
    state_tr = run_compiled_agent(travel_request_agent, payload)
    sr_tr = extract_structured_response(state_tr)
    # prova a validare come Pydantic v2
    try:
        tr_obj = to_pydantic_v2(TravelRequest, sr_tr)
        tr_serializable = to_serializable_v2(tr_obj)
    except ValidationError as e:
        print("Attenzione: TravelRequest non valido:", e)
        tr_serializable = to_serializable_v2(sr_tr)
        tr_obj = None
    print(json.dumps(tr_serializable, indent=2, ensure_ascii=False))

    # --- UserProfile ---
    print("\n--- UserProfile ---")
    state_up = run_compiled_agent(user_profile_agent, payload)
    sr_up = extract_structured_response(state_up)
    try:
        up_obj = to_pydantic_v2(UserProfile, sr_up)
        up_serializable = to_serializable_v2(up_obj)
    except ValidationError as e:
        print("Attenzione: UserProfile non valido:", e)
        up_serializable = to_serializable_v2(sr_up)
        up_obj = None
    print(json.dumps(up_serializable, indent=2, ensure_ascii=False))

    # --- TravelResponse ---
    print("\n--- TravelResponse ---")
    combined = {"travel_request": tr_serializable, "user_profile": up_serializable}
    payload_resp = {"messages": [{"role": "user", "content": "Crea un itinerario"}], "combined": combined}
    state_resp = run_compiled_agent(travel_response_agent, payload_resp)
    sr_resp = extract_structured_response(state_resp)
    try:
        resp_obj = to_pydantic_v2(TravelResponse, sr_resp)
        resp_serializable = to_serializable_v2(resp_obj)
    except ValidationError as e:
        print("Attenzione: TravelResponse non valido:", e)
        resp_serializable = to_serializable_v2(sr_resp)
        resp_obj = None
    print(json.dumps(resp_serializable, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_pipeline()
