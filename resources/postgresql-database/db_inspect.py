"""
Script di ispezione del database travel_db usando psycopg2.
Richiama init_db() per assicurarsi che le tabelle (come definite in SQLAlchemy)
esistano, quindi raccoglie informazioni dal database reale per diagnostica.
"""

import os
import sys
import json
from typing import List, Dict, Any

import psycopg2
import psycopg2.extras

# Import della init_db e settings esistenti
from src.resources.db.base import init_db
from src.resources.config.settings import DATABASE_URL
from src.resources.db import models as db_models  # i modelli SQLAlchemy definiti

# ---------- Helper per DSN compatibile psycopg2 ----------
def make_psycopg2_dsn(sqlalchemy_url: str) -> str:
    """
    Trasforma un URL di SQLAlchemy come
    'postgresql+psycopg2://user:pwd@host:port/db' in qualcosa
    che psycopg2.connect accetta, cioè 'postgresql://user:pwd@host:port/db'
    """
    if sqlalchemy_url.startswith("postgresql+psycopg2://"):
        return sqlalchemy_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    # già compatibile?
    return sqlalchemy_url

# ---------- Query utili ----------
TABLES_QUERY = """
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
"""

COLUMNS_QUERY = """
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
ORDER BY ordinal_position;
"""

ROWCOUNT_QUERY = "SELECT COUNT(*) FROM {};"  # format(table)
TABLE_SIZE_QUERY = """
SELECT
    pg_size_pretty(pg_total_relation_size(%s)) AS total_size,
    pg_size_pretty(pg_relation_size(%s)) AS table_size,
    pg_size_pretty(pg_total_relation_size(%s) - pg_relation_size(%s)) AS index_size;
"""


INDEXES_QUERY = """
SELECT
  indexname,
  indexdef
FROM pg_indexes
WHERE schemaname = %s AND tablename = %s
ORDER BY indexname;
"""

FK_QUERY = """
SELECT
  tc.constraint_name,
  kcu.column_name,
  ccu.table_schema AS foreign_table_schema,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM
  information_schema.table_constraints AS tc
  JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
       AND tc.table_schema = kcu.table_schema
  JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = %s
  AND tc.table_name = %s;
"""

# ---------- Funzioni di ispezione ----------
def list_tables(conn) -> List[Dict[str,str]]:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(TABLES_QUERY)
        rows = cur.fetchall()
    return [{"schema": r["table_schema"], "table": r["table_name"]} for r in rows]

def describe_table(conn, schema: str, table: str) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(COLUMNS_QUERY, (schema, table))
        return [dict(r) for r in cur.fetchall()]

def row_count(conn, schema: str, table: str) -> int:
    q = ROWCOUNT_QUERY.format(f'"{schema}"."{table}"')
    with conn.cursor() as cur:
        cur.execute(q)
        return cur.fetchone()[0]

def table_size(conn, schema: str, table: str) -> Dict[str, str]:
    fq = f'"{schema}"."{table}"'  # fully-qualified table name con doppi apici
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(TABLE_SIZE_QUERY, (fq, fq, fq, fq))
        r = cur.fetchone()
        if r:
            return dict(r)
        return {"total_size": "N/A", "table_size": "N/A", "index_size": "N/A"}

def list_indexes(conn, schema: str, table: str) -> List[Dict[str,str]]:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(INDEXES_QUERY, (schema, table))
        return [dict(r) for r in cur.fetchall()]

def list_foreign_keys(conn, schema: str, table: str) -> List[Dict[str,str]]:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(FK_QUERY, (schema, table))
        return [dict(r) for r in cur.fetchall()]

# ---------- Confronto con modelli SQLAlchemy ----------
def sqlalchemy_model_columns() -> Dict[str, List[str]]:
    """
    Ritorna mapping table_name -> [columns] basandosi sui modelli SQLAlchemy importati
    (usa db_models)
    """
    mapping = {}
    # Scorri gli attributi del modulo models e prendi le classi che hanno __table__
    for attr in dir(db_models):
        cls = getattr(db_models, attr)
        # semplice check: oggetto ORM con attributo __table__ (classi dei modelli)
        if hasattr(cls, "__table__"):
            tbl = cls.__table__.name
            cols = [c.name for c in cls.__table__.columns]
            mapping[tbl] = cols
    return mapping

def compare_db_and_models(conn):
    """
    Confronta colonne viste dal DB con quelle definite nei modelli.
    Stampa discrepanze.
    """
    models_map = sqlalchemy_model_columns()
    problems = []

    tables = list_tables(conn)
    # crea mappa per facilità
    db_tables = {f"{t['schema']}.{t['table']}": t for t in tables}

    for full_table, cols in models_map.items():
        # assumiamo schema public per i modelli
        schema = "public"
        table = full_table
        # verifica esistenza tabella
        if {"schema": schema, "table": table} not in tables:
            problems.append(f"Tabella mancante nel DB: {schema}.{table}")
            continue

        db_cols = describe_table(conn, schema, table)
        db_col_names = [c["column_name"] for c in db_cols]

        missing_in_db = set(cols) - set(db_col_names)
        extra_in_db = set(db_col_names) - set(cols)

        if missing_in_db or extra_in_db:
            problems.append({
                "table": f"{schema}.{table}",
                "missing_in_db": sorted(list(missing_in_db)),
                "extra_in_db": sorted(list(extra_in_db)),
            })

    return problems

# ---------- Main ----------
def main():
    print("Avvio init_db() (crea tabelle mancanti secondo SQLAlchemy)...")
    init_db()
    print("init_db() completata.\n")

    dsn = make_psycopg2_dsn(DATABASE_URL)
    print(f"Connessione a: {dsn}\n")

    conn = None
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
    except Exception as e:
        print("Errore di connessione al DB:", e)
        sys.exit(1)

    try:
        print("Elenco tabelle (schema.table):")
        tables = list_tables(conn)
        for t in tables:
            print(f" - {t['schema']}.{t['table']}")
        print()

        # Per ogni tabella nel DB, raccogli dettagli essenziali
        print("Dettagli tabelle principali (description, rowcount, size, indexes, fks):\n")
        for t in tables:
            schema = t["schema"]
            table = t["table"]
            print(f"--- {schema}.{table} ---")
            cols = describe_table(conn, schema, table)
            print("Colonne:")
            for c in cols:
                print(f"  - {c['column_name']} ({c['data_type']}) nullable={c['is_nullable']} default={c['column_default']}")
            try:
                rc = row_count(conn, schema, table)
            except Exception as e:
                rc = f"Errore: {e}"
            print(f"Row count: {rc}")
            size = table_size(conn, schema, table)
            print(f"Sizes: {json.dumps(size)}")
            idxs = list_indexes(conn, schema, table)
            if idxs:
                print("Indici:")
                for i in idxs:
                    print(f"  - {i['indexname']}: {i['indexdef']}")
            fks = list_foreign_keys(conn, schema, table)
            if fks:
                print("Foreign keys:")
                for fk in fks:
                    print(f"  - {fk['constraint_name']}: {fk['column_name']} -> {fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}")
            print()

        # Confronta con modelli SQLAlchemy
        print("Confronto colonne DB vs modelli SQLAlchemy:")
        problems = compare_db_and_models(conn)
        if not problems:
            print("Nessuna discrepanza trovata. Modelli e DB coerenti.")
        else:
            print("Discrepanze rilevate:")
            for p in problems:
                print(" -", p)
    finally:
        if conn:
            conn.close()
            print("\nConnessione chiusa.")

if __name__ == "__main__":
    main()
