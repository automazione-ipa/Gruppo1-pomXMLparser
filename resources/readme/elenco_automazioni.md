# TravelForge Spark – Documentazione API & Agenti Intelligenti

Ecco un elenco completo e strutturato delle automazioni e agenti previsti, integrata con i requisiti di applicazione.
La costruzione della Knowledge Base con RAG e GPT è pensata per coprire tutto il flusso end-to-end:

## Requisiti di Automazione

### 1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI
- Scraping
- API Interne
- API Gateway
- API Esterne

### 2. CHATBOT (per costruire l'itinerario)
- RAG Ingestion / Generation

### 3. PRENOTAZIONI AUTOMATICHE
- In definizione
- Completo il processo di automazione con acquisto biglietti/prenotazioni, previo consenso utente. 

---

## 1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI

Ricerche periodiche su provider (?)
- https://www.booking.com
- https://www.trivago.com
- https://www.viviberlino.it/
- https://www.expedia.it/

Ad esempio, posso implementare un servizio di scraping per individuare le offerte, i prezzi migliori, ...

Valutare anche approccio tramite API per alcune infoe salvataggio in mongo / postgres. 

## 2. CHATBOT (per costruire l'itinerario)
Pipeline costruzione KB [Knowledge Base/Indice] per ricerche semantiche.

### 2.1 Obiettivo: aumentare la precisione della risposta del chatbot con informazioni recurate da KB. Anche detto processo di RAG [Retrieval-Augmented Generation]

 
### 2.2 RAG-Ingestion per la creazione dell'indice e dei suoi documenti.
Raccolgo informazioni da diversi provider per poter poi generare una risposta riguardo gli itinerari più precisa ed affidabile. Inoltre la ricerca semantica riduce i tempi di elaborazione della risposta.

Se non trovo le info cercate nella KB, prevedo funzione (function calling) di ricerca su web e notifico in admin dashboard questo evento -> andrà arrichita KB con quelle info. 

Automatismo (semi) di creazione KB anche grazie a interazione utente.

### 2.3 RAG-Generation: inserisco nel prompt dell'utente le informazioni raccolte dalla ricerca e le ripasso a GPT x generazione migliorata. 


### 🔧 Strategia Tecnologica per la KB

| Aspetto            | Scelta Tecnologica                                                 | Motivazione                                                       |
| ------------------ | ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **Storage base**   | Vector DB (es. Weaviate, Qdrant, Pinecone)                         | Permette embedding, similar search, domande e retrieval semantico |
| **Fallback**       | PostgreSQL (relazionale, dati strutturati: orari, prezzi certi)    | Per avere certezza su prezzi fissi/valori tabellari               |
| **Indicizzazione** | Embedding con modelli tipo `all-MiniLM` o `text-embedding-3-small` | Ottimale per semantica breve, costi bassi                         |

---

## 🚀 Elenco Automazioni / Agenti Previsti

### 1. **Agenti di Raccolta Dati (Scraper / RPA)**

* **Agente Musei e Attrazioni:**
  Scraping periodico da portali ufficiali città e siti museali (orari, prezzi, descrizioni, link)
* **Agente Eventi Temporanei:**
  Rilevamento eventi tramite API (Eventbrite, Meetup) o scraping da calendari locali
* **Agente Attività Outdoor e Itinerari:**
  Estrazione da blog, city guides, TripAdvisor usando NLP e scraping HTML
* **Agente Recensioni e Tips:**
  Aggregazione continua da Google Maps, blog di viaggio per arricchire i dati con opinioni

### 2. **Agenti di Normalizzazione e Pulizia Dati**

* Parsing e standardizzazione dei dati raccolti
* Normalizzazione formati orari, prezzi, date
* Verifica di coerenza e validità (es. link attivi, prezzi aggiornati)

### 3. **Agenti NLP e Embedding**

* Estrazione keyword e tagging semantico da testi non strutturati
* Generazione embedding vettoriali (Google Gecko o simili) per tutti i documenti
* Classificazione documenti per categorie e filtri (es. tipo attrazione, location, tipo evento)

