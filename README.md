**README**

# AI-Powered Maven Dependency Agent

Un MVP Python per l’analisi e l’esplorazione delle dipendenze Maven di un progetto tramite GPT e graph analytics.

## Changelog

### Langchain Agent - 06.10.2025
* Aggiunto agente smart langchain e tool con CRUD su postgreSQL, per avere anche la gestione di utenti e conversazioni.
* Aggiornato README.md con le informazioni su Agenzia Viaggi Smart
* Unificato requirements.txt
* .gitignore
---

## 📁 Struttura del progetto

Organizziamo il codice in un package principale `pom_agent` e uno script CLI in `cli.py`.

```
.
├── pom_agent/                # Modulo principale
│   ├── __init__.py
│   ├── config.py             # costanti, logging centralizzato, utilità JSON
│   ├── pomxml_extractor.py   # parse_pom_file: parsing POM
│   ├── agent_functions.py    # implementazione funzioni callable (parse, read, write, load_json)
│   ├── functions.py          # schema JSON per le funzioni GPT
│   ├── gpt_wrap.py           # wrapper OpenAI Chat API
│   ├── interactive_agent.py  # classe PomAgent + run_pom_agent()
│   └── graph_util.py         # funzioni per costruire e interrogare grafo di dipendenze
├── resources/
│   └── pom.xml               # file POM di esempio
├── cli.py                    # interfaccia a menu per l’agente
├── run_agent.py              # entrypoint semplice
├── setup.py                  # configurazione pip install
├── Makefile                  # comandi utili
└── requirements.txt          # dipendenze
```

> Il codice sorgente principale è in `pom_agent/`, per facilitare estensioni e test.

---

## 🚀 Funzionalità core

1. **Parsing POM** (`pom_agent.pomxml_extractor.parse_pom_file`)

   * Estrae `groupId`, `artifactId`, `version`, `packaging` e dipendenze.
2. **Salvataggio JSON** (`pom_agent.agent_functions.write_file`)

   * Produce `pom_info.json` con struttura:

     ```json
     {
       "project": {...},
       "dependencies": [{...}, ...]
     }
     ```
3. **Chat interattiva GPT** (`pom_agent.interactive_agent.PomAgent`)

   * Domande sul POM via function calling (parse, read, write, load\_json).
4. **CLI/Menu** (`cli.py`)

   * Menu numerato con domande predefinite e supporto custom.
5. **Grafo delle dipendenze** (`pom_agent.graph_util`)

   * Utilizza `networkx` per creare un DiGraph di project→dependency.
   * Query: cammini, cicli, filtri per scope.

---

## 🔧 Installazione

```bash
git clone <url>
cd <repo>
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
make install
```

---

## 📋 Comandi principali

| Comando         | Descrizione                                               |
| --------------- | --------------------------------------------------------- |
| `make install`  | Installa il progetto in modalità editable                 |
| `make run`      | Avvia sessione interattiva (equiv. `python run_agent.py`) |
| `make cli`      | Avvia menu CLI (`python cli.py`)                          |
| `pom-agent`     | Entry point interattivo (via console\_scripts)            |
| `pom-agent-cli` | Menu CLI (via console\_scripts)                           |

---

## 🛠️ Config & Logging

* `pom_agent.config.setup_logging(level)` imposta il root logger.
* Costanti in `pom_agent.config`:

  * `POM_FILE`, `TXT_REPORT`, `RECIPIENTS`, `NVD_URL`.
  * Namespace Maven per `ElementTree`.

---

## ⚙️ Funzioni callable GPT

* `parse_pom_file(pom_path: str) -> dict`
* `read_file(path: str) -> str`
* `write_file(path: str, content: str) -> dict`
* `load_json(path: str) -> dict`

---

## 📈 Grafo delle Dipendenze

Modulo di utilità (`pom_agent.graph_util`):

```python
from networkx import DiGraph

def build_dependency_graph(data: dict) -> DiGraph:
    g = DiGraph()
    project = data['project']['artifactId']
    g.add_node(project, **data['project'])
    for dep in data['dependencies']:
        key = dep['artifactId']
        g.add_node(key, **dep)
        g.add_edge(project, key, scope=dep['scope'])
    return g
```

**Esempi di interrogazione**:

* `list(g.successors(project))`
* `list(nx.simple_cycles(g))`
* `[n for n, e in g[project].items() if e['scope']=='test']`

---

## 🔮 Next Steps

1. **CVE-check**: integrazione NVD per versioni vulnerabili.
2. **Multi-modulo**: supporto a progetti Maven multi-module.
3. **Esportazione**: GraphViz, YAML, Dashboard web.
4. **AI Enrichment**: spiegazioni e raccomandazioni LLM.
5. Si utilizza come base per inserire l'MVP per Agenzia Viaggi Smart "TravelForge". Segue una panoramica complessiva. 

