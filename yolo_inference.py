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
    results = model(image_path, verbose=False)
    detections = results[0].boxes

    hazard_score = 0.0

    for det in detections:
        conf = det.conf.item()
        if conf < conf_thresh:
            continue

        class_id = int(det.cls.item())
        classname = labels[class_id]

        hazard_score += HAZARD_SCORES.get(classname, 0.0)

    # Cap at 1.0
    hazard_score = min(hazard_score, 1.0)

    return {
        "score": hazard_score
    }