from ultralytics import YOLO

# Load model ONCE (important for performance)
model = YOLO("best.pt")
labels = model.names

# Define hazard weights
HAZARD_SCORES = {
    "pothole": 0.25,
    "construction": 0.35,
    "log": 0.5,
    "debris": 0.2
}

def analyze_image(image_path, conf_thresh=0.4):
    """
    Runs YOLO on an image and returns a safety score
    """
    results = model(image_path, verbose=False, device='cpu')
    detections = results[0].boxes

    hazard_score = 0.0
    bbox_coords = []

    for i in range(len(detections)):
        conf = detections[i].conf.item()
        if conf < conf_thresh:
            continue

        class_id = int(detections[i].cls.item())
        classname = labels[class_id]
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

        hazard_score += HAZARD_SCORES.get(classname, 0.0)

    # Cap at 1.0
    hazard_score = min(hazard_score, 1.0)

    return {
        "score": hazard_score,
        "hazard_detected": True if hazard_score > 0.0 else False,
        "bbox": bbox_coords
    }

