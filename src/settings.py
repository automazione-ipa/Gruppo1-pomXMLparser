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


settings = Settings(os.getenv('CONFIG_PATH', '../config.yaml'))