**Unificare i due progetti e avere la gestione del parsing HTML come tool non sarebbe male. Buon lavoro!**

---

## 🔍 1️⃣ LangChain Travel Agency

### Idea iniziale

Automazione:


1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI
-> scraping/API

2. CHATBOT (per costruire l'itinerario)
-> RAG Ingestion / Generation

3. PRENOTAZIONI AUTOMATICHE
- in definizione

1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI

Ricerche periodiche su provider (?)
- https://www.booking.com
- https://www.trivago.com
- https://www.viviberlino.it/
- https://www.expedia.it/

Ad esempio, posso implementare un servizio di scraping per individuare le offerte, i prezzi migliori, ...

Valutare anche approccio tramite API per alcune infoe salvataggio in mongo / postgres. 


2. CHATBOT (per costruire l'itinerario)
Pipeline costruzione KB [Knowledge Base/Indice] per ricerche semantiche.

2.1 Obiettivo: aumentare la precisione della risposta del chatbot con informazioni recurate da KB. Anche detto processo di RAG [Retrieval-Augmented Generation]

 
2.2 RAG-Ingestion per la creazione dell'indice e dei suoi documenti.
Raccolgo informazioni da diversi provider per poter poi generare una risposta riguardo gli itinerari più precisa ed affidabile. Inoltre la ricerca semantica riduce i tempi di elaborazione della risposta.

Se non trovo le info cercate nella KB, prevedo funzione (function calling) di ricerca su web e notifico in admin dashboard questo evento -> andrà arrichita KB con quelle info. 

Automatismo (semi) di creazione KB anche grazie a interazione utente.


2.3 RAG-Generation: inserisco nel prompt dell'utente le informazioni raccolte dalla ricerca e le ripasso a GPT x generazione migliorata. 

3. PRENOTAZIONI AUTOMATICHE

Completo il processo di automazione con acquisto biglietti/prenotazioni, previo consenso utente. 

---

### Langchain Pipeline
Hai appena eseguito la **prima pipeline completa multi-agente** basata su **LangChain 1.0a10** e **Pydantic v2**, composta da tre agenti distinti:

### a) `travel_request_agent`

* Input: testo naturale dell’utente (`"Roma, 3 giorni"`).
* Output: un oggetto `TravelRequest`, generato dal modello (`gpt-4o-mini`) in formato strutturato conforme al JSON schema.
* In questo caso:

  ```json
  {
    "origin": "Roma",
    "destination": null,
    "start_date": null,
    "end_date": null,
    "interests": []
  }
  ```

  Il modello ha interpretato “Roma” come origine ma non come destinazione (tipico in input brevi).
  Gli altri campi restano `null` in attesa di un eventuale follow-up (potresti aggiungere un passo di “completion” per completare il viaggio).

---

### b) `user_profile_agent`

* Riceve la stessa input conversazionale, ma costruisce un `UserProfile` basandosi sulle preferenze implicite.
* Output:

  ```json
  {
    "name": null,
    "age": null,
    "preferences": ["Roma", "3 giorni"]
  }
  ```

  Quindi deduce preferenze di durata e destinazione dal contesto utente.

---

### c) `travel_response_agent`

* Combina `TravelRequest` + `UserProfile` e produce un `TravelResponse`: un piano completo di viaggio coerente.
* Output:

  ```json
  {
    "itinerary": [
      "Giorno 1: Arrivo nella città, check-in in hotel, visita al centro storico, cena in un ristorante tipico.",
      "Giorno 2: Tour guidato in città, visita a musei, pranzo in un locale locale, pomeriggio libero per shopping, cena in un ristorante di cucina internazionale.",
      "Giorno 3: Escursione in una località vicina, pranzo al sacco, ritorno in serata, check-out dall'hotel e partenza."
    ],
    "hotels": ["Hotel Centrale", "Hotel Vista Mare", "Hotel Boutique"],
    "transport": ["Treno per la città", "Autobus per l'escursione", "Taxi per gli spostamenti in città"],
    "events": ["Festival locale il giorno 2", "Mercato artigianale il giorno 1", "Concerto dal vivo il giorno 3"]
  }
  ```

Il modello ha rispettato lo schema Pydantic e generato un output completamente strutturato — validato e serializzato correttamente.

---

## 🧠 2️⃣ REPORT COMPLETO DEL TOOL

### 🧩 Nome progetto

**LangChain Travel Planner (Jacky Project)**

---

### ⚙️ Architettura generale

| Componente             | Ruolo                                     | Tecnologia             |
| ---------------------- | ----------------------------------------- | ---------------------- |
| **LangChain 1.0a10**   | Framework LLM e gestione agenti           | Python                 |
| **OpenAI GPT-4o-mini** | Modello conversazionale generativo        | via `langchain_openai` |
| **Pydantic v2**        | Validazione e schema dei dati strutturati | Python                 |
| **dotenv**             | Gestione sicura delle chiavi API          | Python                 |
| **agents.py**          | Definizione dei tre agenti principali     | LangChain Agents       |
| **main.py**            | Pipeline orchestratrice                   | Python                 |
| **pydantic_utils.py**  | Helper compatibili con Pydantic v2        | Custom                 |

---

### 🧠 Agenti implementati

| Agente                  | Input                           | Output           | Descrizione                                                     |
| ----------------------- | ------------------------------- | ---------------- | --------------------------------------------------------------- |
| `travel_request_agent`  | Conversazione utente            | `TravelRequest`  | Interpreta la richiesta di viaggio in formato strutturato.      |
| `user_profile_agent`    | Conversazione utente            | `UserProfile`    | Estrae o costruisce il profilo dell’utente in base al contesto. |
| `travel_response_agent` | `TravelRequest` + `UserProfile` | `TravelResponse` | Genera itinerario, hotel, trasporti ed eventi coerenti.         |

---

### 🧱 Tipi Pydantic usati (Pydantic v2)

```python
class TravelRequest(BaseModel):
    origin: str | None
    destination: str | None
    start_date: str | None
    end_date: str | None
    interests: list[str] = []

class UserProfile(BaseModel):
    name: str | None
    age: int | None
    preferences: list[str] = []

class TravelResponse(BaseModel):
    itinerary: list[str]
    hotels: list[str]
    transport: list[str]
    events: list[str]
```

---

### 🧩 Flusso dati

```text
Utente → TravelRequest Agent → UserProfile Agent → TravelResponse Agent → Output finale (JSON)
```

Ogni agente usa il proprio **schema Pydantic** come `response_format`, in modo che l’LLM restituisca direttamente JSON conforme.
I risultati vengono **validati e convertiti** con `model_validate()` e `model_dump()` (API Pydantic v2).

---

### 🧰 Funzioni chiave implementate

| Funzione                        | File                | Scopo                                                            |
| ------------------------------- | ------------------- | ---------------------------------------------------------------- |
| `to_serializable_v2()`          | `pydantic_utils.py` | Conversione sicura di oggetti Pydantic v2 in JSON serializzabile |
| `to_pydantic_v2()`              | `pydantic_utils.py` | Validazione dinamica di dict/string in istanza Pydantic          |
| `run_compiled_agent()`          | `agents.py`         | Esecuzione sincrona di agenti LangChain compilati                |
| `extract_structured_response()` | `agents.py`         | Estrazione automatica del JSON strutturato da grafi LangChain    |
| `run_pipeline()`                | `main.py`           | Orchestrazione sequenziale degli agenti e serializzazione finale |

---

### 🧾 Output finale (per input: “Roma, 3 giorni”)

```json
{
  "TravelRequest": {
    "origin": "Roma",
    "destination": null,
    "start_date": null,
    "end_date": null,
    "interests": []
  },
  "UserProfile": {
    "name": null,
    "age": null,
    "preferences": ["Roma", "3 giorni"]
  },
  "TravelResponse": {
    "itinerary": [
      "Giorno 1: Arrivo nella città, check-in in hotel, visita al centro storico, cena in un ristorante tipico.",
      "Giorno 2: Tour guidato in città, visita a musei, pranzo in un locale locale, pomeriggio libero per shopping, cena in un ristorante di cucina internazionale.",
      "Giorno 3: Escursione in una località vicina, pranzo al sacco, ritorno in serata, check-out dall'hotel e partenza."
    ],
    "hotels": ["Hotel Centrale", "Hotel Vista Mare", "Hotel Boutique"],
    "transport": ["Treno per la città", "Autobus per l'escursione", "Taxi per gli spostamenti in città"],
    "events": ["Festival locale il giorno 2", "Mercato artigianale il giorno 1", "Concerto dal vivo il giorno 3"]
  }
}
```

---

### 🧾 Conclusione

✅ **Funzionalità core confermata:**
Il sistema genera in automatico una catena coerente tra richiesta utente → strutturazione → profilo → itinerario.

✅ **Compatibilità garantita:**

* LangChain 1.0a10 (nuovo sistema a grafi)
* Pydantic v2 (nuovo sistema `model_validate` e `model_json_schema`)

✅ **Architettura pronta per estensioni:**
Puoi aggiungere:

* Tool personalizzati (es. API di voli, hotel, meteo)
* Persistenza dei risultati in DB
* Interfaccia web (Streamlit, FastAPI, o Next.js)
