# Course: COSC 3P71

# Author 1
# Name: Hansel Janzen
# Sdt. no: 7954639

# Author 2
# Name: David Shamess
# Sdt. no: 

from ultralytics import YOLO

# Load model ONCE (important for performance)
model = YOLO("best.pt")
labels = model.names

# Define hazard weights
HAZARD_SCORES = {
    "pothole": 0.25,
    "pylon": 0.1,
    "barrier": 0.3,
    "barrel": 0.1,
    "log": 0.5,
    "debris": 0.2
}

#run the YOLO model on an image, return a safety score, and details of each object detected (bounding box coordinates, object name, and confidence in detection)
def analyze_image(image_path, conf_thresh=0.4):
    results = model(image_path, verbose=False, device='cpu') #run the model on the image, use CPU to load images rather than GPU because of limited hardware capabilities
    detections = results[0].boxes #store the results of inference to extract data from

    hazard_score = 0.0
    bbox_coords = []

    #go through all the objects detected in inference
    for i in range(len(detections)):
        conf = detections[i].conf.item()

        #if the object detected has a confidence level below the threshold, skip it
        if conf < conf_thresh:
            continue

        class_id = int(detections[i].cls.item()) #obtain the ID of the object detected
        classname = labels[class_id] #obtain the label of the object detected

        # Ultralytics returns results in Tensor format, which have to be converted to a regular Python array
        xyxy_tensor = detections[i].xyxy.cpu() # Detections in tensor format in CPU memory
        xyxy = xyxy_tensor.numpy().squeeze() # Convert tensors to numpy array, squeezing out unnessary dimensions
        x1, y1, x2, y2 = xyxy.astype(int) # Extract individual coordinates and convert to int

        #append bbox coordinates for the detected object to the bbox_coords list
        #store classname, confidence score and coordinates in the list as a dictionary
        bbox_coords.append({
            "label": classname,
            "labelid": class_id,
            "confidence": conf,
            "xyxy": [x1,y1,x2,y2]
        })

        #sum up the objects detected to get a safety score
        hazard_score += HAZARD_SCORES.get(classname, 0.0)

    # Cap at 1.0
    hazard_score = min(hazard_score, 1.0)

    return {
        "score": hazard_score,
        "hazard_detected": True if hazard_score > 0.0 else False,
        "bbox": bbox_coords
    }

