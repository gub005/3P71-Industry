from pathlib import Path
import requests

TOKEN = "MLY|25126427610349644|f1794d3e373d529431bf9dca9397f01f"

# FIXED: order must be lon, lat (Ontario longitude is negative)
lon, lat = -76.2440273114915, 44.898000488494546  #44.897686, -76.244378 are coords of the real location road graph is modeled after

url = "https://graph.mapillary.com/images"

params = {
    "access_token": TOKEN,
    "fields": "id,computed_geometry,thumb_1024_url",  # FIXED: thumb_original_url is often missing
    "closeto": f"{lon},{lat}",   # NOTE: lon,lat order
    "radius": 10000,               # meters
    "limit": 500                 #limit of images to return
}

resp = requests.get(url, params=params)
resp.raise_for_status()  # waits for HTTP request code, if 200-399 does nothing, otherwise it raises an error
data = resp.json()       # put the response in json format and store in a list

print("Images returned:", len(data.get("data", [])))  # helpful debug print

# save images from api call, stored in list "data" to the out_dir

out_dir = Path(r"D:/University/Third Year/Courses/COSC 3P71/Proj/Training Data/Mapillary Data/RoadGraph_Location_Images")
out_dir.mkdir(parents=True, exist_ok=True)

for img in data.get("data", []):
    image_id = img["id"]
    thumb_url = img["thumb_1024_url"]  # FIXED: use 1024-size thumbnail (always available)

    # Extract coordinates
    coords = img["computed_geometry"]["coordinates"]
    lon, lat = coords  # GeoJSON format = [lon, lat]

    # Download image
    img_resp = requests.get(thumb_url)
    img_resp.raise_for_status()

    # Build cleaned filename (limits decimal places)
    lon_fmt = f"{lon:.6f}"
    lat_fmt = f"{lat:.6f}"

    filename = f"{image_id}_{lon_fmt}_{lat_fmt}.jpg"
    out_path = out_dir / filename

    with open(out_path, "wb") as f:
        f.write(img_resp.content)

    print("Saved:", out_path)
