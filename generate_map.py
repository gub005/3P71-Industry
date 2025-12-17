import folium
from load_graph import load_graph
from graph_utils import safety_color

G = load_graph()

#generate a map for a certain type of path
#path is a sequence of edges, type is an integer representing safest, shortest, or combined path
def generate_map(path, type):
        lat, lon = G.nodes[path[0]]["lat"], G.nodes[path[0]]["lon"]
        m = folium.Map(location=[lat, lon], zoom_start=16)

        # draw the route
        for u, v in zip(path[:-1], path[1:]):
            edge_data = G.edges[u, v]
            color = safety_color(edge_data.get("safety", 0.1))

            folium.PolyLine(
                [[G.nodes[u]["lat"], G.nodes[u]["lon"]],
                 [G.nodes[v]["lat"], G.nodes[v]["lon"]]],
                color=color, weight=5, opacity=0.8
            ).add_to(m)

        # Add start marker
        folium.Marker(
            location=[G.nodes[path[0]]["lat"], G.nodes[path[0]]["lon"]],
            popup="Start",
            icon=folium.Icon(color="green")
        ).add_to(m)

        # add end location marker
        folium.Marker(
            location=[G.nodes[path[-1]]["lat"], G.nodes[path[-1]]["lon"]],
            popup="End",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # save our map to static folder for display
        if type == 0:
            m.save("static/shortestroute_map.html")
        elif type == 1:
            m.save("static/safestroute_map.html")
        elif type == 2: 
            m.save("static/combinedroute_map.html")