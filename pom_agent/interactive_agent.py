"""Interactive function call agent"""
import logging
import json
from pom_agent.gpt_wrap import chat_functions, gpt_choice_message
from pom_agent.functions import FUNCTIONS
from pom_agent.agent_functions import parse_pom_file, write_file, read_file, load_json
from pom_agent.config import POM_FILE

logger = logging.getLogger(__name__)

FUNCTION_DISPATCHER = {
    "parse_pom_file": parse_pom_file,
    "write_file": write_file,
    "read_file": read_file,
    "load_json": load_json
}


class PomAgent:
    def __init__(self):
        self.chat_history = []
        logger.info("🤖 Avvio del POM Agent...")

        initial_prompt = f"""
            Sei un assistente tecnico. 
            Il tuo compito è leggere un file pom.xml da percorso '{POM_FILE}', estrarre le informazioni e salvarle in un file JSON chiamato 'pom_info.json'.

            Dopo l'elaborazione, l'utente potrà farti domande su:
            - dipendenze del progetto
            - struttura XML
            - tecnologie e versioni usate
        """

        response = chat_functions(
            user_message=initial_prompt,
            functions=FUNCTIONS,
            function_call="auto"
        )
        message = gpt_choice_message(response)
        self.chat_history.append(message)

        self._handle_functions(message)

    def _handle_functions(self, message):
        while message.get("function_call"):
            fname = message["function_call"]["name"]
            args = json.loads(message["function_call"]["arguments"])

            if fname in FUNCTION_DISPATCHER:
                logger.info(f"⚙️  Eseguo funzione: {fname} con args: {args}")
                result = FUNCTION_DISPATCHER[fname](**args)

                function_response = {
                    "role": "function",
                    "name": fname,
                    "content": json.dumps(result)
                }
                self.chat_history.append(function_response)

                response = chat_functions(
                    messages=self.chat_history,
                    functions=FUNCTIONS,
                    function_call="auto"
                )
                message = gpt_choice_message(response)
                self.chat_history.append(message)
            else:
                logger.warning(f"❌ Funzione non gestita: {fname}")
                break

    def ask(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})

        response = chat_functions(
            messages=self.chat_history,
            functions=FUNCTIONS,
            function_call="auto"
        )
        message = gpt_choice_message(response)
        self.chat_history.append(message)

        if message.get("function_call"):
            self._handle_functions(message)
        else:
            logger.info("🗨️ %s", message.get("content"))


def run_pom_agent():
    agent = PomAgent()
    while True:
        user_input = input("\n❓ Fai una domanda sul pom.xml (oppure digita 'exit'): ")
        if user_input.lower() == "exit":
            break
        agent.ask(user_input)
