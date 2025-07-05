"""Main module"""

import logging
from pom_agent.pomxml_extractor import parse_pom
from pom_agent.config import POM_FILE, write_pom_json

logger = logging.getLogger(__name__)


def main():
    try:
        data = parse_pom(pom_path=POM_FILE)
    except RuntimeError as e:
        logger.error(f"❌ Errore: {e}")
        return

    _, json_path = write_pom_json(data)

    proj = data['project']
    logger.info("📦 Informazioni sul progetto:")
    logger.info(f"  - groupId:    {proj.get('groupId')}")
    logger.info(f"  - artifactId: {proj.get('artifactId')}")
    logger.info(f"  - version:    {proj.get('version')}")
    logger.info(f"📁 File JSON salvato in: {json_path}")

    logger.info("📄 Dipendenze rilevate:")
    for d in data['dependencies']:
        logger.info(f"  • {d['groupId']}:{d['artifactId']}:{d['version']}")


if __name__ == "__main__":
    main()
