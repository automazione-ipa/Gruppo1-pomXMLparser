"""
Interfaccia per salvataggio dei paragrafi su SQLite
"""
import sqlite3
from data.config import settings


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
    sql_query = 'INSERT INTO paragraphs (section_id, paragraph_index, content) VALUES (?, ?, ?)'
    for sec in parsed_sections:
        for i, text in enumerate(sec['paragraphs']):
            c.execute(
                sql_query,
                (sec['id'], i, text)
            )
    conn.commit()
    conn.close()
