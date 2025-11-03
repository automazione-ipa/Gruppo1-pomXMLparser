# models.py
from pydantic import BaseModel
from typing import List, Optional


class TravelRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interests: Optional[List[str]] = None


class UserProfile(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    preferences: Optional[List[str]] = None


# TODO: update TravelResponse and app logic
class TravelResponse(BaseModel):
    itinerary: List[str] = []
    hotels: List[str] = []
    transport: List[str] = []
    events: List[str] = []