### 4. **Agenti di Popolamento Vector DB**

* Caricamento dati puliti + embedding su Vertex AI Vector DB
* Aggiornamenti incrementali con versioning

### 5. **Scheduler & Validator**

* Scheduler per aggiornamenti periodici:

  * Musei/attrazioni: settimanale
  * Eventi: quotidiano o bisettimanale
* Validator automatico che segnala anomalie o dati mancanti
* Alert e logging per errori scraping o incoerenze

### 6. **Agenti di Recupero Fallback (DB relazionale e API)**

* Query su PostgreSQL per prezzi, orari fissi, disponibilità ticket
* Chiamate API live se disponibili (trasporti, prenotazioni)
* Validazione e caching risultati fallback

### 7. **Agent di Interrogazione e RAG**

* Gestione query utente in linguaggio naturale
* Generazione embedding query e ricerca in vector DB con filtri
* Aggregazione risultati semantici da Vector DB + fallback
* Preparazione contesto per GPT (Gemini) in modalità RAG

### 8. **Agent di Generazione Risposta (GPT + Function Calling)**

* Prompt engineering per output specifici (itinerari, prezzi, eventi)
* Gestione chiamate di funzioni (es. recupero prezzi, aggiornamento dati)
* Composizione risposta finale in Markdown o JSON

### 9. **Agent di Monitoraggio e Feedback**

* Raccolta feedback utente su risposte e itinerari generati
* Analisi metriche di accuratezza, tempi di risposta, copertura dati
* Automazioni di miglioramento continuo basate su feedback

---

### 🔄 **Workflow Integrato**

```mermaid
graph TD
A[Query Utente] --> B[Embedding + Vector Search]
B --> C{Risultati KB?}
C -- sì --> D[Prepara contesto + GPT generazione risposta]
C -- no --> E[Function calling fallback (prezzi, API)]
E --> D
D --> F[Output a utente]
```

---

### 📘 Contenuti da Inserire nella KB

| Categoria         | Fonte                                        | Metodo Raccoglimento               | Frequenza Update |
| ----------------- | -------------------------------------------- | ---------------------------------- | ---------------- |
| Musei & Monumenti | Portali ufficiali città, NostraCultura       | Scraping via RPA (Puppeteer + OCR) | 1/settimana      |
| Prezzi ingressi   | API ufficiali o scraping (es. Teide, Louvre) | RPA + validazione su portali       | 1/settimana      |
| Eventi temporanei | Eventbrite, Meetup, City Calendar            | API quando disponibili, o scraping | 1-2/giorni       |
| Attività outdoor  | Blog, city guides, Tripadvisor               | NLP + estrazione da testi HTML     | 1-2/settimane    |
| Recensioni / Tips | Google Maps, blog viaggi                     | Embedding + NLP                    | continuo (delta) |

---

### 🧠 Funzionalità Supportate dalla KB

| Use Case                                   | Meccanismo                                                 |
| ------------------------------------------ | ---------------------------------------------------------- |
| "Quanto costa entrare al Museo Egizio?"    | Query semantica + fallback su prezzo da tabella verificata |
| "Cosa vedere a Berlino in 3 giorni?"       | Retrieval attività + matching per durata e priorità        |
| "Ci sono eventi jazz a Lisbona in agosto?" | Ricerche event-centriche con filtro semantico + temporale  |
| "Quali attrazioni sono aperte di sera?"    | KB orari + filtro semantico su fascia oraria               |

---

### 🧩 Integrazione con GPT

* **Retrieval-augmented generation (RAG)**: il sistema recupera chunk semantici rilevanti da vector DB → questi vengono passati nel `context` al GPT (es. GPT-4o mini) per generare la risposta.
* **Function Calling con fallback**: se il contenuto non è in KB, GPT può chiamare una `function` per attivare scraping / API provider.

---

### 🔄 Pipeline di Popolamento KB

