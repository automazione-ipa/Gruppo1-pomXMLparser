"""Config module"""
import json
import logging
import sys

# Path constants
POM_FILE = 'resources/pom.xml'
TXT_REPORT = 'alerts.txt'
RECIPIENTS = ['alessandrobrillante78@gmail.com', 'lucasalzone@gmail.com']
NVD_URL = 'https://nvd.nist.gov/vuln/search'

# Maven Constants
MAVEN_URL = 'http://maven.apache.org/POM/4.0.0'
MVN_GROUP_ID = 'm:groupId'
MVN_ARTIFACT_ID = 'm:artifactId'
MVN_VERSION = 'm:version'
MVN_PKG = 'm:packaging'
MVN_SCOPE = 'm:scope'
MVN_PARENT = 'mvn:parent'
MVN_DEP = './/m:dependency'


def setup_logging(level=logging.INFO):
    """Logging setup (centralized)."""
    logger = logging.getLogger()
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)


setup_logging()


def write_alerts(alerts):
    with open(TXT_REPORT, 'w') as f:
        f.write('\n'.join(alerts))


def write_pom_json(result, json_path="resources/pom_info.json"):
    """Save result to JSON file"""
    with open(json_path, "w") as f:
        json.dump(result, f, indent=4)
    return result, json_path
