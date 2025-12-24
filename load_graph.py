# Course: COSC 3P71

# Author 1
# Name: David Shamess

import json
from networkx.readwrite import json_graph

def load_graph():
    with open("graph.json") as f:
        data = json.load(f)   # THIS is required

    G = json_graph.node_link_graph(data, edges="edges", multigraph=False)
    return G
