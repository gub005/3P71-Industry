from flask import Flask, render_template, request, redirect, url_for
from load_graph import load_graph
from routing import shortest_distance, safest_route, combined_route
import folium
from graph_utils import safety_color
from yolo_inference import analyze_image
import json
import os
from werkzeug.utils import secure_filename
from generate_map import generate_map




app = Flask(__name__)

G = load_graph()
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route("/", methods=["GET", "POST"])
def home():
    edges_list = list(G.edges)
    shortest_path = None
    safest_path = None
    combined_path = None
    shortest_dtls = []
    safest_dtls = []
    combined_dtls = []

    if request.method == "POST":
        start = request.form.get("start")
        end = request.form.get("end")

        # compute shortest path
        shortest_path = shortest_distance(G, start, end)
        safest_path = safest_route(G, start, end)
        combined_path = combined_route(G, start, end)

        #generate folium maps and save in static/ 
        generate_map(shortest_path, 0)
        generate_map(safest_path, 1)
        generate_map(combined_path, 2)

        #generate route details for each route
        shortest_dtls = route_edges(shortest_path)
        safest_dtls = route_edges(safest_path)
        combined_dtls = route_edges(combined_path)

    return render_template("home.html", 
                           nodes=list(G.nodes), 
                           edges_list=edges_list, 
                           shortest_path=shortest_path, 
                           safest_path=safest_path, 
                           combined_path=combined_path, 
                           shortest_dtls=shortest_dtls, 
                           safest_dtls=safest_dtls, 
                           combined_dtls=combined_dtls,)


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



def route_edges(path):
    edge_info = []

    for u, v in zip(path[:-1], path[1:]):
            edge_data = G.edges[u, v]

            # Build data for the template
            imgs = edge_data.get("images", [])
            if not isinstance(imgs, list):
                imgs = [imgs]

            edge_info.append({
                "u": u,
                "v": v,
                "label": f"{u} → {v}",
                "safety": edge_data.get("safety"),
                "image_urls": [url_for("static", filename=p) for p in imgs],
            })

    return edge_info


if __name__ == "__main__":
    app.run(debug=True)

