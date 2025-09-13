# src/resources/db/crud.py
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from src.resources.db import models

def create_user(db: Session, user_id: str):
    u = db.query(models.User).filter_by(user_id=user_id).first()
    if u:
        return u
    u = models.User(user_id=user_id)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def create_travel_request(db: Session, travel_id: str, user_id: str,
                          origin: str = None, destination: str = None, start_date: str = None,
                          end_date: str = None, interests: list = None, year_season_or_month: str = None):
    tr = models.TravelRequest(
        travel_id=travel_id,
        user_id=user_id,
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        interests=interests or [],
        year_season_or_month=year_season_or_month
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr

def get_travel_request(db: Session, travel_id: str):
    return db.query(models.TravelRequest).filter_by(travel_id=travel_id).first()

def update_structured_output(db: Session, travel_id: str, structured_output: dict):
    tr = get_travel_request(db, travel_id)
    if not tr:
        raise ValueError("TravelRequest not found")
    # Aggiorna campi specifici da dict (per allineamento Pydantic)
    tr.origin = structured_output.get('origin', tr.origin)
    tr.destination = structured_output.get('destination', tr.destination)
    tr.start_date = structured_output.get('start_date', tr.start_date)
    tr.end_date = structured_output.get('end_date', tr.end_date)
    tr.interests = structured_output.get('interests', tr.interests)
    tr.structured_output = structured_output  # Full JSON
    db.commit()
    db.refresh(tr)
    return tr

def append_message_to_travel(db: Session, travel_id: str, role: str, content: str):
    tr = get_travel_request(db, travel_id)
    if not tr:
        raise ValueError("TravelRequest not found")
    if tr.messages is None:
        tr.messages = []
    msg = {"role": role, "content": content, "ts": datetime.utcnow().isoformat() + "Z"}
    tr.messages.append(msg)
    db.commit()
    db.refresh(tr)
    return tr

# Alias
save_message = append_message_to_travel

def create_llm_session(db: Session, travel_id: str, model: str, agent: str = None, session_conversation_id: str = None):
    sid = str(uuid.uuid4())[:36]
    sess = models.LLMSession(
        session_id=sid,
        travel_id=travel_id,
        model=model,
        agent=agent,
        session_conversation_id=session_conversation_id
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    # Set as current
    tr = get_travel_request(db, travel_id)
    if tr:
        tr.current_llm_session_id = sess.session_id
        tr.current_llm_model = model
        tr.current_llm_agent = agent
        db.commit()
    return sess

def end_llm_session(db: Session, session_id: str):
    s = db.query(models.LLMSession).filter_by(session_id=session_id).first()
    if not s:
        raise ValueError("LLM session not found")
    s.ended_at = datetime.utcnow()
    db.commit()
    # Clear current
    tr = get_travel_request(db, s.travel_id)
    if tr and tr.current_llm_session_id == s.session_id:
        tr.current_llm_session_id = None
        tr.current_llm_model = None
        tr.current_llm_agent = None
        db.commit()
    return s

# Nuove/aggiornate per PersonalProfile
def get_personal_profile(db: Session, user_id: str):
    return db.query(models.PersonalProfile).filter_by(user_id=user_id).first()

def update_personal_profile(db: Session, user_id: str, profile_data: dict):
    pp = get_personal_profile(db, user_id)
    if not pp:
        pp = models.PersonalProfile(user_id=user_id)
        db.add(pp)
    pp.name = profile_data.get('name', pp.name)
    pp.age = profile_data.get('age', pp.age)
    pp.preferences = profile_data.get('preferences', pp.preferences or [])
    pp.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pp)
    return pp

# Nuove per TravelResponse
def create_travel_response(db: Session, travel_id: str, response_data: dict, raw_llm_response: str = None):
    resp_id = f"resp-{uuid.uuid4().hex[:12]}"
    resp = models.TravelResponse(
        response_id=resp_id,
        travel_id=travel_id,
        itinerary=response_data.get('itinerary', []),
        hotels=response_data.get('hotels', []),
        transport=response_data.get('transport', []),
        events=response_data.get('events', []),
        raw_llm_response=raw_llm_response
    )
    db.add(resp)
    db.commit()
    db.refresh(resp)
    return resp

def get_travel_response(db: Session, response_id: str):
    return db.query(models.TravelResponse).filter_by(response_id=response_id).first()