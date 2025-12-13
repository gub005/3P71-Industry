import streamlit as st
from load_graph import load_graph
from routing import shortest_distance, safest_route, combined_route

G = load_graph()

st.title("Smart City Safe Routing")

nodes = list(G.nodes)

start = st.selectbox("Select Start Intersection:", nodes)
end = st.selectbox("Select End Intersection:", nodes)

mode = st.radio("Routing Mode", ["Shortest Distance", "Safest Route", "Combined"])

alpha = st.slider("Safety Weight (alpha)", 0.0, 5.0, 1.0)

if st.button("Compute Route"):
    if mode == "Shortest Distance":
        path = shortest_distance(G, start, end)
    elif mode == "Safest Route":
        path = safest_route(G, start, end)
    else:
        path = combined_route(G, start, end, alpha)

    st.subheader("Route:")
    st.write(path)

    st.subheader("Road Segment Details:")
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        edge = G[u][v]
        st.write(f"**{u} → {v}**")
        st.write(f"Distance: {edge['distance']} meters")
        st.write(f"Safety Score: {edge['safety']}")

        # show associated images
        if edge["images"]:
            st.write("Images that contributed to safety:")
            for img in edge["images"]:
                st.image(img)
        else:
            st.write("No images yet.")
