"""Modulo dei prompts per StructuredOutput con schema JSON (usando model_json_schema di Pydantic v2)."""
import json
from core.models import TravelRequest, UserProfile, TravelResponse


travel_request_prompt = (
    "Se l'utente vuole pianificare un viaggio, costruisci un oggetto TravelRequest "
    "conforme al JSON schema fornito. Se mancano informazioni, poni domande di follow-up "
    "step-by-step fino ad ottenere uno schema valido.\n\n"
    f"Schema: {json.dumps(TravelRequest.model_json_schema(), indent=2, ensure_ascii=False)}\n\n"
    "Utente: {user_input}\nAgente:"
)

user_profile_prompt = (
    "Genera un UserProfile coerente con l'input utente. Se mancano dettagli, chiedili.\n\n"
    f"Schema: {json.dumps(UserProfile.model_json_schema(), indent=2, ensure_ascii=False)}\n\n"
    "Utente: {user_input}\nAgente:"
)

travel_response_prompt = (
    "Genera un TravelResponse dettagliato (itinerario, hotel, trasporti, eventi) per 3 giorni "
    "basato sui dati forniti. Restituisci SOLO JSON conforme allo schema.\n\n"
    f"Schema: {json.dumps(TravelResponse.model_json_schema(), indent=2, ensure_ascii=False)}\n\n"
    "Input combinato: {combined}\nAgente:"
)