1. **Scraper agents**:

   * Navigano portali di città / cultura
   * Estraggono nome, descrizione, orari, prezzo, link ufficiale
   * Normalizzazione dati in formato JSON

2. **NLP agents**:

   * Estraggono keyword da articoli/blog
   * Embedding + tagging semantico
   * Identificazione eventi o attività emergenti

3. **Scheduler & Validator**:

   * Cron settimanale per musei & attrazioni
   * Daily fetch per eventi
   * Verifica automatica link e coerenza prezzi

---



### 📂 Struttura Dati KB (semplificata)

```json
{
  "type": "museo",
  "title": "Museo Egizio di Torino",
  "location": "Torino, Italia",
  "description": "Uno dei più antichi musei egizi del mondo...",
  "category": ["cultura", "storico"],
  "tags": ["egizio", "archeologia", "storico"],
  "price": 18,
  "opening_hours": {
    "lun": "09:00-18:30",
    "mar": "09:00-18:30",
    ...
  },
  "official_link": "https://museoegizio.it",
  "embedding": [/* vector */]
}
```



### 🎯 Spiegazione campi chiave

| Campo       | Scopo                                                           |
| ----------- | --------------------------------------------------------------- |
| `content`   | Testo semantico da embeddare → usato per similar search         |
| `embedding` | Vettore numerico calcolato con modello embedding                |
| `metadata`  | Filtraggio / faceting (es. per città, categoria, prezzo, orari) |
| `id`        | Utile per gestione update o deduplicazione                      |

---

### 🧠 Come funziona nel retrieval

* **Query dell’utente** viene trasformata in embedding → `similarity search` nel Vector DB su `content`.
* **Filtri secondari** (es. `location == Torino`, `price < 20`) applicati su `metadata`.
* Risultati → forniti a GPT via `context` nel RAG.

---

### 🔁 Se usi DB ibrido (Vector + Relazionale)

* Vector DB → `descrizioni`, `esperienze`, `cosa fare`, `raccomandazioni`
* Relazionale (PostgreSQL) → `prezzi`, `orari`, `URL`, dati con **precisione numerica o regole chiare**

---

### ✅ Best practices

* Normalizza `content` per essere **autosufficiente** anche fuori dal JSON (es. nei chunk RAG)
* Aggiungi un campo `updated_at` se prevedi refresh periodici
* Non mettere l’`embedding` se viene calcolato in fase di inserimento (alcuni DB lo supportano)

---

---

## 🧭 3. Responsabilità del Nostro Team


Definito il seguente **framework** per:

1. **Responsabilità del nostro team**
2. **Interfacce tra API e agenti**
3. **Architettura dati (DB relazionali, Mongo, Vector DB)**
4. **Scraping pipeline** con tabelle di output ben definite

In questo modo lo scrum master e tutti gli altri componenti del team avranno una visione chiara di cosa forniamo e cosa ci aspettiamo come input/output.

**Ruolo:**

* Implementiamo gli **agenti intelligenti** (es. Itinerary Auto-Builder, Tourism Data Integrator, Ticket Price Estimator).
* Manteniamo **pipeline dati** (scraping, normalizzazione, enrichment AI, KB update).
* Espone **API interne** che il team API Gateway chiama per ottenere risposte.
* Gestiamo **vector DB** e **RAG pipeline** per fornire risposte grounding su dati reali.

**Non siamo responsabili di:**

* Autenticazione utenti
* Orchestrazione API Gateway
* Frontend UI/UX
* Logiche di billing o monetizzazione

---

## 🔗 4. Interfacce Comuni (API Contracts)

Esempio di API che il team API ci chiama:

```http
POST /api/generate_itinerary
{
  "city": "Berlin",
  "start_date": "2025-09-20",
  "duration_days": 5,
  "preferences": ["culture", "nightlife"]
}
```

**La nostra risposta (contratto atteso):**

