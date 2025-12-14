from flask import Flask, render_template, request
from load_graph import load_graph
from routing import shortest_distance, safest_route
import folium
from graph_utils import safety_color



app = Flask(__name__)

G = load_graph()

@app.route("/", methods=["GET", "POST"])
def home():
    path = None
    nodes = list(G.nodes)

    if request.method == "POST":
        start = request.form.get("start")
        end = request.form.get("end")

        # compute shortest path
        path = shortest_distance(G, start, end)

        # generate Folium map (centred on first node)
        lat, lon = G.nodes[path[0]]["lat"], G.nodes[path[0]]["lon"]
        m = folium.Map(location=[lat, lon], zoom_start=16)

        # draw the route
        for u, v in zip(path[:-1], path[1:]):
            edge = G[u][v]
            color = safety_color(edge["safety"])  # green, orange, or red
            folium.PolyLine(
                [[G.nodes[u]["lat"], G.nodes[u]["lon"]], [G.nodes[v]["lat"], G.nodes[v]["lon"]]],
                color=color,
                weight=5,
                opacity=0.8
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
        m.save("static/route_map.html")

    return render_template("home.html", nodes=nodes, path=path)

if __name__ == "__main__":
    app.run(debug=True)
