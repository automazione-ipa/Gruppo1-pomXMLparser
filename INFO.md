# **PoC TravelForge – Progetto "TravelForge Spark"**

**Obiettivo**: In 7 settimane realizzare una piattaforma di travel tech che fornisca un’esperienza fluida e personalizzata: l’utente indica meta e durata (es. Berlino, 5 giorni) e ottiene un pacchetto completo di informazioni e strumenti AI-driven.

---

## Elenco sintetico delle Features

* Tourism Data Integrator
* Itinerary Auto-Builder
* Ticket Price Estimator
* Events & Nightlife Module
* Car Sharing & Mobility
* Accommodation Advisor
* Home Exchange Matcher
* Travel Leaderboard
* Smart Alerts & Links
* Interactive Demo UI

## 1. Ambito e Funzionalità

| Feature                       | Descrizione                                                                                                                                          | Valore Creativo                         |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| **Tourism Data Integrator**   | Bot RPA per scraping di dati ufficiali (siti city portal, nostracultura.it) su musei, orari, prezzi, eventi in corso; normalizzazione e update       | Dati affidabili e sempre aggiornati     |
| **Itinerary Auto-Builder**    | Microservizio AI che genera itinerari personalizzati: durata, preferenze, budget. Includere mappe, foto, link di riferimento e timeframe giornalieri | Itinerario dettagliato e pronto all’uso |
| **Ticket Price Estimator**    | Modulo AI/RPA per estrazione prezzi biglietti (musei, attrazioni) e stima costo totale, corretta in real-time                                        | Preventivo realistico e dinamico        |
| **Events & Nightlife Module** | Servizio AI che recupera eventi (concerti, mostre) e luoghi serali (bar, discoteche) con filtri per data e gusti utente                              | Esperienze di viaggio personalizzate    |
| **Car Sharing & Mobility**    | RPA per aggregare tariffe car sharing, bike/e-scooter sharing e rental car; visualizzazione costi e disponibilità                                    | Mobilità integrata e confrontabile      |
| **Accommodation Advisor**     | AI-driven consigli su zone migliori per alloggio (musei vs nightlife), periodo migliore per viaggiare, portali di prenotazione                       | Scelta più adatta a esigenze e budget   |
| **Home Exchange Matcher**     | Matching AI tra host e viaggiatori per scambio case ottimale: preferenze, date, zona                                                                 | Aumento delle opportunità di scambio    |
| **Travel Leaderboard**        | Dashboard gamificata con badge ("Explorer Pro", "Local Host"), punti basati su utilizzo moduli e feedback                                            | Engagement, retention e viralità        |
| **Smart Alerts & Links**      | Notifiche push su offerte lampo, variazioni prezzo, eventi imminenti, con link diretti ai siti di prenotazione e alle mappe interattive              | Proattività e click-through immediato   |
| **Interactive Demo UI**       | Frontend Angular + Tailwind con interfaccia fluida: input meta/tempo, mappe dinamiche, drag\&drop per custom itinerari e preview “immersive”         | Esperienza utente premium e intuitiva   |

## 2. Architettura PoC

1. **Backend**: FastAPI + Python (scikit-learn, Pandas, Hugging Face Transformers)
2. **Data Store**: PostgreSQL (utenti, itinerari, case, eventi) + Redis (cache offerte, previsioni)
3. **AI Service**:

   * Itinerary generation (seq2seq + GPT fallback)
   * Recommendation (matching preferences)
   * Regression per stima costi
   * NLP per eventi, nightlife e recensioni
4. **RPA Module**: Containerizzati (Puppeteer + OCR) per scraping:

   * Tourism portals (Visit Berlin, City APIs)
   * Event calendars (Eventbrite, Meetup)
   * Car sharing APIs (ShareNow, Lime)
5. **Frontend**: Angular + Tailwind (Itinerary Builder, Event Explorer, Mobility Dashboard, Leaderboard)
6. **Orchestrazione**: Kubernetes (API, AI, RPA agent, Redis)
7. **CI/CD**: GitHub Actions (build, lint, test, deploy su dev e staging)
8. **Monitoring**: Prometheus & Grafana (metriche API e RPA)

## 3. Functional Prototype: Backend Itinerary Service

**Obiettivo**: Implementare in Python un endpoint FastAPI che, dati in input `city_country`, `duration_days`, `season_or_dates`, restituisca:

1. **Galleria Immagini**: Le foto più significative (attrazioni, spiagge, architettura), ottenute tramite API di image search (es. Unsplash o Google Custom Search).
2. **Report Itinerario Markdown**:

   * Itinerario giorno-per-giorno con link ufficiali (siti musei, tour operator, city portal).
   * Preventivo costi: tabella con dettaglio prezzi (biglietti musei, attività, trasporti) e totale.
   * Link diretti ai provider per prenotazione (biglietti, hotel, car sharing).
3. **Meccanismo di Function Calling**:

   * Chiamata a GPT tramite l’API OpenAI con `functions` per:

     * Generare schema itinerario base.
     * Estrarre keyword per ricerca immagini e prezzi.
   * Pipeline custom in Python per:

     * Eseguire scraping o chiamate API a siti ufficiali.
     * Validare e normalizzare i prezzi (evitando dati errati o inventati).

