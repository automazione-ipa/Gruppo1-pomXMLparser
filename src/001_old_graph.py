from enum import Enum

import networkx as nx


# Types
class InformationType(str, Enum):
    ALGORITHM   = "Algorithm"
    CONCEPT     = "Concept"


g = nx.DiGraph()


# Nodi
tp_symm_encryption = ("Symmetric encryption", {"type": "Concept"})
tp_DES = ("DES", {"type": "Algorithm", "key_length": 56, "block_size": 64})
tp_XOR = ("XOR", {"type": "Concept"})
tp_ECB = ("ECB", {"type": "ModeOfOperation", "requires_iv": False})


entities = [tp_symm_encryption ,tp_DES, tp_XOR, tp_ECB]
for node, attrs in entities:
    g.add_node(node, **attrs)
# Relazioni
g.add_edge("DES", "XOR", rel="USES")
g.add_edge("DES", "ECB", rel="HAS_MODE")


# Esempio di interrogazioni

# Trova algoritmi che usano XOR
lst_research_1 = [
    n for n in g.nodes if g.nodes[n]["type"]=="Algorithm" and any(e[2]["rel"] == "USES" and e[1] == "XOR" for e in g.out_edges(n, data=True))
]

# Elenca parametri di CBC

lst_CBC_params = [
    nbr for nbr in g.successors("CBC") if g["CBC"][nbr]["rel"] == "HAS_PARAMETER"
]

#
# async def main_v2():
#     """Flusso principale."""
#     deps = extract_dependencies()
#     queries = build_queries(deps)
#     alerts = await search_with_playwright(queries)
#     write_alerts(alerts)
#     send_email()
