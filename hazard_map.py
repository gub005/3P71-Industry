# Course: COSC 3P71

# Author 1
# Name: Hansel Janzen
# Sdt. no: 7954639

# Author 2
# Name: David Shamess
# Sdt. no: 6548366

import folium
from load_graph import load_graph


#generate an html map of edges with hazards present, also return a list of edges with hazards and their scores

def hazard_map():
    G = load_graph() #load the most recent version of the graph for updated safety scores
    lat, lon = G.nodes["Gore & Harvey"]["lat"], G.nodes["Cockburn & Beckwith"]["lon"]
    m = folium.Map(location=[lat, lon], zoom_start=16)

    #draw the color of safety for each edge
    for u, v, attr in G.edges(data=True):
        edge_data = G.edges[u, v]
        color = safety_color(edge_data.get("safety", 0.1))

        folium.PolyLine(
            [[G.nodes[u]["lat"], G.nodes[u]["lon"]],
            [G.nodes[v]["lat"], G.nodes[v]["lon"]]],
            color=color, weight=5, opacity=0.4
        ).add_to(m)

    m.save("static/hazard_map.html")


def safety_color(p):
    if p < 0.3:
        return "green"
    elif p < 0.7:
        return "orange"
    else:
        return "red"
