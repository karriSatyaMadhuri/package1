<<<<<<< HEAD
import streamlit as st
import sys, os

# 🔧 Add parent directory to path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_recommender import LLMRecommender

# 🧭 Page config
st.set_page_config(page_title="📊 Insert Matrix Visualization", layout="wide")
st.title("Step 3️⃣ - Insert Matrix Visualization")

# ✅ Validate session state
if "product" not in st.session_state:
    st.warning("⚠ Please complete Step 1 first.")
    st.stop()

product = st.session_state["product"]

# ✅ Normalize outer box keys with fallback defaults
recommendation = st.session_state.get("recommendation")
outer_box_raw = st.session_state.get("outer_box", {})

outer_box_length = (
    outer_box_raw.get("L")
    or outer_box_raw.get("length")
    or (recommendation.get("box", {}).get("length") if recommendation else None)
    or 1100
)
outer_box_width = (
    outer_box_raw.get("W")
    or outer_box_raw.get("width")
    or (recommendation.get("box", {}).get("width") if recommendation else None)
    or 900
)
outer_box_height = (
    outer_box_raw.get("H")
    or outer_box_raw.get("height")
    or 580
)

# ✅ Validate product keys
required_keys = ["L", "W", "H", "weight"]
if not all(k in product for k in required_keys):
    st.error("🚫 Missing product dimensions. Please complete Step 1.")
    st.stop()

# ✅ Call LLMRecommender
llm = LLMRecommender()
with st.spinner("🔄 Generating insert matrix layout..."):
    insert_data = llm.recommend_insert_matrix(
        part_length=product["L"],
        part_width=product["W"],
        part_height=product["H"],
        weight=product["weight"],
        orientation=product["orientation"][0] if product.get("orientation") else "length-standing",
        outer_box_length=outer_box_length,
        outer_box_width=outer_box_width,
        outer_box_height=outer_box_height
    )

# ✅ Save for next step
st.session_state["insert_matrix"] = insert_data
insert = insert_data["insert"]

# -------------------------------
# Layout: Left = Specs, Right = Grid
# -------------------------------
left, right = st.columns([2, 1])

# -------------------------------
# LEFT SIDE (Insert Specs)
# -------------------------------
with left:
    st.subheader("🧩 Insert & Separator Design")

    with st.container(border=True):
        st.markdown("### Insert Details")
        st.markdown(f"**Type:** {insert['type']}")
        st.markdown(f"**Orientation:** {insert['orientation']}")
        st.markdown(f"**Matrix Pattern:** {insert['matrix']}")
        st.markdown(
            f"**Outer Dimensions:** {outer_box_length} × {outer_box_width} × {outer_box_height} mm"
        )
        st.markdown(
            f"**Cell (Part Orientation):** {insert['cell_dimensions']['length']} × "
            f"{insert['cell_dimensions']['width']} × "
            f"{insert['cell_dimensions']['height']} mm"
        )
        st.markdown(f"**Auto-parts per insert:** {insert['units_per_insert']}")
        st.markdown(f"**Weight per Layer:** {product['weight']} kg")

    with st.container(border=True):
        st.markdown("### 💡 Why this layout")
        st.write(insert_data["reason"])

