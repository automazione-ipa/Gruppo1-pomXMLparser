from src.resources.config.settings import SessionLocal
from src.resources.db.base import init_db
from src.resources.db import crud

def main():
    db = SessionLocal()
    init_db()

    print("✅ Database connesso!")

    user = crud.create_user(db, "test-user")
    print("👤 Utente:", user.user_id)

    travel = crud.create_travel_request(db, "test-user", "Tokyo", "Milano", "Primavera 2025")
    print("🧳 Travel ID:", travel.travel_id)

    conv = crud.create_conversation(db, "test-user", travel.travel_id)
    print("💬 Conversation ID:", conv.conversation_id)

    db.close()

if __name__ == "__main__":
    main()
