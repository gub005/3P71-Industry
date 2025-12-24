**NOTE**
Some of the contents of this project were a part of the assignment submission and not uploaded to GitHub. If you would like any of the mentioned files for whatever reason (e.g. training artifacts, model weights), reach out to hanseljzn@gmail.com
****

Table of Contents
1 - Project Overview

2 - Tech Stack

3 - Locations of Project Files/Components

4 - Instructions on How to Run the Project

    4.1 - Web App Functions/Features

[1 - Project Overview]

This system addresses road safety by integrating real time computer vision (YOLO) with graph based navigation to not just find the route with the shortest distance from point a to point b, but also the safest.

The computer vision model runs inference on an image of a road, evaluating for hazards within a set list. A graph representing the area the computer vision model would monitor for hazards has attributes like safety and image associated with each edge/road. Based on the hazards detected from inference, a safety score for the associated edge is calculated, stored and used for future routing.

[2 - Tech Stack]

AI/ML           -   YOLO (Ultralytics - YOLO11x), PyTorch
Backend         -   Python, Flask
Mapping/Graph   -   Folium, NetworkX
Computer Vision -   OpenCV (cv2)

[3 - Locations of Project Files/Components]
Component: Screenshots of Running SafetyVision
    Stored in: Screenshots/

Component: Images and Annotations in YOLO and CSV format
    Stored in: Training Data/

Component: Application Code (Graph, UI)
    Stored in: 3P71-Industry/

Component: Model Weights and Training Graphs/Artifacts
    Stored in: Model Data/
        Notes: There are weights and artifacts for the old model, and the new one, the new/current model weights are Model2/, the old is Model1/
        
Component: Python Script to Test Model
    Stored in: Testing/UseModel.py
        Notes: The script takes two arguments, --source, which is the location to the images you are feeding to the model, and --model, which is the location of the weights the model will run on.
        
Component: Project Report
    Stored in: Main Folder (ProjectReportFinal.pdf)
    
Component: Mapillary Script to obtain Images
    Stored in: 3P71-Industry/mapillary/
    
[4 - Instructions on How to run the Project]
First, it's a good idea to setup a python virtual environment to run the application in. I recommend using Anaconda, as it provides a nice UI to manage your environments.

Required Python Libraries: ultralytics networkx folium cv2 flask
    
Once the libraries are installed, run app.py (stored within 3P71-Industry/)

Flask will give you a link to access the Web app.

From within the WebApp you have access to the following functionalities

[4.1 - Web App Functions/Features]
1. Compute a Route
    - Select a Starting and Ending intersection, uplon clicking "compute route" you will be given 3 routes. A route that prioritizes shortest distance, a route that priorities safety, and a combined route
    - Details about the roads along the computed route are also given, including the images that the system has for that road, the safety score of the road, and the road name 
    
2. Upload a new Road Image
    - Select a road (an edge in the graph), which is represented by the connection between two intersections. After selecting a road, upload an image that you desire to represent the chosen road. The model will evaluate the image for hazards, and update the safety score of the road accordingly.
    - There is a folder called Testing/ containing images that can be used to test the system. There are unagumented/ (hazards present), and augmented/ images (no hazards) that can be used for testing.
    
3. Map of Current Road Hazard Status
    - This map is to give a general view of what has been "seen" by the system, and what the statuses of the roads currently are. There is a legend below the map to understand what the colors of the roads mean.