### 3.1 Input e Output

* **Input JSON**:

```json
{
  "city_country": "Las Americas, Tenerife",
  "duration_days": 10,
  "season_or_dates": {"season": "estate", "from": "2025-08-10", "to": "2025-08-20"}
}
```

* **Output Markdown**:

```markdown
# Itinerario per Las Americas, Tenerife (10 giorni, 10-20 agosto 2025)

## 📸 Galleria Immagini
![Spiaggia](link1)
![Mount Teide](link2)
...

## 🗓️ Itinerario Giornaliero
| Giorno | Attività                        | Link                                                |
| ------ | ------------------------------- | --------------------------------------------------- |
| 1      | Escursione al Mount Teide       | https://www.volcanoteide.com                        |
| 2      | Visita Loro Parque              | https://www.loroparque.com/tickets                   |
...

## 💰 Preventivo Costi
| Voce                  | Prezzo (€) |
| --------------------- | ---------- |
| Mount Teide           | 25         |
| Loro Parque           | 35         |
| Car sharing (giornaliero) | 40      |
| **Totale Stimato**    | **1000**   |

## 🔗 Link Prenotazione
- Biglietti Mount Teide: https://www.volcanoteide.com
- Car sharing: https://www.sharenow.com
```

### 3.2 Architettura e Pipeline

1. **Endpoint FastAPI** `/generate-itinerary`
2. **Service Layer**:

   * `gpt_client.call_functions()` per struttura base itinerario
   * `image_service.search_images(keywords)`
   * `pricing_service.fetch_prices(items, dates)`
   * `markdown_builder.build_report(data)`
3. **Data Validation**: Controlli su prezzi e link (schema JSON + regex sui domini ufficiali).
4. **Caching**: Redis per risposte di image search e price fetch per 1h.

---

4. Timeline & Deliverables (7 settimane)

\| Settimana | Attività                                                                                                                                       | Deliverable                              |

1. **Backend**: FastAPI + Python (scikit-learn, Pandas, Hugging Face Transformers)
2. **Data Store**: PostgreSQL (utenti, itinerari, case, eventi) + Redis (cache offerte, previsioni)
3. **AI Service**:

   * Itinerary generation (seq2seq + GPT fallback)
   * Recommendation (matching preferences)
   * Regression per stima costi
   * NLP per eventi, nightlife e recensioni
4. **RPA Module**: Containerizzati (Puppeteer + OCR) per scraping:

   * Tourism portals (Visit Berlin, City APIs)
   * Event calendars (Eventbrite, Meetup)
   * Car sharing APIs (ShareNow, Lime)
5. **Frontend**: Angular + Tailwind (Itinerary Builder, Event Explorer, Mobility Dashboard, Leaderboard)
6. **Orchestrazione**: Kubernetes (API, AI, RPA agent, Redis)
7. **CI/CD**: GitHub Actions (build, lint, test, deploy su dev e staging)
8. **Monitoring**: Prometheus & Grafana (metriche API e RPA)

## 3. Timeline & Deliverables (7 settimane)

| Settimana | Attività                                                                                                                                    | Deliverable                            |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 1         | Ambiente, schema DB (utenti, destinazioni, itinerari, eventi, case), stub API RPA/AI, autenticazione base                                   | Repo iniziale, DB schema, auth stub    |
| 2         | **Tourism Data Integrator**: bot scraping musei, attrazioni, orari, prezzi; API per dati culturali                                          | Servizio scraping + esempi dataset     |
| 3         | **Itinerary Auto-Builder**: modello NLP + GPT fallback, generazione itinerari base; integrazione mappe e foto via API esterna               | Microservizio itinerari, endpoint demo |
| 4         | **Ticket Price Estimator**: RPA extraction prezzi biglietti + regressione costi totali; integrazione link ufficiali                         | API stima costi + test accuracy        |
| 5         | **Events & Nightlife Module**: scraping eventi in corso, raccomandazioni locali, AI filter per gusti; sviluppo UI lista eventi              | Servizio eventi + UI prototipo         |
| 6         | **Car Sharing & Accommodation Advisor**: RPA price aggregator car sharing; AI consigli zone e periodi; Home Exchange Matcher                | Mobility dashboard + matching service  |
| 7         | **Gamification Engine** + **Interactive Demo UI**: leaderboard, notifiche, link diretti, test end-to-end, documentazione, presentazione PoC | UI completa, report PoC, demo live     |

## 4. Metriche di Successo

* **Fluidità UX**: <2 click per ottenere itinerario completo
* **Accuratezza dati culturali** ≥ 95%
* **Soddisfazione Itinerario** ≥ 85%
* **Precisione stima prezzo** MAPE ≤ 12%
* **Matching Accuracy** ≥ 75%
* **Engagement Gamification** ≥ 60% utenti attivi
* **Tempo totale elaborazione** < 15s per richiesta

---

*TravelForge Spark* offre una user journey senza interruzioni: dall’input di meta e giorni a un’esperienza ricca di contenuti, link ufficiali, mappe e consigli su misura, sfruttando RPA, AI e un’interfaccia immersiva.
