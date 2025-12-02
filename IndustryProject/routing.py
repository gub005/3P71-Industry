import networkx as nx

def shortest_distance(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight="distance")

def safest_route(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight="safety")

def combined_route(G, start, end, alpha=1.0):
    # weight = distance + alpha * safety
    for u, v, d in G.edges(data=True):
        d["weight"] = d["distance"] + alpha * d["safety"]

    return nx.shortest_path(G, source=start, target=end, weight="weight")
