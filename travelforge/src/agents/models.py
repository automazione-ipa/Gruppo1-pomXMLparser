# models.py
from pydantic import BaseModel
from typing import List, Optional

class TravelRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interests: List[str] = []

class UserProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    preferences: List[str] = []

class TravelResponse(BaseModel):
    itinerary: List[str] = []
    hotels: List[str] = []
    transport: List[str] = []
    events: List[str] = []
