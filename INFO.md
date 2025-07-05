## MVP: Knowledge Graph Ingestion from Polito Cryptography Course Notes

**Obiettivo**: creare un prototipo Python (MVP) che:

1. Estrae e normalizza i contenuti dal sito di Polito (Cryptography course)
2. Analizza il testo e struttura informazioni in un Knowledge Graph (KG)
3. Rende navigabili concetti e relazioni via query Python
4. (Futuro) integra logica AI per arricchire e validare il grafo

---

* IPA che prende e controlla a tappeto, fa analisi, ...
* Faccio fare valutazioni al modello
* Faccio predirre soluzioni al modello -> potresti fare X, Y, Z
* Grafo delle dipendenze

* Dependency Check? Function call lo può aggiungere in automatico.
* Sonar Lint?
* ...

### 1. Data Ingestion

* **Sorgente**: ``
* **Tecnologia**: `requests` + `BeautifulSoup` per scraping
* **Output**: file JSON per ogni sezione, con:

  * `id`: slug
  * `title`: titolo sezione
  * `content`: HTML raw
  * `text`: testo pulito

```python
import requests
from bs4 import BeautifulSoup

URL = "https://quantum-engineering-polito.github.io/CourseNotes/Cyber-Security/02_Cryptography/Cryptography"

resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Esempio: tutte le sezioni <h2>
sections = []
for header in soup.select("h2"):    
    id = header.get_text(strip=True).lower().replace(" ", "-")
    section = {"id": id, "title": header.get_text(), "content": ""}
    # raccogli paragrafi fino al prossimo <h2>
    for sib in header.find_next_siblings():
        if sib.name == "h2": break
        section["content"] += str(sib)
    sections.append(section)

# Salva JSON
import json
with open("sections.json", "w") as f:
    json.dump(sections, f, indent=2)
```

---

### 2. Parsing & Text Extraction

* Usa `BeautifulSoup` o `lxml` per estrarre testo puro, paragrafi, liste e code snippet
* Salva in strutture Python:

  ```python
  {
    "id": "symmetric-encryption",
    "title": "Symmetric encryption",
    "paragraphs": ["Symmetric cryptography...", ...],
    "lists": {"ul": [...], "ol": [...]},
    "code": ["C = enc(K, P)", ...]
  }
  ```

---

### 3. Knowledge Graph Schema & Design

**Entità principali**:

1. **Concept**: termini o vocaboli chiave, es. "Symmetric encryption", "XOR", "Kerchoffs' principle"

   * Attributi: `name`, `type` (e.g. Principle, Term)
2. **Algorithm**: descrive una procedura, es. "DES", "3DES", "AES"

   * Attributi: `name`, `key_length`, `block_size`, `mode` (when fixed)
3. **ModeOfOperation**: modalità di cifratura a blocchi, es. "ECB", "CBC", "CTR"

   * Attributi: `name`, `requires_iv` (bool)
4. **Attack**: tipologie di attacco, es. "Brute Force", "Meet-in-the-Middle"

   * Attributi: `name`, `complexity`
5. **Parameter**: parametri tecnici, es. `KeyBitLength`, `BlockSize`, `PaddingScheme`

   * Attributi: `name`, `value`
6. **Definition**: descrizioni o testo esplicativo

   * Attributi: `text`

**Relazioni chiave**:

* `DEFINES` (Concept → Definition)

  * es. `(Concept: "Symmetric encryption")-[:DEFINES]->(Definition)`
* `USES` (Algorithm → Concept)

  * es. `(Algorithm: "DES")-[:USES]->(Concept: "XOR")`
* `DERIVES_FROM` (Algorithm → Algorithm)

  * es. `(Algorithm: "3DES")-[:DERIVES_FROM]->(Algorithm: "DES")`
* `HAS_MODE` (Algorithm → ModeOfOperation)

  * es. `(Algorithm: "DES")-[:HAS_MODE]->(ModeOfOperation: "ECB")`
* `HAS_PARAMETER` (Algorithm/ModeOfOperation → Parameter)

  * es. `(ModeOfOperation: "CBC")-[:HAS_PARAMETER]->(Parameter: "IV")`
