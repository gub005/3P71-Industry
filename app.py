from flask import Flask, render_template, request, redirect, url_for
from load_graph import load_graph
from routing import shortest_distance, safest_route
import folium
from graph_utils import safety_color
from yolo_inference import analyze_image
import json
import os
from werkzeug.utils import secure_filename




app = Flask(__name__)

G = load_graph()
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route("/", methods=["GET", "POST"])
def home():
    path = None
    nodes = list(G.nodes)
    edges_list = list(G.edges)
    route_edges = []

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
            edge_data = G.edges[u, v]
            color = safety_color(edge_data.get("safety", 0.1))

            folium.PolyLine(
                [[G.nodes[u]["lat"], G.nodes[u]["lon"]],
                 [G.nodes[v]["lat"], G.nodes[v]["lon"]]],
                color=color, weight=5, opacity=0.8
            ).add_to(m)

            # Build data for the template
            imgs = edge_data.get("images", [])
            if not isinstance(imgs, list):
                imgs = [imgs]

            route_edges.append({
                "u": u,
                "v": v,
                "label": f"{u} → {v}",
                "safety": edge_data.get("safety"),
                "image_urls": [url_for("static", filename=p) for p in imgs],
            })

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

    return render_template("home.html", nodes=list(G.nodes), edges_list=edges_list, path=path, route_edges=route_edges)


# Helper method to make changes to the NetworkX graph persistent after image uploading
def save_graph_to_json(graph):
    output = {"nodes": [], "edges": []}

    # Save Nodes
    for node, data in graph.nodes(data=True):
        output["nodes"].append({
            "id": node,
            "lat": data.get("lat"),
            "lon": data.get("lon"),
        })

    # Save Edges
    for u, v, data in graph.edges(data=True):
        output["edges"].append({
            "source": u,
            "target": v,
            "distance": data.get("distance"),
            "safety": data.get("safety"),
            "images": data.get("images", []),
        })

    with open("graph.json", "w") as f:
        json.dump(output, f, indent=4)


# Method to update the image with an edge, run inference on the image,
# and update the safety score of an edge
@app.route("/upload_evidence", methods=["POST"])
def upload_evidence():
    # 1. Get Form Data
    edge_str = request.form.get("edge_select")
    u, v = edge_str.split("|")  # Split the "Source|Target" string back into two nodes

    file = request.files.get("evidence")
    if file:
        # 2. Save File
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # 3. Run YOLO Inference
        inf_results = analyze_image(save_path, 0.4) #CV2 Bounding boxes?

        is_hazard = inf_results["hazard_detected"]
        risk_score = inf_results["score"]
        print(f"{risk_score}")

        # 4. Update the Graph (In-Memory)

        # Initialize 'images' list if it doesn't exist for this edge
        if "images" not in G[u][v]:
            G[u][v]["images"] = []

        # Store image filename
        G[u][v]["images"] = [f"uploads/{filename}"]

        # Update Safety Score based on YOLO
        if is_hazard:
            # If hazard found, INCREASE risk / DECREASE safety
            # Assuming 'safety' attribute: 0.1 (Safe) -> 0.9 (Dangerous)
            current_safety = G[u][v].get("safety", 0.1)
            G[u][v]["safety"] = max(current_safety, risk_score)

            print(
                f"Hazard detected on edge {u}->{v}. "
                f"New Safety Score: {G[u][v]['safety']}"
            )

        # 5. Persist Changes to JSON
        save_graph_to_json(G)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

