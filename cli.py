"""Command Line Interface for the PomAgent"""

import sys
from pom_agent.interactive_agent import PomAgent

MENU = """
========= 📦 POM Agent CLI =========

1. Mostra tutte le dipendenze
2. Mostra versioni delle tecnologie usate
3. Mostra struttura XML del pom.xml
4. Fai una domanda personalizzata
0. Esci

Scegli un'opzione: """

PREDEFINED_QUESTIONS = {
    "1": "Quali sono tutte le dipendenze elencate nel pom.xml?",
    "2": "Quali tecnologie e versioni vengono usate nel progetto?",
    "3": "Puoi mostrarmi la struttura XML del pom.xml?"
}


def main():
    print("🤖 Avvio dell'agente (modalità CLI)...")
    agent = PomAgent()

    while True:
        choice = input(MENU).strip()

        if choice == "0":
            print("👋 Uscita.")
            sys.exit(0)
        elif choice in PREDEFINED_QUESTIONS:
            agent.ask(PREDEFINED_QUESTIONS[choice])
        elif choice == "4":
            question = input("Scrivi la tua domanda: ").strip()
            agent.ask(question)
        else:
            print("❗ Scelta non valida.")


if __name__ == "__main__":
    main()
