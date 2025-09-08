<<<<<<< HEAD
# ==============================
# Truck Optimisation Page
# ==============================

import streamlit as st
import itertools

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="🚛 Truck Optimisation", layout="wide")
st.title("🚛 Truck Optimisation")

# -----------------------------
# Initialize session state defaults
# -----------------------------
if "product" not in st.session_state:
    st.session_state["product"] = {}

if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = {}

if "user_box" not in st.session_state:
    st.session_state["user_box"] = {}

# -----------------------------
# Read user inputs safely
# -----------------------------
product = st.session_state.get("product", {})
recommendation = st.session_state.get("recommendation", {})
outer_box_raw = st.session_state.get("user_box", {})

if not outer_box_raw:
    st.warning("⚠ Please generate a recommendation on the Input page first.")
    st.stop()

st.markdown(f"""
**Recommended type:** {recommendation.get('box', {}).get('type', 'N/A')}  
**Internal (L×W×H):** {recommendation.get('box', {}).get('internal', 'N/A')} mm
""")

outer_box = {
    "name": outer_box_raw.get("name", "Outer Box"),
    "dimensions": outer_box_raw.get("dimensions", (1100, 900, 580)),
    "weight": outer_box_raw.get("weight", 18)
}

# -----------------------------
# Define trucks
# -----------------------------
trucks = [
    {"name": "32 ft. single axle", "dimensions": (9754, 2440, 2440), "payload": 16000},
    {"name": "32 ft. multi axle", "dimensions": (9750, 2440, 2440), "payload": 21000},
    {"name": "22 ft. truck", "dimensions": (7300, 2440, 2440), "payload": 10000},
]

# -----------------------------
# Truck optimisation function
# -----------------------------
def calculate_optimisation(truck, box):
    truck_len, truck_wid, truck_hei = truck["dimensions"]
    box_len, box_wid, box_hei = box["dimensions"]

    best_result = None

    # Try all 6 orientations
    for dims in set(itertools.permutations([box_len, box_wid, box_hei], 3)):
        b_len, b_wid, b_hei = dims

        fit_len = truck_len // b_len
        fit_wid = truck_wid // b_wid
        fit_hei = truck_hei // b_hei
        total_boxes_dim = int(fit_len * fit_wid * fit_hei)   # by dimensions

        if total_boxes_dim == 0:
            continue

        # Weight constraint
        max_boxes_by_weight = truck["payload"] // box["weight"]

        # Apply restriction: whichever is smaller
        total_boxes = min(total_boxes_dim, max_boxes_by_weight)

        truck_volume = (truck_len * truck_wid * truck_hei) / 1e9  # m³
        box_volume = (b_len * b_wid * b_hei) / 1e9  # m³
        utilised_volume = total_boxes * box_volume
        utilisation_percent = (utilised_volume / truck_volume) * 100 if truck_volume > 0 else 0

        result = {
            "truck_name": truck["name"],
            "truck_dimensions": truck["dimensions"],
            "truck_volume": round(truck_volume, 2),
            "payload": truck["payload"],
            "box_name": box["name"],
            "box_dimensions": (b_len, b_wid, b_hei),
            "box_volume": round(box_volume, 3),
            "box_weight": box["weight"],
            "boxes_dim_limit": total_boxes_dim,
            "boxes_weight_limit": max_boxes_by_weight,
            "boxes_per_truck": total_boxes,
            "utilisation_percent": round(utilisation_percent, 1),
            "orientation": (fit_len, fit_wid, fit_hei)
        }

        if best_result is None or result["utilisation_percent"] > best_result["utilisation_percent"]:
            best_result = result

    return best_result

