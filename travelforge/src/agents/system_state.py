# system_state.py
from pydantic import BaseModel
from typing import Optional
from core.models import TravelRequest, UserProfile, TravelResponse


class SystemState(BaseModel):
    user_profile: Optional[UserProfile] = None
    travel_request: Optional[TravelRequest] = None
    travel_response: Optional[TravelResponse] = None
