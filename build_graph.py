# Course: COSC 3P71

# Author 1
# Name: Alexandere Brillon
# Sdt. no: 

# Author 2
# Name:
# Sdt. no:

import json
import math

# Haversine distance (meters)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# REAL STREET INTERSECTION NAMES + GPS COORDINATES
nodes = {
    "Cockburn & Beckwith":   (44.896900, -76.241108),
    "Cockburn & Drummond":   (44.896063, -76.242459),
    "Cockburn & Gore":       (44.895217, -76.243863),
    "Gore & Brock":          (44.896222, -76.245082),
    "Drummond & Brock":      (44.897062, -76.243646),
    "Beckwith & Brock":      (44.897895, -76.242256),
    "Beckwith & Craig":      (44.898848, -76.243445),
    "Drummond & Craig":      (44.898034, -76.244836),
    "Gore & Craig":          (44.897204, -76.246243),
    "Gore & Harvey":         (44.898169, -76.247429),
    "Drummond & Harvey":     (44.899027, -76.246000),
    "Beckwith & Harvey":     (44.899826, -76.244636)
}

# ROAD CONNECTIONS (same order as earlier)
edges = [
    ("Cockburn & Beckwith", "Cockburn & Drummond"),
    ("Cockburn & Drummond", "Cockburn & Gore"),

    ("Cockburn & Beckwith", "Beckwith & Brock"),
    ("Beckwith & Brock", "Beckwith & Craig"),
    ("Beckwith & Craig", "Beckwith & Harvey"),

    ("Cockburn & Drummond", "Drummond & Brock"),
    ("Drummond & Brock", "Drummond & Craig"),
    ("Drummond & Craig", "Drummond & Harvey"),

    ("Cockburn & Gore", "Gore & Brock"),
    ("Gore & Brock", "Gore & Craig"),
    ("Gore & Craig", "Gore & Harvey"),

    ("Gore & Brock", "Drummond & Brock"),
    ("Drummond & Brock", "Beckwith & Brock"),

    ("Beckwith & Craig", "Drummond & Craig"),
    ("Drummond & Craig", "Gore & Craig"),

    ("Gore & Harvey", "Drummond & Harvey"),
    ("Drummond & Harvey", "Beckwith & Harvey")
]

# Build output JSON manually
output = {
    "nodes": [],
    "edges": []
}

# Add nodes
for name, (lat, lon) in nodes.items():
    output["nodes"].append({
        "id": name,
        "lat": lat,
        "lon": lon
    })

# Add edges with real distances, default safety, empty image list
for u, v in edges:
    lat1, lon1 = nodes[u]
    lat2, lon2 = nodes[v]
    dist = round(haversine(lat1, lon1, lat2, lon2), 2)

    output["edges"].append({
        "source": u,
        "target": v,
        "distance": dist,
        "safety": 0.10,
        "images": []
    })

# Save JSON
with open("graph.json", "w") as f:
    json.dump(output, f, indent=4)

print("graph.json created successfully with REAL street names!")
