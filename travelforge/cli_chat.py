# src/cli_chat.py
import json
import uuid
from src.resources.config.settings import SessionLocal
from src.resources.db.base import init_db
from travel_agent import TravelChatAgent
from src.resources.db import crud
from src.core.pipeline_runner import run_pipeline
from src.resources.utils.logger import get_logger

logger = get_logger("cli_chat")

def print_help():
    help_text = """
Commands:
  /help                 Show this help
  /new                  Create new conversation (new travel_request)
  /open <travel_id>     Open existing conversation by travel_id
  /show                 Show current travel_request summary
  /messages             Show conversation messages
  /generate             Trigger generate-itinerary (saves structured_output)
  /exit                 Exit
Typing anything else sends it as a message from the user.
"""
    print(help_text.strip())

def show_tr_summary(db, travel_id):
    tr = crud.get_travel_request(db, travel_id)
    if not tr:
        print("No travel_request found.")
        return
    print(f"TravelRequest {tr.travel_id} (user={tr.user_id})")
    print(f"  destination: {tr.destination}")
    print(f"  origin: {tr.origin}")
    print(f"  when: {tr.year_season_or_month}")
    print(f"  status: {tr.status}")
    print(f"  structured_output: {tr.structured_output}")
    print(f"  messages: {len(tr.messages) if tr.messages else 0}")

def show_messages(db, travel_id):
    tr = crud.get_travel_request(db, travel_id)
    if not tr:
        print("No travel_request found.")
        return
    if not tr.messages:
        print("No messages.")
        return
    for i, m in enumerate(tr.messages, 1):
        ts = m.get("ts", "")
        role = m.get("role", "")
        content = m.get("content", "")
        print(f"{i:03d} | {ts} | {role}: {content}")

def main():
    print("Travel Chat CLI")
    user_id = input("User ID (default 'test-user'): ") or "test-user"

    db = SessionLocal()
    init_db()

    # ensure user exists
    crud.create_user(db, user_id)

    # create initial travel_request and agent
    tr_id = f"tr-{uuid.uuid4().hex[:12]}"
    crud.create_travel_request(db, tr_id, user_id)
    agent = TravelChatAgent(db=db, user_id=user_id, travel_id=tr_id)

    print(f"\nConversation id (internal): {agent.travel_id}\n")
    print("Type '/help' for commands. Type 'exit' to quit.\n")

    last_user_message = ""
    conversation_id = agent.travel_id

    while True:
        text = input("You: ").strip()
        if not text:
            continue

        if text.startswith("/"):
            parts = text.split()
            cmd = parts[0].lower()

            if cmd == "/help":
                print_help()
                continue
            elif cmd == "/new":
                new_id = f"tr-{uuid.uuid4().hex[:12]}"
                crud.create_travel_request(db, new_id, user_id)
                agent = TravelChatAgent(db=db, user_id=user_id, travel_id=new_id)
                conversation_id = new_id
                print(f"New conversation: {new_id}")
                continue
            elif cmd == "/open":
                if len(parts) < 2:
                    print("Usage: /open <travel_id>")
                    continue
                tid = parts[1]
                tr_obj = crud.get_travel_request(db, tid)
                if not tr_obj:
                    print("travel_request not found:", tid)
                    continue
                agent = TravelChatAgent(db=db, user_id=user_id, travel_id=tid)
                conversation_id = tid
                print(f"Opened conversation {tid}")
                continue
            elif cmd == "/show":
                show_tr_summary(db, agent.travel_id)
                continue
            elif cmd == "/messages":
                show_messages(db, agent.travel_id)
                continue
            elif cmd in ["/generate", "genera", "generate itinerary"]:
                try:
                    if not last_user_message:
                        last_user_message = "Voglio fare un viaggio a Berlino di 3 giorni, arte e cibo."
                    # --- Step 1: Esegui pipeline ---
                    response = run_pipeline(
                        user_input=last_user_message,
                        conversation_id=conversation_id,
                        user_id=user_id
                    )
                    logger.info(f"[{user_id} | {conversation_id}] Itinerario generato correttamente.")
                    print("AI:", json.dumps(response, indent=2, ensure_ascii=False))
                    # --- Step 2: Salva TravelResponse nel DB ---
                    crud.create_travel_response(
                        db=db,
                        travel_id=conversation_id,
                        response_data=response,
                        raw_llm_response=json.dumps(response),
                        # salva raw output per tracciamento
                    )
                    db.commit()
                    logger.info(
                        f"[{user_id} | {conversation_id}] TravelResponse salvata nel DB.")

                except Exception as e:
                    logger.error(f"Pipeline error: {e}")
                    print("AI: Errore interno. Controlla logs o riprova.")
                continue
            elif cmd in ["/exit", "/quit"]:
                break

            print("Unknown command. Type /help for commands.")
            continue

        # Default: treat as user message; persist in agent
        last_user_message = text
        response = agent.run(text)
        print(f"AI: {response}\n")

    db.close()

if __name__ == "__main__":
    main()
