# Requisiti di Automazione

1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI
- scraping/API

2. CHATBOT (per costruire l'itinerario)
- RAG Ingestion / Generation

3. PRENOTAZIONI AUTOMATICHE
- in definizione

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


## 3. PRENOTAZIONI AUTOMATICHE

Completo il processo di automazione con acquisto biglietti/prenotazioni, previo consenso utente. 


---


# TravelForge Spark – Documentazione API & Agenti Intelligenti

## 6. Descrizione delle API REST Necessarie

Definita una prima bozza per la definizione di API REST, da confrontare con il team dedicato.

### 6.1 Autenticazione e Gestione Utenti

| Metodo | Endpoint              | Descrizione                           |
| ------ | --------------------- | ------------------------------------- |
| POST   | /auth/register        | Registrazione nuovo utente            |
| POST   | /auth/login           | Login utente                          |
| GET    | /users/me             | Profilo dell'utente autenticato       |
| PUT    | /users/me/preferences | Aggiorna preferenze di viaggio utente |

---

### 6.2 Generazione Itinerario

| Metodo | Endpoint            | Descrizione                                                  |
| ------ | ------------------- | ------------------------------------------------------------ |
| POST   | /generate-itinerary | Genera un itinerario AI-driven per una destinazione e durata |
| GET    | /itineraries/{id}   | Recupera un itinerario specifico                             |
| GET    | /itineraries/user   | Recupera tutti gli itinerari dell’utente                     |

---

### 6.3 Modulo Prezzi e Prenotazioni

| Metodo | Endpoint                    | Descrizione                                  |
| ------ | --------------------------- | -------------------------------------------- |
| POST   | /pricing/estimate           | Stima costo attività, musei, trasporti, etc. |
| GET    | /pricing/history/{location} | Storico prezzi attrazioni e trasporti        |

---

### 6.4 Modulo Eventi e Nightlife

| Metodo | Endpoint                | Descrizione                                                  |
| ------ | ----------------------- | ------------------------------------------------------------ |
| GET    | /events/{city}          | Recupera eventi in corso filtrati per data, categoria, gusti |
| GET    | /events/recommendations | Suggerisce eventi in base a profilo utente                   |

---

### 6.5 Mobilità e Alloggi

| Metodo | Endpoint              | Descrizione                                        |
| ------ | --------------------- | -------------------------------------------------- |
| GET    | /mobility/options     | Tariffe e disponibilità car/bike/scooter sharing   |
| GET    | /accommodation/advice | Zone consigliate per alloggio in base a preferenze |
| POST   | /home-exchange/match  | Matching per scambio casa                          |

---

### 6.6 Gamification e Notifiche

| Metodo | Endpoint           | Descrizione                                       |
| ------ | ------------------ | ------------------------------------------------- |
| GET    | /leaderboard       | Classifica utenti per badge, punteggio e attività |
| GET    | /alerts/{user\_id} | Notifiche smart su offerte, eventi, cambi prezzi  |

---

### 6.7 Immagini e Contenuti

| Metodo | Endpoint              | Descrizione                                |
| ------ | --------------------- | ------------------------------------------ |
| GET    | /images/search        | Cerca immagini per destinazione/tema       |
| GET    | /content/links/{type} | Link utili per prenotazione e informazioni |

---

## 7. Descrizione Funzionale Agenti Intelligenti e Automazioni

Sono stati anche definiti alcuni agenti e automazioni da creare.
Bisogna capire quali sono necessari in relazione alle user stories, poi come implementarli. 

### 7.1 Itinerary Auto-Builder Agent

* **Input**: destinazione, durata, stagione, preferenze
* **Tecnologia**: GPT-4o (o mini) + pipeline NLP custom
* **Output**: schema itinerario giornaliero, con link ufficiali e timeframe
* **Funzioni**:

  * Generazione schema base
  * Traduzione e localizzazione contenuti
  * Inclusione tappe AI-ranked

### 7.2 Tourism Data Integrator (RPA Agent)

* **Input**: città
* **Tecnologia**: Puppeteer + OCR + cron scheduler
* **Output**: dataset attrazioni, musei, orari, prezzi aggiornati
* **Funzioni**:

  * Scraping portali ufficiali (Visit City, Nostracultura)
  * Parsing HTML, PDF e contenuti dinamici
  * Normalizzazione dati e validazione

### 7.3 Ticket Price Estimator Agent

* **Input**: elenco attività/attrazioni, date
* **Tecnologia**: RPA scraping + regressione costi
* **Output**: tabella prezzi e stima costo viaggio
* **Funzioni**:

  * Raccolta prezzi da siti ufficiali o piattaforme prenotazione
  * Stima costi mancanti tramite modello AI (MAPE ≤ 12%)

### 7.4 Events & Nightlife Agent

* **Input**: città, data, interessi utente
* **Tecnologia**: scraping + embedding + filtro AI
* **Output**: eventi rilevanti con info e link
* **Funzioni**:

  * Parsing di Eventbrite, Meetup, siti locali
  * Raccomandazione semantica eventi simili

### 7.5 Mobility Aggregator Agent

* **Input**: città, data
* **Tecnologia**: API calls + scraping
* **Output**: tabella con tariffe car/bike/scooter sharing
* **Funzioni**:

  * Comparazione multi-provider (ShareNow, Lime, ecc.)
  * Previsione disponibilità per fascia oraria

### 7.6 Home Exchange Matcher Agent

* **Input**: profilo host e viaggiatore
* **Tecnologia**: Similarity Matching (embeddings + filtri logici)
* **Output**: coppie compatibili per scambio
* **Funzioni**:

  * Matching preferenze / date / tipo alloggio
  * Classificazione qualità match (score > soglia)

### 7.7 Smart Notification Engine

* **Input**: profilo utente, itinerario salvato, dati prezzo/eventi
* **Tecnologia**: Rule-based + AI thresholding
* **Output**: alert push/email su variazioni rilevanti
* **Funzioni**:

  * Trigger su soglie prezzo
  * Notifiche eventi imminenti o nuovi

### 7.8 TravelGPT Chat Agent

* **Input**: domanda generica o contestuale
* **Tecnologia**: GPT-4o + RAG (opzionale con Vector DB)
* **Output**: risposte precise su viaggio, attività, cultura locale
* **Funzioni**:

  * Risposte grounding su contenuti reali
  * Integrazione con knowledge base da scraping/API
