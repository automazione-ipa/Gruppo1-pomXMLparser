"""
Orchestra l’esecuzione di ingestion, parsing, salvataggio e grafo
"""
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