**README**

# AI-Powered Maven Dependency Agent

Un MVP Python per l’analisi e l’esplorazione delle dipendenze Maven di un progetto tramite GPT e graph analytics.

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

**Buon lavoro!**
