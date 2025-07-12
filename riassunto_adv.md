# Requisiti di Automazione

1. INTEGRAZIONE VIAGGI/MEZZI/PREZZI
-> scraping/API

2. CHATBOT (per costruire l'itinerario)
-> RAG Ingestion / Generation

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
