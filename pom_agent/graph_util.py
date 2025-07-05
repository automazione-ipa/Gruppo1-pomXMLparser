from networkx import DiGraph


def build_dependency_graph(data: dict) -> DiGraph:
    g = DiGraph()
    project = data['project']['artifactId']
    g.add_node(project, **data['project'])
    for dep in data['dependencies']:
        key = dep['artifactId']
        g.add_node(key, **dep)
        g.add_edge(project, key, scope=dep['scope'])
    return g