from src.resources.config.settings import Base, engine
from src.resources.db import models

def init_db():
    """Crea le tabelle nel database se non esistono."""
    Base.metadata.create_all(bind=engine)