* `VULNERABLE_TO` (Algorithm/ModeOfOperation → Attack)

  * es. `(Algorithm: "2DES")-[:VULNERABLE_TO]->(Attack: "Meet-in-the-Middle")`
* `NEXT` (Concept/Section → Concept/Section)

  * per sequenze di appunti, es. flusso didattico

**Esempio di frammento di grafo**:

```
(:Algorithm {name: "DES", key_length: 56, block_size: 64})
  -[:USES]->(:Concept {name: "XOR"})
  -[:HAS_MODE]->(:ModeOfOperation {name: "ECB", requires_iv: false})
(:Algorithm {name: "3DES"})
  -[:DERIVES_FROM]->(:Algorithm {name: "DES"})
  -[:VULNERABLE_TO]->(:Attack {name: "Meet-in-the-Middle", complexity: "2^56"})
```

---

### 4. Implementazione Graph

* **Graph DB**: `NetworkX` per prototipo, `Neo4j` per casi di scala

```python
import networkx as nx

g = nx.DiGraph()
# Nodi
entities = [
    ("Symmetric encryption", {"type":"Concept"}),
    ("DES", {"type":"Algorithm", "key_length":56, "block_size":64}),
    ("XOR", {"type":"Concept"}),
    ("ECB", {"type":"ModeOfOperation", "requires_iv":False}),
]
for node, attrs in entities:
    g.add_node(node, **attrs)
# Relazioni
g.add_edge("DES", "XOR", rel="USES")
g.add_edge("DES", "ECB", rel="HAS_MODE")
```

---

### 5. Navigazione e Query

* Esempi di interrogazioni:

  * **Trova algoritmi che usano XOR**

    ```python
    [n for n in g.nodes if g.nodes[n]["type"]=="Algorithm" and any(e[2]["rel"]=="USES" and e[1]=="XOR" for e in g.out_edges(n, data=True))]
    ```
  * **Elenca parametri di CBC**

    ```python
    [nbr for nbr in g.successors("CBC") if g["CBC"][nbr]["rel"]=="HAS_PARAMETER"]
    ```

---

### 6. Estensioni Future

1. Embedding di concept per similarità semantica
2. Automazione detection di incongruenze tra definizioni
3. UI web (Streamlit, Dash) per esplorazione grafica
4. Batch job periodico per sincronizzazione e validazione

---

### 7. Requisiti e Configurazione

Per avviare il prototipo, creiamo i file:

#### 7.1 requirements.txt

```text
# HTTP & Parsing
requests>=2.25.1
beautifulsoup4>=4.9.3
lxml>=4.6.2

# Data manipulation
pandas>=1.2.0
networkx>=2.5

# (Opzionali) per storage e .env
python-dotenv>=0.15.0
PyYAML>=5.4.1

# (Futuro) per Neo4j
neo4j>=4.3.1
```

#### 7.2 config.yaml

```yaml
# URL di origine dei notes
source:
  url: "https://quantum-engineering-polito.github.io/CourseNotes/Cyber-Security/02_Cryptography/Cryptography"

database:
  # per SQLite locale
  type: "sqlite"
  path: "./data/graph.db"
  # per Neo4j (se utilizzato)
  neo4j_uri: "bolt://localhost:7687"
  neo4j_user: "neo4j"
  neo4j_password: "password"

scraping:
  headers:
    User-Agent: "Mozilla/5.0 (compatible; ProtfolioBot/1.0)"

graph:
  use_neo4j: false
  batch_size: 1000
```

#### 7.3 .env

```ini
# Se usi python-dotenv
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secret
```

#### 7.4 Struttura di progetto consigliata

```
project_root/
├── data/                # file JSON e database SQLite
├── src/                 # codice sorgente Python
│   ├── ingestion.py     # scraping e JSON output
│   ├── parser.py        # estrazione testo, paragrafi, liste, code
│   ├── graph.py         # costruzione e query NetworkX/Neo4j
│   ├── database.py      # interfaccia SQLite/Neo4j per salvataggio
│   ├── config.py        # caricamento config.yaml e .env
│   └── main.py          # orchestratore dei moduli
├── requirements.txt
├── config.yaml
└── .env
```

#### 7.5 Template dei file Python

**src/config.py**

