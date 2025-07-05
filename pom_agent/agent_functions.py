"""Agent functions wrapper module."""
import json
from pom_agent.pomxml_extractor import parse_pom


def parse_pom_file(pom_path):
    """Parse pom.xml and return project and dependencies info."""
    result = parse_pom(pom_path)
    return result


def load_json(path):
    """Load a JSON file and return its content."""
    with open(path, "r") as f:
        return json.load(f)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"path": path, "status": "success"}
