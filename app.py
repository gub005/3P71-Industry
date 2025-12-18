# Course: COSC 3P71

# Author 1
# Name: Hansel Janzen
# Sdt. no: 7954639

# Author 2
# Name: David Shamess
# Sdt. no: 

from flask import Flask, render_template, request, redirect, url_for
from load_graph import load_graph
from routing import shortest_distance, safest_route, combined_route
import folium
from yolo_inference import analyze_image
import json
import os
from werkzeug.utils import secure_filename
from generate_map import generate_map
from hazard_map import hazard_map
import cv2

#list of colors used to draw bounding boxes on the detected objects
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]


app = Flask(__name__) #create instance of flask server/app


app.config['UPLOAD_FOLDER'] = 'static/uploads' #define file upload location for new street images

#main page of webapp
@app.route("/", methods=["GET", "POST"])
def home():
    G = load_graph() #load instance of the graph from JSON file ensures its updated)

    edges_list = list(G.edges)  #list of edges to populate the jinja2 template
    #init path variables to pass to jinja template, and create folium maps for routes
    shortest_path = None
    safest_path = None
    combined_path = None
    #init lists to contain details of the edges for the calcualted routes, like edge image and safety score
    shortest_dtls = []
    safest_dtls = []
    combined_dtls = []

    #if the user clicks "compute route" = POST request, do the following
    if request.method == "POST":
        #obtained from home.html to select start and end nodes for a route
        start = request.form.get("start")
        end = request.form.get("end")

        # compute paths (shortest, safest and combined)
        shortest_path = shortest_distance(G, start, end)
        safest_path = safest_route(G, start, end)
        combined_path = combined_route(G, start, end)

        #generate folium maps and save in static/ 
        generate_map(shortest_path, 0)
        generate_map(safest_path, 1)
        generate_map(combined_path, 2)
        hazard_map()

        #generate route details for each route
        shortest_dtls = route_edges(shortest_path)
        safest_dtls = route_edges(safest_path)
        combined_dtls = route_edges(combined_path)

    #render home.html given the graph information (nodes, edges), calculated paths, and the details of the paths
    return render_template("home.html", 
                           nodes=list(G.nodes), 
                           edges_list=edges_list, 
                           shortest_path=shortest_path, 
                           safest_path=safest_path, 
                           combined_path=combined_path, 
                           shortest_dtls=shortest_dtls, 
                           safest_dtls=safest_dtls, 
                           combined_dtls=combined_dtls,)


# Helper method to update the JSON file to reflect the networkX graph (make persistent changes)
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

    #overwrite graph.json with the new graph data
    with open("graph.json", "w") as f:
        json.dump(output, f, indent=4) 


# Method to update the image with an edge, run inference on the image,
# and update the safety score of an edge
@app.route("/upload_evidence", methods=["POST"])
def upload_evidence():
    G = load_graph()

    # Get Form Data
    edge_str = request.form.get("edge_select")
    u, v = edge_str.split("|")  # Split the "Source|Target" string back into two nodes

    file = request.files.get("evidence")
    if file:
        # save image file to /static/uploads
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # run inference on uploaded image
        inf_results = analyze_image(save_path, 0.4) #pass in path to the uploaded image, and confidence score threshold

        risk_score = inf_results["score"] #exctract the safety score from inference
        bbox = inf_results["bbox"] #extract the bounding box coordinates of detected objects and other detection data from inference

        # Draw bounding boxes on the processed image
        img = cv2.imread(save_path) #convert the image to cv2 modifiable format
        if img is None:
            raise FileNotFoundError(f"cv2 could not read {save_path}")
        
        #go through every object that was detected, and draw a box for it with a label and confidence score
        for box in bbox:
            color = bbox_colors[box["labelid"] % 10] #get the color of the bounding box to draw
            x1, y1, x2, y2 = box["xyxy"] #extract the xy coords of the object detected

            #draw the rectangle on the image
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            #draw the label and confidence score on the image
            label = f'{box["label"]}: {int(box["confidence"]*100)}%' #concatenate class label and confidence score
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1) # Get font size
            label_ymin = max(y1, labelSize[1]-10) #ensure the label does not clip off the image (top of frame)
            cv2.rectangle(img, (x1, label_ymin-labelSize[1]-10), (x1+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED) #Draw box to put labelText in
            cv2.putText(img, label, (x1, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) #Draw label text

        #replace the image without boxes with the marked up image
        ok = cv2.imwrite(save_path, img)
        if not ok:
            raise RuntimeError(f"cv2.imwrite failed for: {save_path}")
            
        # update the in-memory (networkX) graph
        # init 'images' list if it doesn't exist for this edge
        if "images" not in G[u][v]:
            G[u][v]["images"] = []

        # store image filename in edge attribute
        G[u][v]["images"] = [f"uploads/{filename}"]

        # store safety score in edge attribute    
        G[u][v]["safety"] = risk_score

        # persist changes to JSON
        save_graph_to_json(G)

    hazard_map() #update overall graph to have edge colors reflect new safety scores

    return redirect(url_for("home"))


# create a list of details for each edge in the calculated routes
#edge details include name of edge (name of road), image associated with the edge, and safety score for that edge
def route_edges(path):
    G = load_graph()

    edge_info = []


    for u, v in zip(path[:-1], path[1:]):
            edge_data = G.edges[u, v]

            imgs = edge_data.get("images", [])
            #if the data stored in "images" is not a list, wrap it in one
            if not isinstance(imgs, list):
                imgs = [imgs]

            #add the edge details to the list
            edge_info.append({
                "u": u,
                "v": v,
                "label": f"{u} → {v}",
                "safety": edge_data.get("safety"),
                "image_urls": [url_for("static", filename=p) for p in imgs], #give the url to the file that lives in the static folder for that edge (for home.html to load the image)
            })

    return edge_info


if __name__ == "__main__":
    app.run(debug=True)