```python
"""
Carica parametri da config.yaml e variabili .env
"""
import os
import yaml
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self, path: str):
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
        self.source_url = cfg['source']['url']
        self.db_type = cfg['database']['type']
        self.db_path = cfg['database']['path']
        self.neo4j_cfg = cfg['database']
        self.headers = cfg['scraping']['headers']
        self.use_neo4j = cfg['graph']['use_neo4j']
        self.batch_size = cfg['graph']['batch_size']
        # .env overrides
        self.neo4j_user = os.getenv('NEO4J_USER')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')


settings = Settings(os.getenv('CONFIG_PATH', 'config.yaml'))
```

**src/ingestion.py**

```python
"""
Esegue lo scraping del sito e salva sezioni in JSON
"""
import json
import requests
from bs4 import BeautifulSoup
from src.config import settings


def fetch_sections() -> list:
    resp = requests.get(settings.source_url, headers=settings.headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    sections = []
    for header in soup.select('h2'):
        sid = header.get_text(strip=True).lower().replace(' ', '-')
        content = ''
        for sib in header.find_next_siblings():
            if sib.name == 'h2': break
            content += str(sib)
        sections.append({'id': sid, 'title': header.get_text(), 'content': content})
    return sections


if __name__ == '__main__':
    secs = fetch_sections()
    with open('data/sections.json', 'w') as f:
        json.dump(secs, f, indent=2)
```

**src/parser.py**

```python
"""
Estrae testo pulito, paragrafi, liste e code dai JSON di sezione
"""
import json
from bs4 import BeautifulSoup

def parse_section(section: dict) -> dict:
    soup = BeautifulSoup(section['content'], 'lxml')
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    lists = {
        'ul': [li.get_text(strip=True) for ul in soup.find_all('ul') for li in ul.find_all('li')],
        'ol': [li.get_text(strip=True) for ol in soup.find_all('ol') for li in ol.find_all('li')]
    }
    code = [code.get_text(strip=True) for code in soup.find_all('code')]
    return {
        'id': section['id'],
        'title': section['title'],
        'paragraphs': paragraphs,
        'lists': lists,
        'code': code
    }

if __name__ == '__main__':
    with open('data/sections.json') as f:
        secs = json.load(f)
    parsed = [parse_section(s) for s in secs]
    with open('data/sections_parsed.json', 'w') as f:
        json.dump(parsed, f, indent=2)
```

**src/database.py**

```python
"""
Interfaccia per salvataggio dei paragrafi su SQLite
"""
import sqlite3
from src.config import settings


def init_db():
    conn = sqlite3.connect(settings.db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id TEXT,
            paragraph_index INTEGER,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_paragraphs(parsed_sections: list):
    conn = sqlite3.connect(settings.db_path)
    c = conn.cursor()
    for sec in parsed_sections:
        for i, text in enumerate(sec['paragraphs']):
            c.execute(
                'INSERT INTO paragraphs (section_id, paragraph_index, content) VALUES (?, ?, ?)',
                (sec['id'], i, text)
            )
    conn.commit()
    conn.close()
```

**src/graph.py**

```python
"""
Costruisce e interroga il Knowledge Graph con NetworkX o Neo4j
"""
import networkx as nx
from src.config import settings


def build_graph(parsed_sections: list):
    g = nx.DiGraph()
    # esempio: aggiungi nodi e relazioni
    # TODO: implementare mapping entità-relazioni
    return g


if __name__ == '__main__':
    # caricamento e test
    pass
```

**src/main.py**

```python
"""
Orchestra l’esecuzione di ingestion, parsing, salvataggio e grafo
"""
import json
from src.ingestion import fetch_sections
from src.parser import parse_section
from src.database import init_db, save_paragraphs
from src.graph import build_graph


def main():
    print('Scraping...')
    sections = fetch_sections()

    print('Parsing...')
    parsed = [parse_section(s) for s in sections]

    print('Inizializza DB...')
    init_db()

    print('Salva paragrafi...')
    save_paragraphs(parsed)

    print('Costruisci grafo...')
    g = build_graph(parsed)
    print('Nodi nel grafo:', len(g.nodes))


if __name__ == '__main__':
    main()
```
