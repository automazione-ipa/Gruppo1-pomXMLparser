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
