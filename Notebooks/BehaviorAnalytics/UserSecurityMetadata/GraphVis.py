from pathlib import Path
from string import Template
from NodeEdge import Node, Edge
import jsonpickle


class GraphVis:
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def addEdge(self, fromNode, toNode, label):
        if fromNode.group != "User" and fromNode.group != "Group" and fromNode.group != "AzureSubscription" and fromNode.group != "ServicePrincipal":
            raise Exception("Error: Unsupported node type - " +
                            jsonpickle.encode(fromNode, unpicklable=False, make_refs=False))
        if toNode.group != "User" and toNode.group != "Group" and toNode.group != "AzureSubscription" and toNode.group != "ServicePrincipal":
            raise Exception("Error: Unsupported node type - " +
                            jsonpickle.encode(toNode, unpicklable=False, make_refs=False))
        self.nodes.add(fromNode)
        self.nodes.add(toNode)
        edge = Edge(fromNode.id, toNode.id, label)
        self.edges.add(edge)

    def getHtml(self):
        htmlTemplate = Template(Path('./graph.html.template').read_text())
        nodesJson = jsonpickle.encode(
            self.nodes, unpicklable=False, make_refs=False)
        edgesJson = jsonpickle.encode(
            self.edges, unpicklable=False, make_refs=False).replace("from_", "from")
        return htmlTemplate.substitute(NODES=nodesJson, EDGES=edgesJson)
