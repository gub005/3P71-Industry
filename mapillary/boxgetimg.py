# Finds all images Mapillary knows about at that location
# Works even when /images?closeto= returns 0
# saves coordinates with 6-decimal precision
# Stores everything in a folder + optional metadata CSV
#

import requests
from pathlib import Path
import mapbox_vector_tile
import math
import csv

# ----------------------------------------------------
# SETTINGS
# ----------------------------------------------------
TOKEN = "MLY|25126427610349644|f1794d3e373d529431bf9dca9397f01f"

# The location you're interested in
lat = 44.89814752321598
lon = -76.24493951025102

# Zoom level for tile resolution (14–15 is good)
Z = 14

# Output folder
out_dir = Path(r"D:/Mapillary_Tile_Download")
out_dir.mkdir(parents=True, exist_ok=True)

# Metadata file
metadata_file = out_dir / "metadata.csv"


# ----------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------

def latlon_to_tile(lat, lon, z):
    """Convert lat/lon to slippy map tile indices."""
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def download_tile(z, x, y, token):
    """Download a Mapillary vector tile."""
    url = f"https://tiles.mapillary.com/maps/vtp/mly1_public/2/{z}/{x}/{y}?access_token={token}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content


def parse_tile(tile_bytes):
    """Decode the vector tile and return image features."""
    tile = mapbox_vector_tile.decode(tile_bytes)
    # Layer name is ALWAYS "image" for image points
    if "image" not in tile:
        return []
    return tile["image"]["features"]


def get_image_download_url(image_id, token):
    """Query image metadata to get download URL."""
    url = f"https://graph.mapillary.com/{image_id}"
    params = {
        "access_token": token,
        "fields": "thumb_1024_url,computed_geometry"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


# ----------------------------------------------------
# MAIN PROCESS
# ----------------------------------------------------

print("Converting coordinate to tile index...")
x, y = latlon_to_tile(lat, lon, Z)
print(f"Tile: Z={Z}, X={x}, Y={y}")

print("Downloading vector tile...")
tile_bytes = download_tile(Z, x, y, TOKEN)

print("Parsing tile for images...")
features = parse_tile(tile_bytes)
print(f"Found {len(features)} images in tile.")

# Prepare metadata CSV
with open(metadata_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["image_id", "lon", "lat", "filename"])

    # Process each feature (image point)
    for feat in features:
        props = feat["properties"]

        if "id" not in props:
            continue

        image_id = props["id"]

        # Tile geometries are in pixel coordinates; convert to lon/lat
        # Convert tile-local point to lat/lon
        geom = feat["geometry"]["coordinates"]
        px, py = geom  # 0–4096 tile-pixel coordinates

        # Convert pixel coords → lat lon
        # Based on slippy tile pixel formulas
        def tile_pixel_to_latlon(px, py, x, y, z):
            tile_size = 4096
            n = 2.0 ** z

            lon_deg = (x + px / tile_size) / n * 360.0 - 180.0

            lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y + py / tile_size) / n)))
            lat_deg = math.degrees(lat_rad)

            return lat_deg, lon_deg

        img_lat, img_lon = tile_pixel_to_latlon(px, py, x, y, Z)

        print(f"Fetching metadata for image {image_id}...")
        info = get_image_download_url(image_id, TOKEN)

        if "thumb_1024_url" not in info:
            print(f"Skipping {image_id}: no public download URL")
            continue

        img_url = info["thumb_1024_url"]

        # Download image
        img_resp = requests.get(img_url)
        img_resp.raise_for_status()

        # Save
        filename = f"{image_id}_{img_lon:.6f}_{img_lat:.6f}.jpg"
        out_path = out_dir / filename

        with open(out_path, "wb") as f_out:
            f_out.write(img_resp.content)

        writer.writerow([image_id, img_lon, img_lat, filename])
        print(f"Saved {out_path}")

print("\nDONE — All available images in the tile were downloaded.")
print("Metadata saved to:", metadata_file)
