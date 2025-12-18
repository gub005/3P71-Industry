import folium
from load_graph import load_graph
from graph_utils import safety_color

G = load_graph()

#generate an html map of edges with hazards present, also return a list of edges with hazards and their scores

def hazard_map():
    lat, lon = G.nodes["Gore & Harvey"]["lat"], G.nodes["Cockburn & Beckwith"]["lon"]
    m = folium.Map(location=[lat, lon], zoom_start=16)

    for u, v, attr in G.edges(data=True):
        edge_data = G.edges[u, v]
        color = safety_color(edge_data.get("safety", 0.1))

        folium.PolyLine(
            [[G.nodes[u]["lat"], G.nodes[u]["lon"]],
            [G.nodes[v]["lat"], G.nodes[v]["lon"]]],
            color=color, weight=5, opacity=0.4
        ).add_to(m)

    m.save("static/hazard_map.html")
