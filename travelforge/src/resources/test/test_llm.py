# test_llm.py
from config import OPENAI_API_KEY
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from pydantic import BaseModel

llm = init_chat_model("openai:gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.0)

class Sample(BaseModel):
    destination: str
    days: int

parser = PydanticOutputParser(pydantic_object=Sample)

try:
    # con invoke / llm_output_parser (se supportato)
    out = llm.invoke("Fammi un TravelRequest breve per Berlino di 3 giorni", llm_output_parser=parser)
    print("Parsed (invoke):", out)
except TypeError:
    # fallback a run / invoke diverso
    print("invoke con llm_output_parser non supportato, prova a chiamare il chain/agent.")
