"""GPT functions module."""
dct_fn_read_file = {
    "name": "read_file",
    "description": "Legge il contenuto di un file.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Percorso del file da leggere."}
        },
        "required": ["path"]
    }
}

dct_fn_write_file = {
    "name": "write_file",
    "description": "Scrive contenuto su file.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Percorso di destinazione."},
            "content": {"type": "string", "description": "Contenuto da scrivere nel file."}
        },
        "required": ["path", "content"]
    }
}

dct_fn_parse_pom = {
    "name": "parse_pom_file",
    "description": "Legge un pom.xml, estrae informazioni e restituisce una struttura JSON.",
    "parameters": {
        "type": "object",
        "properties": {
            "pom_path": {
                "type": "string",
                "description": "Percorso al file pom.xml"
            }
        },
        "required": ["pom_path"]
    }
}

dct_fn_load_json = {
    "name": "load_json",
    "description": "Carica un file JSON da disco e restituisce la struttura.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Percorso al file JSON"
            }
        },
        "required": ["path"]
    }
}

FUNCTIONS = [
    dct_fn_read_file,
    dct_fn_write_file,
    dct_fn_parse_pom,
    dct_fn_load_json
]