# -----------------------------
# UI: Optimisation button
# -----------------------------
if st.button("🔵 Optimise Truck Loading", use_container_width=True):
    st.subheader(f"📦 Analysing for outer box: *{outer_box['name']}*")

    results = []
    for truck in trucks:
        result = calculate_optimisation(truck, outer_box)
        if result:
            results.append(result)

    if not results:
        st.error("No valid truck arrangement found for this box.")
        st.stop()

    # ✅ Pick best truck based on utilisation
    best_truck = max(results, key=lambda r: r["utilisation_percent"])

    # -----------------------------
    # 🚀 Show Recommendation
    # -----------------------------
    st.markdown(f"""
    ## 🏆 Recommended Truck: **{best_truck['truck_name']}**
    ✅ Best utilisation: <span style="color:green; font-weight:bold;">{best_truck['utilisation_percent']}%</span>  
    ✅ Boxes per truck: {best_truck['boxes_per_truck']}  
    ✅ Orientation: {best_truck['orientation'][0]} × {best_truck['orientation'][1]} × {best_truck['orientation'][2]}  
    """, unsafe_allow_html=True)

    st.divider()

    # -----------------------------
    # 📊 Show all trucks for comparison
    # -----------------------------
    for result in results:
        with st.expander(f"🚛 {result['truck_name']} - {result['utilisation_percent']}% filled"):
            st.markdown(f"""
            *Truck Dimensions:* {result['truck_dimensions'][0]} × {result['truck_dimensions'][1]} × {result['truck_dimensions'][2]} mm  
            *Truck Volume:* {result['truck_volume']} m³  
            *Payload Capacity:* {result['payload']} kg  

            *Box Type:* {result['box_name']}  
            *Box Dimensions:* {result['box_dimensions'][0]} × {result['box_dimensions'][1]} × {result['box_dimensions'][2]} mm  
            *Box Volume:* {result['box_volume']} m³  
            *Box Weight:* {result['box_weight']} kg  

            *Boxes by Dimension Limit:* {result['boxes_dim_limit']}  
            *Boxes by Payload Limit:* {result['boxes_weight_limit']}  
            *Final Boxes Loaded:* <span style="color:blue; font-weight:bold;">{result['boxes_per_truck']}</span>  

            *Truck Space Utilisation:* <span style="color:green; font-weight:bold;">{result['utilisation_percent']}%</span>  
            """, unsafe_allow_html=True)

            # Total trucks needed
            quantity = product.get("quantity", 500)
            total_trucks_needed = -(-quantity // result['boxes_per_truck'])
            st.write(f"*Total trucks needed:* {total_trucks_needed}")

            # Orientation & placement
            fit_len, fit_wid, fit_hei = result["orientation"]
            st.write(f"Boxes along Length: *{fit_len}*")
            st.write(f"Boxes along Width: *{fit_wid}*")
            st.write(f"Boxes along Height: *{fit_hei}*")
            st.success(f"Arrangement: {fit_len} × {fit_wid} × {fit_hei} = {fit_len*fit_wid*fit_hei} boxes")

            # Placement grid
            total_boxes = fit_len * fit_wid * fit_hei
            st.markdown(
                f"""
                <div style="border:2px solid #333; padding:8px; text-align:center; 
                            width:100%; max-height:400px; display:grid; 
                            grid-template-columns: repeat({fit_len}, 1fr); 
                            grid-auto-rows: 40px; gap:2px; overflow:auto;">
                """
                +
                "".join([
                    f"<div style='background:#90EE90; display:flex; justify-content:center; align-items:center; font-size:11px;'>B</div>"
                    for _ in range(total_boxes)
                ])
                +
                "</div><p style='margin-top:6px;'>🟩 Optimal box placement (sample layout)</p>",
                unsafe_allow_html=True
            )
=======
# ==============================
# Truck Optimisation Page
# ==============================

import streamlit as st
import itertools

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="🚛 Truck Optimisation", layout="wide")
st.title("🚛 Truck Optimisation")

# -----------------------------
# Initialize session state defaults
# -----------------------------
if "product" not in st.session_state:
    st.session_state["product"] = {}

if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = {}

if "user_box" not in st.session_state:
    st.session_state["user_box"] = {}

# -----------------------------
# Read user inputs safely
# -----------------------------
product = st.session_state.get("product", {})
recommendation = st.session_state.get("recommendation", {})
outer_box_raw = st.session_state.get("user_box", {})

if not outer_box_raw:
    st.warning("⚠ Please generate a recommendation on the Input page first.")
    st.stop()

st.markdown(f"""
**Recommended type:** {recommendation.get('box', {}).get('type', 'N/A')}  
**Internal (L×W×H):** {recommendation.get('box', {}).get('internal', 'N/A')} mm
""")

outer_box = {
    "name": outer_box_raw.get("name", "Outer Box"),
    "dimensions": outer_box_raw.get("dimensions", (1100, 900, 580)),
    "weight": outer_box_raw.get("weight", 18)
}

# -----------------------------
# Define trucks
# -----------------------------
trucks = [
    {"name": "32 ft. single axle", "dimensions": (9754, 2440, 2440), "payload": 16000},
    {"name": "32 ft. multi axle", "dimensions": (9750, 2440, 2440), "payload": 21000},
    {"name": "22 ft. truck", "dimensions": (7300, 2440, 2440), "payload": 10000},
]

