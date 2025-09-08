<<<<<<< HEAD
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_recommender import LLMRecommender

st.set_page_config(page_title="🧩 InsertDesign", layout="wide")
st.title("Step 2️⃣ - Insert Design")

# -------------------------------
# 0️⃣ Optional: Default test values
# -------------------------------
if "product" not in st.session_state:
    st.session_state["product"] = {"L": 450, "W": 300, "H": 220, "weight": 18}

if "outer_box" not in st.session_state:
    st.session_state["outer_box"] = {
        "internal_length": 1120,
        "internal_width": 920,
        "internal_height": 580
    }

# -------------------------------
# 1️⃣ Check Step 1 completion
# -------------------------------
if "product" not in st.session_state or "outer_box" not in st.session_state:
    st.warning("⚠️ Please complete Step 1 first.")
    if st.button("⬅️ Go to Step 1"):
        st.switch_page("Step 1️⃣ - Enter Part Details")
    st.stop()  # Stop execution if Step 1 not done

product = st.session_state["product"]
outer_box = st.session_state["outer_box"]

llm = LLMRecommender()

# -------------------------------
# 2️⃣ Analyze orientations
# -------------------------------
with st.spinner("Analyzing optimal orientations..."):
    orientation_analysis = llm.analyze_orientations(
        product["L"], product["W"], product["H"], product["weight"]
    )

if not orientation_analysis or "orientations" not in orientation_analysis:
    st.error("⚠️ No orientation analysis returned from LLM.")
    st.stop()

st.subheader("Analyzing Part Orientations")
st.caption("Evaluating optimal insert configurations...")

# Show orientation results
for label, status in orientation_analysis["orientations"].items():
    if status == "✅":
        st.success(f"{label}: ✅ Allowed")
    elif status == "❌":
        st.error(f"{label}: ❌ Not Allowed")
    else:
        st.info(f"{label}: ⏳ In Progress")

# -------------------------------
# 3️⃣ Generate insert design
# -------------------------------
allowed_orientation = next(
    (k for k, v in orientation_analysis["orientations"].items() if v == "✅"),
    "length-standing"
)

with st.spinner("Generating insert design matrix..."):
    insert_design = llm.recommend_insert_matrix(
        part_length=product["L"],
        part_width=product["W"],
        part_height=product["H"],
        weight=product["weight"],
        orientation=allowed_orientation,
        outer_box_length=outer_box.get("internal_length", 1100),
        outer_box_width=outer_box.get("internal_width", 900),
        outer_box_height=outer_box.get("internal_height", 580)
    )

st.session_state["insert_design"] = insert_design

# -------------------------------
# 4️⃣ Display insert design JSON
# -------------------------------
st.subheader("📦 Insert Design Summary (JSON)")
st.json(st.session_state["insert_design"])
insert = insert_design["insert"]
insert_layer_height = insert["insert_dimensions"]["height"]  # 220
outer_height = outer_box["internal_height"]                  # 580
layers_possible = outer_height // insert_layer_height        # 2

# Attach these extra values for clarity
insert["insert_dimensions"]["outer_box_height"] = outer_height
insert["insert_dimensions"]["layers_possible"] = layers_possible

st.json(insert_design)

# -------------------------------
# 5️⃣ Generate human-readable engineering summary
# -------------------------------
insert = insert_design["insert"]

summary = f"""
Part dimensions {product['L']}×{product['W']}×{product['H']} mm fit within internal {outer_box['internal_length']}×{outer_box['internal_width']}×{outer_box['internal_height']} mm.
Orientation used: {insert['orientation']}.
Units per insert: {insert['units_per_insert']} ({insert['matrix']} matrix).
Cell dimensions: {insert['cell_dimensions']['length']}×{insert['cell_dimensions']['width']}×{insert['cell_dimensions']['height']} mm.
Reason: {insert_design.get('reason', 'No reason provided by LLM.')}
"""
st.subheader("📦 Updated Insert Design Summary")
st.json(insert_design)
st.subheader("📋 Engineering Summary")
st.text(summary)

# -------------------------------
# 6️⃣ Navigation to visualization
# -------------------------------
if st.button("➡️ Go to Visualization"):
    st.switch_page("pages/Visualisation.py")
=======
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_recommender import LLMRecommender