```jsonc
{
  "itinerary": [
    {
      "day": 1,
      "morning": ["Pergamon Museum", "Brunch in Mitte"],
      "afternoon": ["Berlin Wall Memorial"],
      "evening": ["Tech Meetup at Factory Berlin"]
    },
    ...
  ],
  "cost_estimate": {
    "tickets": 75.50,
    "transport": 20.00,
    "total": 95.50,
    "currency": "EUR"
  },
  "source": "RAG+LLM"
}
```

Questo implica che noi:

* Chiamiamo il **gpt-4o-mini** con prompt arricchito (RAG su Vector DB).
* Recuperiamo dati tabellari da **DB classici** (es. prezzi biglietti).
* Eseguiamo un **cost estimator** e normalizziamo output.

---

## 🗂️ 5. Architettura Dati (DB + Vector DB)

### 📊 Database Classici (SQL o MongoDB)

1. **Tabella: attractions**

```sql
CREATE TABLE attractions (
  id SERIAL PRIMARY KEY,
  city VARCHAR(255),
  name TEXT,
  category VARCHAR(100),
  address TEXT,
  open_hours JSONB,
  price_eur NUMERIC,
  url TEXT,
  last_updated TIMESTAMP
);
```

2. **Tabella: events**

```sql
CREATE TABLE events (
  id VARCHAR PRIMARY KEY,
  city VARCHAR(255),
  title TEXT,
  category TEXT[],
  start_datetime TIMESTAMP,
  end_datetime TIMESTAMP,
  venue_name TEXT,
  venue_address TEXT,
  price_eur NUMERIC,
  language VARCHAR(5),
  tags TEXT[],
  last_updated TIMESTAMP
);
```

3. **Tabella: ticket\_prices**

```sql
CREATE TABLE ticket_prices (
  id SERIAL PRIMARY KEY,
  attraction_id INT REFERENCES attractions(id),
  date DATE,
  price_eur NUMERIC,
  source TEXT,
  last_updated TIMESTAMP
);
```

4. **Tabella: transport\_tariffs**

```sql
CREATE TABLE transport_tariffs (
  id SERIAL PRIMARY KEY,
  city VARCHAR(255),
  provider TEXT,
  mode TEXT, -- carsharing, scooter, bus
  price_per_min NUMERIC,
  currency VARCHAR(5),
  last_updated TIMESTAMP
);
```

5. **Tabella: accommodations** (opzionale se usiamo API esterne tipo Booking.com)

---

### 📦 MongoDB (contenuti non strutturati)

* **collection: raw\_scraping\_logs**

```jsonc
{
  "_id": "...",
  "source": "eventbrite",
  "html_snapshot": "<html>....</html>",
  "scraped_at": "2025-09-13T12:00:00Z"
}
```

Utile per audit/debug e per rianalizzare dati in caso di bug.

---

### 🔎 Vector DB (Vertex AI Matching Engine)

* **Index:** `events_index`

  * `id` → event\_id
  * `embedding` → calcolato su `description + tags + category`
  * `metadata`: `{ "city": "...", "category": [...], "price_eur": ... }`

* **Index:** `attractions_index`

  * simile a sopra, embedding calcolato su descrizione + categoria

---

## 🕷️ 6. Pipeline di Scraping (Definizione Migliore)

### Step:

1. **Scheduler (Cloud Scheduler)** → Triggera scraping periodico
2. **Scraping (Puppeteer)** → estrazione dati raw
3. **Parsing & Normalizzazione** → mappe JSON normalizzate secondo schema
4. **Data Validation** → check campi obbligatori, deduplica
5. **Storage in DB Classici**
6. **Calcolo Embeddings & Upsert su Vector DB**
7. **Versionamento snapshot**

---

### 📝 Esempio Integrato

Pseudo-codice in Python:

```python
def run_scraping_job(city):
    raw_events = scrape_eventbrite(city)
    parsed_events = normalize_events(raw_events)
    store_to_db(parsed_events)  # SQL insert/update
    embeddings = build_embeddings(parsed_events)
    upsert_to_vector_db(embeddings)
    save_snapshot(parsed_events)
```