# -----------------------------
# Truck optimisation function
# -----------------------------
def calculate_optimisation(truck, box):
    truck_len, truck_wid, truck_hei = truck["dimensions"]
    box_len, box_wid, box_hei = box["dimensions"]

    best_result = None

    # Try all 6 orientations
    for dims in set(itertools.permutations([box_len, box_wid, box_hei], 3)):
        b_len, b_wid, b_hei = dims

        fit_len = truck_len // b_len
        fit_wid = truck_wid // b_wid
        fit_hei = truck_hei // b_hei
        total_boxes_dim = int(fit_len * fit_wid * fit_hei)   # by dimensions

        if total_boxes_dim == 0:
            continue

        # Weight constraint
        max_boxes_by_weight = truck["payload"] // box["weight"]

        # Apply restriction: whichever is smaller
        total_boxes = min(total_boxes_dim, max_boxes_by_weight)

        truck_volume = (truck_len * truck_wid * truck_hei) / 1e9  # m³
        box_volume = (b_len * b_wid * b_hei) / 1e9  # m³
        utilised_volume = total_boxes * box_volume
        utilisation_percent = (utilised_volume / truck_volume) * 100 if truck_volume > 0 else 0

        result = {
            "truck_name": truck["name"],
            "truck_dimensions": truck["dimensions"],
            "truck_volume": round(truck_volume, 2),
            "payload": truck["payload"],
            "box_name": box["name"],
            "box_dimensions": (b_len, b_wid, b_hei),
            "box_volume": round(box_volume, 3),
            "box_weight": box["weight"],
            "boxes_dim_limit": total_boxes_dim,
            "boxes_weight_limit": max_boxes_by_weight,
            "boxes_per_truck": total_boxes,
            "utilisation_percent": round(utilisation_percent, 1),
            "orientation": (fit_len, fit_wid, fit_hei)
        }

        if best_result is None or result["utilisation_percent"] > best_result["utilisation_percent"]:
            best_result = result

    return best_result

# -----------------------------
# UI: Optimisation button
# -----------------------------
if st.button("🔵 Optimise Truck Loading", use_container_width=True):
    st.subheader(f"📦 Analysing for outer box: *{outer_box['name']}*")

    results = []
    for truck in trucks:
        result = calculate_optimisation(truck, outer_box)
        if result:
            results.append(result)

    if not results:
        st.error("No valid truck arrangement found for this box.")
        st.stop()

    # ✅ Pick best truck based on utilisation
    best_truck = max(results, key=lambda r: r["utilisation_percent"])

    # -----------------------------
    # 🚀 Show Recommendation
    # -----------------------------
    st.markdown(f"""
    ## 🏆 Recommended Truck: **{best_truck['truck_name']}**
    ✅ Best utilisation: <span style="color:green; font-weight:bold;">{best_truck['utilisation_percent']}%</span>  
    ✅ Boxes per truck: {best_truck['boxes_per_truck']}  
    ✅ Orientation: {best_truck['orientation'][0]} × {best_truck['orientation'][1]} × {best_truck['orientation'][2]}  
    """, unsafe_allow_html=True)

    st.divider()

    # -----------------------------
    # 📊 Show all trucks for comparison
    # -----------------------------
    for result in results:
        with st.expander(f"🚛 {result['truck_name']} - {result['utilisation_percent']}% filled"):
            st.markdown(f"""
            *Truck Dimensions:* {result['truck_dimensions'][0]} × {result['truck_dimensions'][1]} × {result['truck_dimensions'][2]} mm  
            *Truck Volume:* {result['truck_volume']} m³  
            *Payload Capacity:* {result['payload']} kg  

            *Box Type:* {result['box_name']}  
            *Box Dimensions:* {result['box_dimensions'][0]} × {result['box_dimensions'][1]} × {result['box_dimensions'][2]} mm  
            *Box Volume:* {result['box_volume']} m³  
            *Box Weight:* {result['box_weight']} kg  

            *Boxes by Dimension Limit:* {result['boxes_dim_limit']}  
            *Boxes by Payload Limit:* {result['boxes_weight_limit']}  
            *Final Boxes Loaded:* <span style="color:blue; font-weight:bold;">{result['boxes_per_truck']}</span>  

            *Truck Space Utilisation:* <span style="color:green; font-weight:bold;">{result['utilisation_percent']}%</span>  
            """, unsafe_allow_html=True)

            # Total trucks needed
            quantity = product.get("quantity", 500)
            total_trucks_needed = -(-quantity // result['boxes_per_truck'])
            st.write(f"*Total trucks needed:* {total_trucks_needed}")

            # Orientation & placement
            fit_len, fit_wid, fit_hei = result["orientation"]
            st.write(f"Boxes along Length: *{fit_len}*")
            st.write(f"Boxes along Width: *{fit_wid}*")
            st.write(f"Boxes along Height: *{fit_hei}*")
            st.success(f"Arrangement: {fit_len} × {fit_wid} × {fit_hei} = {fit_len*fit_wid*fit_hei} boxes")

            # Placement grid
            total_boxes = fit_len * fit_wid * fit_hei
            st.markdown(
                f"""
                <div style="border:2px solid #333; padding:8px; text-align:center; 
                            width:100%; max-height:400px; display:grid; 
                            grid-template-columns: repeat({fit_len}, 1fr); 
                            grid-auto-rows: 40px; gap:2px; overflow:auto;">
                """
                +
                "".join([
                    f"<div style='background:#90EE90; display:flex; justify-content:center; align-items:center; font-size:11px;'>B</div>"
                    for _ in range(total_boxes)
                ])
                +
                "</div><p style='margin-top:6px;'>🟩 Optimal box placement (sample layout)</p>",
                unsafe_allow_html=True
            )
>>>>>>> 3a3863a0610f90db8b3fb50756d9c2afa1d1fc53