# -------------------------------
# RIGHT SIDE (Matrix Grid)
# -------------------------------
with right:
    st.subheader("🧮 Matrix Pattern Visualization")

    # get insert data
    cell_L = insert['cell_dimensions']['length']
    cell_W = insert['cell_dimensions']['width']
    insert_H = insert['insert_dimensions']['height']

    units_length = max(0, int(outer_box_length // cell_L))   # cols
    units_width  = max(0, int(outer_box_width  // cell_W))   # rows
    layers       = max(1, int(outer_box_height // insert_H))

    # Debug info (clean format)
    st.markdown(f"**Outer Box (L×W×H):** {outer_box_length} × {outer_box_width} × {outer_box_height} mm")
    st.markdown(f"**Cell Dimensions (L×W):** {cell_L} × {cell_W} mm")
    st.markdown(f"**Insert Tray Height:** {insert_H} mm")
    st.markdown(f"**Matrix Pattern:** {units_length} × {units_width} (rows × cols)")
    st.markdown(f"**Layers (stacked trays):** {layers}")

    if units_length == 0 or units_width == 0:
        st.error("❌ No cells fit into the outer box. Adjust box/cell dimensions.")
        st.stop()

    # Pixel size so it fits neatly
    max_visual_width_px = 350
    cell_px = max(20, min(60, max_visual_width_px // max(1, units_length)))

    total_parts = units_length * units_width * layers
    st.success(f"**Total Parts in Box:** {total_parts}")

    # Show each layer
    for l in range(layers):
        with st.expander(f"Layer {l+1} — {units_width} × {units_length}", expanded=(l==0)):
            grid_html = f"""
            <div style="
                display:grid;
                grid-template-columns: repeat({units_length}, {cell_px}px);
                grid-auto-rows: {cell_px}px;
                gap: 4px;
                justify-content:center;
                margin: 6px 0;
            ">
            """
            for _ in range(units_width * units_length):
                grid_html += (
                    f"<div style='width:{cell_px}px; height:{cell_px}px; "
                    "background:#dfffe2; border:1px solid #b0b0b0; "
                    "display:flex; align-items:center; justify-content:center; "
                    f"font-size:{max(10, cell_px//3)}px; font-weight:600; color:#0b3d05; "
                    "border-radius:4px;'>P</div>"
                )
            grid_html += "</div>"
            st.markdown(grid_html, unsafe_allow_html=True)

    # Legend
    st.caption("🟩 Each tile = 1 part cell. Grid auto-scales to fit screen.")

# -------------------------------
# Navigation button
# -------------------------------
if st.button("maximize truckload"):
    st.switch_page("pages/truckRec.py")

=======
import streamlit as st
import sys, os

# 🔧 Add parent directory to path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_recommender import LLMRecommender

# 🧭 Page config
st.set_page_config(page_title="📊 Insert Matrix Visualization", layout="wide")
st.title("Step 3️⃣ - Insert Matrix Visualization")

# ✅ Validate session state
if "product" not in st.session_state:
    st.warning("⚠ Please complete Step 1 first.")
    st.stop()

product = st.session_state["product"]

# ✅ Normalize outer box keys with fallback defaults
recommendation = st.session_state.get("recommendation")
outer_box_raw = st.session_state.get("outer_box", {})

outer_box_length = (
    outer_box_raw.get("L")
    or outer_box_raw.get("length")
    or (recommendation.get("box", {}).get("length") if recommendation else None)
    or 1100
)
outer_box_width = (
    outer_box_raw.get("W")
    or outer_box_raw.get("width")
    or (recommendation.get("box", {}).get("width") if recommendation else None)
    or 900
)
outer_box_height = (
    outer_box_raw.get("H")
    or outer_box_raw.get("height")
    or 580
)

# ✅ Validate product keys
required_keys = ["L", "W", "H", "weight"]
if not all(k in product for k in required_keys):
    st.error("🚫 Missing product dimensions. Please complete Step 1.")
    st.stop()

# ✅ Call LLMRecommender
llm = LLMRecommender()
with st.spinner("🔄 Generating insert matrix layout..."):
    insert_data = llm.recommend_insert_matrix(
        part_length=product["L"],
        part_width=product["W"],
        part_height=product["H"],
        weight=product["weight"],
        orientation=product["orientation"][0] if product.get("orientation") else "length-standing",
        outer_box_length=outer_box_length,
        outer_box_width=outer_box_width,
        outer_box_height=outer_box_height
    )

# ✅ Save for next step
st.session_state["insert_matrix"] = insert_data
insert = insert_data["insert"]

# -------------------------------
# Layout: Left = Specs, Right = Grid
# -------------------------------
left, right = st.columns([2, 1])

# -------------------------------
# LEFT SIDE (Insert Specs)
# -------------------------------
with left:
    st.subheader("🧩 Insert & Separator Design")

    with st.container(border=True):
        st.markdown("### Insert Details")
        st.markdown(f"**Type:** {insert['type']}")
        st.markdown(f"**Orientation:** {insert['orientation']}")
        st.markdown(f"**Matrix Pattern:** {insert['matrix']}")
        st.markdown(
            f"**Outer Dimensions:** {outer_box_length} × {outer_box_width} × {outer_box_height} mm"
        )
        st.markdown(
            f"**Cell (Part Orientation):** {insert['cell_dimensions']['length']} × "
            f"{insert['cell_dimensions']['width']} × "
            f"{insert['cell_dimensions']['height']} mm"
        )
        st.markdown(f"**Auto-parts per insert:** {insert['units_per_insert']}")
        st.markdown(f"**Weight per Layer:** {product['weight']} kg")

    with st.container(border=True):
        st.markdown("### 💡 Why this layout")
        st.write(insert_data["reason"])

# -------------------------------
# RIGHT SIDE (Matrix Grid)
# -------------------------------
with right:
    st.subheader("🧮 Matrix Pattern Visualization")

    # get insert data
    cell_L = insert['cell_dimensions']['length']
    cell_W = insert['cell_dimensions']['width']
    insert_H = insert['insert_dimensions']['height']

    units_length = max(0, int(outer_box_length // cell_L))   # cols
    units_width  = max(0, int(outer_box_width  // cell_W))   # rows
    layers       = max(1, int(outer_box_height // insert_H))

    # Debug info (clean format)
    st.markdown(f"**Outer Box (L×W×H):** {outer_box_length} × {outer_box_width} × {outer_box_height} mm")
    st.markdown(f"**Cell Dimensions (L×W):** {cell_L} × {cell_W} mm")
    st.markdown(f"**Insert Tray Height:** {insert_H} mm")
    st.markdown(f"**Matrix Pattern:** {units_length} × {units_width} (rows × cols)")
    st.markdown(f"**Layers (stacked trays):** {layers}")

    if units_length == 0 or units_width == 0:
        st.error("❌ No cells fit into the outer box. Adjust box/cell dimensions.")
        st.stop()

    # Pixel size so it fits neatly
    max_visual_width_px = 350
    cell_px = max(20, min(60, max_visual_width_px // max(1, units_length)))

    total_parts = units_length * units_width * layers
    st.success(f"**Total Parts in Box:** {total_parts}")

    # Show each layer
    for l in range(layers):
        with st.expander(f"Layer {l+1} — {units_width} × {units_length}", expanded=(l==0)):
            grid_html = f"""
            <div style="
                display:grid;
                grid-template-columns: repeat({units_length}, {cell_px}px);
                grid-auto-rows: {cell_px}px;
                gap: 4px;
                justify-content:center;
                margin: 6px 0;
            ">
            """
            for _ in range(units_width * units_length):
                grid_html += (
                    f"<div style='width:{cell_px}px; height:{cell_px}px; "
                    "background:#dfffe2; border:1px solid #b0b0b0; "
                    "display:flex; align-items:center; justify-content:center; "
                    f"font-size:{max(10, cell_px//3)}px; font-weight:600; color:#0b3d05; "
                    "border-radius:4px;'>P</div>"
                )
            grid_html += "</div>"
            st.markdown(grid_html, unsafe_allow_html=True)

    # Legend
    st.caption("🟩 Each tile = 1 part cell. Grid auto-scales to fit screen.")

# -------------------------------
# Navigation button
# -------------------------------
if st.button("maximize truckload"):
    st.switch_page("pages/truckRec.py")

>>>>>>> 3a3863a0610f90db8b3fb50756d9c2afa1d1fc53
