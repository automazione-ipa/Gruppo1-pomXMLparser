"""PomXML Parser Module"""
import xml.etree.ElementTree as ET

from pom_agent.config import (
    MAVEN_URL,
    MVN_GROUP_ID,
    MVN_ARTIFACT_ID,
    MVN_VERSION,
    MVN_PKG,
    MVN_PARENT,
    MVN_SCOPE,
    MVN_DEP
)


def parse_pom(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()

    # Define namespace
    ns = {'m': MAVEN_URL}

    # Extract project information
    artifact_id = root.find(MVN_ARTIFACT_ID, ns).text
    version = root.find(MVN_VERSION, ns).text
    group_id = root.find(MVN_GROUP_ID, ns).text
    packaging = root.find(MVN_PKG, ns).text if root.find(MVN_PKG, ns) is not None else "jar"

    project_info = {
        'groupId': group_id,
        'artifactId': artifact_id,
        'version': version,
        'packaging': packaging
    }

    # Extract dependencies
    dependencies = []
    for dep in root.findall(MVN_DEP, ns):
        dep_info = {
            'groupId': dep.find(MVN_GROUP_ID, ns).text,
            'artifactId': dep.find(MVN_ARTIFACT_ID, ns).text,
            'version': dep.find(MVN_VERSION, ns).text if dep.find(MVN_VERSION, ns) is not None else "",
            'scope': dep.find(MVN_SCOPE, ns).text if dep.find(MVN_SCOPE, ns) is not None else "compile"
        }
        dependencies.append(dep_info)

    return {
        'project': project_info,
        'dependencies': dependencies
    }
