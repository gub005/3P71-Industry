from yolo_inference import analyze_image

def update_edge_safety(G, u, v):
    edge = G[u][v]

    print(f"\nUpdating safety for edge: {u} -> {v}")
    print(f"Initial safety: {edge.get('safety')}")

    total_score = 0

    images = edge.get("images", [])
    if not images:
        print("No images attached to this edge.")
        return

    for img in images:
        print(f"Analyzing image: {img}")
        result = analyze_image(img)

        score = result.get("score", 0)
        print(f"Image score: {score}")

        total_score += score

    edge["safety"] = total_score

    print(f"Updated safety: {edge['safety']}")
