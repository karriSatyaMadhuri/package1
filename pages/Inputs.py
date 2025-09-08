<<<<<<< HEAD
import streamlit as st
from llm_recommender import LLMRecommender

st.set_page_config(page_title="📦 Packaging Asset Recommender", layout="wide")
st.title("Step 1️⃣ - Enter Part Details")

llm = LLMRecommender()

# -------------------------------
# Layout: Two columns
# -------------------------------
left_col, right_col = st.columns([2, 1], gap="large")

# -------------------------------
# Product inputs (LEFT)
# -------------------------------
with left_col:
    st.subheader("Auto Part Details")
    length = st.number_input("Length (mm)", min_value=10, value=450)
    width = st.number_input("Width (mm)", min_value=10, value=300)
    height = st.number_input("Height (mm)", min_value=10, value=220)
    weight = st.number_input("Weight (kg)", min_value=0.1, value=1.0)
    fragile = st.checkbox("Is the product fragile?")
    stacking = st.checkbox("Stacking Allowed?")

    # Orientation checkboxes
    st.subheader("Orientation Restrictions")
    orientation_options = ["Height-standing", "Length-standing", "Width-standing"]
    selected_orientation = {}
    for option in orientation_options:
        selected_orientation[option] = st.checkbox(option)
    orientation = [opt for opt, checked in selected_orientation.items() if checked]

    st.subheader("Logistics")
    cities = ["Mumbai", "Chennai", "Bangalore", "Delhi", "Kolkata"]
    source_city = st.selectbox("Source City", options=cities)
    destination_city = st.selectbox("Destination City", options=cities)

# -------------------------------
# Recommendation & Buttons (RIGHT)
# -------------------------------
with right_col:
    st.subheader("Outer Box Recommendation")

    if st.button("🔍 Generate Recommendation", use_container_width=True):
        if all([length, width, height, weight]):
            with st.spinner("Thinking through optimal packaging..."):
                recommendation = llm.recommend(
                    length=length,
                    width=width,
                    height=height,
                    weight=weight,
                    fragile="High" if fragile else "Low",
                    stacking=stacking,
                    orientation=orientation,
                    forklift=False,
                    forklift_capacity=0,
                    quantity=500,
                    source=source_city,
                    destination=destination_city
                )

                # Save to session
                st.session_state["product"] = {
                    "L": float(length),
                    "W": float(width),
                    "H": float(height),
                    "weight": float(weight),
                    "fragile": fragile,
                    "stacking": stacking,
                    "orientation": orientation,
                    "source": source_city,
                    "destination": destination_city
                }
                st.session_state["recommendation"] = recommendation

                # ✅ Fixed: clean dimensions safely
                internal_dims = llm._clean_dimensions_tuple(recommendation['box']['internal'])

                st.session_state["user_box"] = {
                    "name": recommendation['box']['type'],
                    "dimensions": internal_dims,
                    "weight": float(weight)
                }

                # Styled card for recommendation
                with st.container(border=True):
                    st.markdown(f"""
                    **Recommended type:** {recommendation['box']['type']}  
                    **Internal (L×W×H):** {recommendation['box']['internal']} mm  
                    **External (L×W×H):** {recommendation['box']['external']} mm  
                    **Capacity:** {recommendation['box']['capacity']} kg  
                    **Material:** {recommendation['box']['material']}  
                    """)
                    st.info("💡 Why this recommendation:")
                    st.write(recommendation["reason"])

    # Navigation button
    if st.button("➡️ Go to Insert Design", use_container_width=True):
        if "product" in st.session_state:
            st.switch_page("pages/InsertDesign.py")
        else:
            st.warning("⚠️ Please generate a recommendation first.")
=======
import streamlit as st
from llm_recommender import LLMRecommender

st.set_page_config(page_title="📦 Packaging Asset Recommender", layout="wide")
st.title("Step 1️⃣ - Enter Part Details")

llm = LLMRecommender()

# -------------------------------
# Layout: Two columns
# -------------------------------
left_col, right_col = st.columns([2, 1], gap="large")

# -------------------------------
# Product inputs (LEFT)
# -------------------------------
with left_col:
    st.subheader("Auto Part Details")
    length = st.number_input("Length (mm)", min_value=10, value=450)
    width = st.number_input("Width (mm)", min_value=10, value=300)
    height = st.number_input("Height (mm)", min_value=10, value=220)
    weight = st.number_input("Weight (kg)", min_value=0.1, value=1.0)
    fragile = st.checkbox("Is the product fragile?")
    stacking = st.checkbox("Stacking Allowed?")

    # Orientation checkboxes
    st.subheader("Orientation Restrictions")
    orientation_options = ["Height-standing", "Length-standing", "Width-standing"]
    selected_orientation = {}
    for option in orientation_options:
        selected_orientation[option] = st.checkbox(option)
    orientation = [opt for opt, checked in selected_orientation.items() if checked]

    st.subheader("Logistics")
    cities = ["Mumbai", "Chennai", "Bangalore", "Delhi", "Kolkata"]
    source_city = st.selectbox("Source City", options=cities)
    destination_city = st.selectbox("Destination City", options=cities)

# -------------------------------
# Recommendation & Buttons (RIGHT)
# -------------------------------
with right_col:
    st.subheader("Outer Box Recommendation")

    if st.button("🔍 Generate Recommendation", use_container_width=True):
        if all([length, width, height, weight]):
            with st.spinner("Thinking through optimal packaging..."):
                recommendation = llm.recommend(
                    length=length,
                    width=width,
                    height=height,
                    weight=weight,
                    fragile="High" if fragile else "Low",
                    stacking=stacking,
                    orientation=orientation,
                    forklift=False,
                    forklift_capacity=0,
                    quantity=500,
                    source=source_city,
                    destination=destination_city
                )

                # Save to session
                st.session_state["product"] = {
                    "L": float(length),
                    "W": float(width),
                    "H": float(height),
                    "weight": float(weight),
                    "fragile": fragile,
                    "stacking": stacking,
                    "orientation": orientation,
                    "source": source_city,
                    "destination": destination_city
                }
                st.session_state["recommendation"] = recommendation

                # ✅ Fixed: clean dimensions safely
                internal_dims = llm._clean_dimensions_tuple(recommendation['box']['internal'])

                st.session_state["user_box"] = {
                    "name": recommendation['box']['type'],
                    "dimensions": internal_dims,
                    "weight": float(weight)
                }

                # Styled card for recommendation
                with st.container(border=True):
                    st.markdown(f"""
                    **Recommended type:** {recommendation['box']['type']}  
                    **Internal (L×W×H):** {recommendation['box']['internal']} mm  
                    **External (L×W×H):** {recommendation['box']['external']} mm  
                    **Capacity:** {recommendation['box']['capacity']} kg  
                    **Material:** {recommendation['box']['material']}  
                    """)
                    st.info("💡 Why this recommendation:")
                    st.write(recommendation["reason"])

    # Navigation button
    if st.button("➡️ Go to Insert Design", use_container_width=True):
        if "product" in st.session_state:
            st.switch_page("pages/InsertDesign.py")
        else:
            st.warning("⚠️ Please generate a recommendation first.")
>>>>>>> 3a3863a0610f90db8b3fb50756d9c2afa1d1fc53