st.set_page_config(page_title="🧩 InsertDesign", layout="wide")
st.title("Step 2️⃣ - Insert Design")

# -------------------------------
# 0️⃣ Optional: Default test values
# -------------------------------
if "product" not in st.session_state:
    st.session_state["product"] = {"L": 450, "W": 300, "H": 220, "weight": 18}

if "outer_box" not in st.session_state:
    st.session_state["outer_box"] = {
        "internal_length": 1120,
        "internal_width": 920,
        "internal_height": 580
    }

# -------------------------------
# 1️⃣ Check Step 1 completion
# -------------------------------
if "product" not in st.session_state or "outer_box" not in st.session_state:
    st.warning("⚠️ Please complete Step 1 first.")
    if st.button("⬅️ Go to Step 1"):
        st.switch_page("Step 1️⃣ - Enter Part Details")
    st.stop()  # Stop execution if Step 1 not done

product = st.session_state["product"]
outer_box = st.session_state["outer_box"]

llm = LLMRecommender()

# -------------------------------
# 2️⃣ Analyze orientations
# -------------------------------
with st.spinner("Analyzing optimal orientations..."):
    orientation_analysis = llm.analyze_orientations(
        product["L"], product["W"], product["H"], product["weight"]
    )

if not orientation_analysis or "orientations" not in orientation_analysis:
    st.error("⚠️ No orientation analysis returned from LLM.")
    st.stop()

st.subheader("Analyzing Part Orientations")
st.caption("Evaluating optimal insert configurations...")

# Show orientation results
for label, status in orientation_analysis["orientations"].items():
    if status == "✅":
        st.success(f"{label}: ✅ Allowed")
    elif status == "❌":
        st.error(f"{label}: ❌ Not Allowed")
    else:
        st.info(f"{label}: ⏳ In Progress")

# -------------------------------
# 3️⃣ Generate insert design
# -------------------------------
allowed_orientation = next(
    (k for k, v in orientation_analysis["orientations"].items() if v == "✅"),
    "length-standing"
)

with st.spinner("Generating insert design matrix..."):
    insert_design = llm.recommend_insert_matrix(
        part_length=product["L"],
        part_width=product["W"],
        part_height=product["H"],
        weight=product["weight"],
        orientation=allowed_orientation,
        outer_box_length=outer_box.get("internal_length", 1100),
        outer_box_width=outer_box.get("internal_width", 900),
        outer_box_height=outer_box.get("internal_height", 580)
    )

st.session_state["insert_design"] = insert_design

# -------------------------------
# 4️⃣ Display insert design JSON
# -------------------------------
st.subheader("📦 Insert Design Summary (JSON)")
st.json(st.session_state["insert_design"])
insert = insert_design["insert"]
insert_layer_height = insert["insert_dimensions"]["height"]  # 220
outer_height = outer_box["internal_height"]                  # 580
layers_possible = outer_height // insert_layer_height        # 2

# Attach these extra values for clarity
insert["insert_dimensions"]["outer_box_height"] = outer_height
insert["insert_dimensions"]["layers_possible"] = layers_possible

st.json(insert_design)

# -------------------------------
# 5️⃣ Generate human-readable engineering summary
# -------------------------------
insert = insert_design["insert"]

summary = f"""
Part dimensions {product['L']}×{product['W']}×{product['H']} mm fit within internal {outer_box['internal_length']}×{outer_box['internal_width']}×{outer_box['internal_height']} mm.
Orientation used: {insert['orientation']}.
Units per insert: {insert['units_per_insert']} ({insert['matrix']} matrix).
Cell dimensions: {insert['cell_dimensions']['length']}×{insert['cell_dimensions']['width']}×{insert['cell_dimensions']['height']} mm.
Reason: {insert_design.get('reason', 'No reason provided by LLM.')}
"""
st.subheader("📦 Updated Insert Design Summary")
st.json(insert_design)
st.subheader("📋 Engineering Summary")
st.text(summary)

# -------------------------------
# 6️⃣ Navigation to visualization
# -------------------------------
if st.button("➡️ Go to Visualization"):
    st.switch_page("pages/Visualisation.py")
>>>>>>> 3a3863a0610f90db8b3fb50756d9c2afa1d1fc53
