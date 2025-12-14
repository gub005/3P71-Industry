from load_graph import load_graph
from graph_safety import update_edge_safety

G = load_graph()

u = "Cockburn & Beckwith"
v = "Beckwith & Brock"

update_edge_safety(G, u, v)

print("\nFINAL EDGE DATA:")
print(G[u][v])
