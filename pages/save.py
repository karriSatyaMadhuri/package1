
import streamlit as st
import itertools

st.set_page_config(page_title="Truck Optimization & Box Placement", layout="wide")
st.title("📦 Truck Optimization & Box Placement")

# -----------------------------
# Get saved session data
# -----------------------------
box_data = st.session_state.get("box_data", [])
route_info = st.session_state.get("route_info", {})

if not box_data or not route_info:
    st.error("❌ No saved data found. Please go back and enter box & route details first.")
    st.stop()

# First box for optimization
box = box_data[0]

# -----------------------------
# Show box & route info
# -----------------------------
with st.container():
    st.subheader("📦 Selected Box & Route Info")
    st.write(f"*Box Type:* {box['type']}")
    st.write(f"*Quantity:* {box['quantity']}")
    st.write(f"*Dimensions:* {box['dimensions'][0]} × {box['dimensions'][1]} × {box['dimensions'][2]} mm")
    st.write(f"*Payload:* {box['payload']} kg")
    st.markdown("---")
    st.write(f"*Source:* {route_info['Source']}")
    st.write(f"*Destination:* {route_info['Destination']}")
    st.write("🛣 *Route Type Distribution:*")
    for route, pct in route_info["Route Distribution"].items():
        st.write(f"- {route}: {pct}%")

st.divider()

# -----------------------------
# Define trucks
# -----------------------------
trucks = [
    {"name": "32 ft. Single Axle", "dimensions": (9750, 2440, 2440), "payload": 16000},
    {"name": "32 ft. Multi Axle", "dimensions": (9750, 2440, 2440), "payload": 21000},
    {"name": "22 ft. Truck", "dimensions": (7300, 2440, 2440), "payload": 10000},
]

st.subheader("🚛 Available Trucks")
cols = st.columns(len(trucks))
for col, truck in zip(cols, trucks):
    with col:
        st.markdown(f"### {truck['name']}")
        st.write(f"*Dimensions:* {truck['dimensions'][0]} × {truck['dimensions'][1]} × {truck['dimensions'][2]} mm")
        st.write(f"*Payload:* {truck['payload']} kg")

st.divider()

# -----------------------------
# Payload toggle
# -----------------------------
apply_payload = st.checkbox("🚦 Apply Payload Restriction", value=True)


# -----------------------------
# Truck optimisation function
# -----------------------------
def calculate_optimisation(truck, box, apply_payload=True):
    truck_len, truck_wid, truck_hei = truck["dimensions"]
    box_len, box_wid, box_hei = box["dimensions"]

    best_result = None

    # Try all 6 orientations
    for dims in set(itertools.permutations([box_len, box_wid, box_hei], 3)):
        b_len, b_wid, b_hei = dims

        # Fit counts along each axis
        fit_len = int(truck_len // b_len)
        fit_wid = int(truck_wid // b_wid)
        fit_hei = int(truck_hei // b_hei)
        boxes_by_space = fit_len * fit_wid * fit_hei

        if boxes_by_space <= 0:
            continue

        # Payload limit
        max_boxes_by_weight = None
        if box["payload"] > 0:
            max_boxes_by_weight = int(truck["payload"] // float(box["payload"]))
            if apply_payload:
                total_boxes = min(boxes_by_space, max_boxes_by_weight)
            else:
                total_boxes = boxes_by_space
        else:
            continue

        # Volume utilisation
        truck_volume = (truck_len * truck_wid * truck_hei) / 1e9  # m³
        box_volume = (b_len * b_wid * b_hei) / 1e9  # m³
        utilised_volume = total_boxes * box_volume
        utilisation_percent = (utilised_volume / truck_volume) * 100 if truck_volume > 0 else 0

        # Space utilisation (% of boxes that fit by space actually loaded)
        utilisation_by_space = (total_boxes / boxes_by_space) * 100 if boxes_by_space > 0 else 0

        result = {
            "truck_name": truck["name"],
            "truck_volume": round(truck_volume, 2),
            "box_volume": round(box_volume, 3),
            "boxes_by_space": boxes_by_space,
            "max_boxes_by_weight": max_boxes_by_weight,
            "boxes_per_truck": total_boxes,
            "utilisation_percent": round(utilisation_percent, 1),
            "utilisation_by_space": round(utilisation_by_space, 1),
            "orientation": (fit_len, fit_wid, fit_hei),
            "box_dims_used": dims,
        }

        if best_result is None or result["utilisation_percent"] > best_result["utilisation_percent"]:
            best_result = result

    return best_result


# -----------------------------
# Optimisation Button
# -----------------------------
if st.button("🔵 Optimise Truck Loading", type="primary", use_container_width=True):
    st.subheader("📊 Truck Optimisation Results")

    for truck in trucks:
        result = calculate_optimisation(truck, box, apply_payload)

        with st.expander(f"🚛 {result['truck_name']} - {result['utilisation_percent']}% filled"):
            # Summary row
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.markdown(f"**Truck Volume:** {result['truck_volume']} m³")
            col2.markdown(f"**Box Volume:** {result['box_volume']} m³")
            col3.markdown(f"**Boxes (by space):** {result['boxes_by_space']}")
            col4.markdown(f"**Boxes (by payload):** {result['max_boxes_by_weight']}")
            col5.markdown(f"**Boxes Loaded:** {result['boxes_per_truck']}")

            st.info(f"✅ Payload restriction applied: {apply_payload}")
            total_trucks_needed = -(-box['quantity'] // result['boxes_per_truck'])  # ceil division
            st.success(f"**Total Trucks Needed:** {total_trucks_needed}")

            st.markdown("---")

            # -------------------------------
            # Placement Visualization (Safe Mode)
            # -------------------------------
            col_left, col_right = st.columns([1, 2])

            with col_left:
                st.subheader(f"🚛 Truck Specs")
                st.info(
                    f"**Dimensions:** {truck['dimensions'][0]} × {truck['dimensions'][1]} × {truck['dimensions'][2]} mm  \n"
                    f"**Payload:** {truck['payload']} kg"
                )

                st.subheader("📦 Box Layout")
                fit_len, fit_wid, fit_hei = result["orientation"]
                st.info(
                    f"**Type:** {box['type']}  \n"
                    f"**Dimensions used:** {result['box_dims_used'][0]} × {result['box_dims_used'][1]} × {result['box_dims_used'][2]} mm  \n"
                    f"**Boxes along Length:** {fit_len}  \n"
                    f"**Boxes along Width:** {fit_wid}  \n"
                    f"**Boxes along Height:** {fit_hei}  \n"
                    f"**Boxes by Space:** {result['boxes_by_space']}  \n"
                    f"**Boxes by Payload:** {result['max_boxes_by_weight']}  \n"
                    f"**Boxes Loaded:** {result['boxes_per_truck']}  \n"
                    f"**Utilisation (by volume):** {result['utilisation_percent']} %  \n"
                    f"**Utilisation (by space):** {result['utilisation_by_space']} %"
                )

            with col_right:
                st.subheader("📊 Placement Visualization")

                fit_len, fit_wid, fit_hei = result["orientation"]
                total_boxes = result["boxes_per_truck"]
                max_visual_boxes = 500  # safe limit

                # Special case for tiny boxes (e.g. 100x100x100 mm)
                if (box['dimensions'][0], box['dimensions'][1], box['dimensions'][2]) == (100, 100, 100):
                    st.info(
                        f"📦 Box is too small for drawing.\n\n"
                        f"- Boxes by space: {result['boxes_by_space']}\n"
                        f"- Boxes by payload: {result['max_boxes_by_weight']}\n"
                        f"- Boxes loaded: {total_boxes}\n"
                        f"- Arrangement: {fit_len} × {fit_wid} × {fit_hei}"
                    )

                elif total_boxes <= max_visual_boxes:
                    for layer in range(fit_hei):
                        st.markdown(f"**Layer {layer + 1}**")
                        for row in range(fit_wid):
                            cols = st.columns(fit_len)
                            for col_idx in range(fit_len):
                                with cols[col_idx]:
                                    st.markdown(
                                        "<div style='background:#90EE90; border:1px solid #333; height:30px; "
                                        "display:flex; justify-content:center; align-items:center;'>B</div>",
                                        unsafe_allow_html=True
                                    )
                    st.markdown("---")
                else:
                    preview_len = min(fit_len, 5)
                    preview_wid = min(fit_wid, 5)

                    st.info(f"⚠ Too many boxes ({total_boxes}) to draw. Showing a {preview_len} × {preview_wid} preview instead.")

                    for row in range(preview_wid):
                        cols = st.columns(preview_len)
                        for col_idx in range(preview_len):
                            with cols[col_idx]:
                                st.markdown(
                                    "<div style='background:#90EE90; border:1px solid #333; height:30px; "
                                    "display:flex; justify-content:center; align-items:center;'>B</div>",
                                    unsafe_allow_html=True
                                )

            # ✅ Always show arrangement summary
            st.success(
                f"Arrangement: {fit_len} × {fit_wid} × {fit_hei} = {total_boxes} boxes"
            )

import streamlit as st
import itertools

st.set_page_config(page_title="Truck Optimization & Box Placement", layout="wide")
st.title("📦 Truck Optimization & Box Placement")

# -----------------------------
# Get saved session data
# -----------------------------
box_data = st.session_state.get("box_data", [])
route_info = st.session_state.get("route_info", {})

if not box_data or not route_info:
    st.error("❌ No saved data found. Please go back and enter box & route details first.")
    st.stop()

# First box for optimization
box = box_data[0]

# -----------------------------
# Show box & route info
# -----------------------------
with st.container():
    st.subheader("📦 Selected Box & Route Info")
    st.write(f"*Box Type:* {box['type']}")
    st.write(f"*Quantity:* {box['quantity']}")
    st.write(f"*Dimensions:* {box['dimensions'][0]} × {box['dimensions'][1]} × {box['dimensions'][2]} mm")
    st.write(f"*Payload:* {box['payload']} kg")
    st.markdown("---")
    st.write(f"*Source:* {route_info['Source']}")
    st.write(f"*Destination:* {route_info['Destination']}")
    st.write("🛣 *Route Type Distribution:*")
    for route, pct in route_info["Route Distribution"].items():
        st.write(f"- {route}: {pct}%")

st.divider()

# -----------------------------
# Define trucks
# -----------------------------
trucks = [
    {"name": "32 ft. Single Axle", "dimensions": (9750, 2440, 2440), "payload": 16000},
    {"name": "32 ft. Multi Axle", "dimensions": (9750, 2440, 2440), "payload": 21000},
    {"name": "22 ft. Truck", "dimensions": (7300, 2440, 2440), "payload": 10000},
]

st.subheader("🚛 Available Trucks")
cols = st.columns(len(trucks))
for col, truck in zip(cols, trucks):
    with col:
        st.markdown(f"### {truck['name']}")
        st.write(f"*Dimensions:* {truck['dimensions'][0]} × {truck['dimensions'][1]} × {truck['dimensions'][2]} mm")
        st.write(f"*Payload:* {truck['payload']} kg")

st.divider()

# -----------------------------
# Payload toggle
# -----------------------------
apply_payload = st.checkbox("🚦 Apply Payload Restriction", value=True)


# -----------------------------
# Truck optimisation function
# -----------------------------
def calculate_optimisation(truck, box, apply_payload=True):
    truck_len, truck_wid, truck_hei = truck["dimensions"]
    box_len, box_wid, box_hei = box["dimensions"]

    best_result = None

    # Try all 6 orientations
    for dims in set(itertools.permutations([box_len, box_wid, box_hei], 3)):
        b_len, b_wid, b_hei = dims

        # Fit counts along each axis
        fit_len = int(truck_len // b_len)
        fit_wid = int(truck_wid // b_wid)
        fit_hei = int(truck_hei // b_hei)
        boxes_by_space = fit_len * fit_wid * fit_hei

        if boxes_by_space <= 0:
            continue

        # Payload limit
        max_boxes_by_weight = None
        if box["payload"] > 0:
            max_boxes_by_weight = int(truck["payload"] // float(box["payload"]))
            if apply_payload:
                total_boxes = min(boxes_by_space, max_boxes_by_weight)
            else:
                total_boxes = boxes_by_space
        else:
            continue

        # Volume utilisation
        truck_volume = (truck_len * truck_wid * truck_hei) / 1e9  # m³
        box_volume = (b_len * b_wid * b_hei) / 1e9  # m³
        utilised_volume = total_boxes * box_volume
        utilisation_percent = (utilised_volume / truck_volume) * 100 if truck_volume > 0 else 0

        # Space utilisation (% of boxes that fit by space actually loaded)
        utilisation_by_space = (total_boxes / boxes_by_space) * 100 if boxes_by_space > 0 else 0

        result = {
            "truck_name": truck["name"],
            "truck_volume": round(truck_volume, 2),
            "box_volume": round(box_volume, 3),
            "boxes_by_space": boxes_by_space,
            "max_boxes_by_weight": max_boxes_by_weight,
            "boxes_per_truck": total_boxes,
            "utilisation_percent": round(utilisation_percent, 1),
            "utilisation_by_space": round(utilisation_by_space, 1),
            "orientation": (fit_len, fit_wid, fit_hei),
            "box_dims_used": dims,
        }

        if best_result is None or result["utilisation_percent"] > best_result["utilisation_percent"]:
            best_result = result

    return best_result


# -----------------------------
# Optimisation Button
# -----------------------------
if st.button("🔵 Optimise Truck Loading", type="primary", use_container_width=True):
    st.subheader("📊 Truck Optimisation Results")

    for truck in trucks:
        result = calculate_optimisation(truck, box, apply_payload)

        with st.expander(f"🚛 {result['truck_name']} - {result['utilisation_percent']}% filled"):
            # Summary row
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.markdown(f"**Truck Volume:** {result['truck_volume']} m³")
            col2.markdown(f"**Box Volume:** {result['box_volume']} m³")
            col3.markdown(f"**Boxes (by space):** {result['boxes_by_space']}")
            col4.markdown(f"**Boxes (by payload):** {result['max_boxes_by_weight']}")
            col5.markdown(f"**Boxes Loaded:** {result['boxes_per_truck']}")

            st.info(f"✅ Payload restriction applied: {apply_payload}")
            total_trucks_needed = -(-box['quantity'] // result['boxes_per_truck'])  # ceil division
            st.success(f"**Total Trucks Needed:** {total_trucks_needed}")

            st.markdown("---")

            # -------------------------------
            # Placement Visualization (Safe Mode)
            # -------------------------------
            col_left, col_right = st.columns([1, 2])

            with col_left:
                st.subheader(f"🚛 Truck Specs")
                st.info(
                    f"**Dimensions:** {truck['dimensions'][0]} × {truck['dimensions'][1]} × {truck['dimensions'][2]} mm  \n"
                    f"**Payload:** {truck['payload']} kg"
                )

                st.subheader("📦 Box Layout")
                fit_len, fit_wid, fit_hei = result["orientation"]
                st.info(
                    f"**Type:** {box['type']}  \n"
                    f"**Dimensions used:** {result['box_dims_used'][0]} × {result['box_dims_used'][1]} × {result['box_dims_used'][2]} mm  \n"
                    f"**Boxes along Length:** {fit_len}  \n"
                    f"**Boxes along Width:** {fit_wid}  \n"
                    f"**Boxes along Height:** {fit_hei}  \n"
                    f"**Boxes by Space:** {result['boxes_by_space']}  \n"
                    f"**Boxes by Payload:** {result['max_boxes_by_weight']}  \n"
                    f"**Boxes Loaded:** {result['boxes_per_truck']}  \n"
                    f"**Utilisation (by volume):** {result['utilisation_percent']} %  \n"
                    f"**Utilisation (by space):** {result['utilisation_by_space']} %"
                )

            with col_right:
                st.subheader("📊 Placement Visualization")

                fit_len, fit_wid, fit_hei = result["orientation"]
                total_boxes = result["boxes_per_truck"]
                max_visual_boxes = 500  # safe limit

                # Special case for tiny boxes (e.g. 100x100x100 mm)
                if (box['dimensions'][0], box['dimensions'][1], box['dimensions'][2]) == (100, 100, 100):
                    st.info(
                        f"📦 Box is too small for drawing.\n\n"
                        f"- Boxes by space: {result['boxes_by_space']}\n"
                        f"- Boxes by payload: {result['max_boxes_by_weight']}\n"
                        f"- Boxes loaded: {total_boxes}\n"
                        f"- Arrangement: {fit_len} × {fit_wid} × {fit_hei}"
                    )

                elif total_boxes <= max_visual_boxes:
                    for layer in range(fit_hei):
                        st.markdown(f"**Layer {layer + 1}**")
                        for row in range(fit_wid):
                            cols = st.columns(fit_len)
                            for col_idx in range(fit_len):
                                with cols[col_idx]:
                                    st.markdown(
                                        "<div style='background:#90EE90; border:1px solid #333; height:30px; "
                                        "display:flex; justify-content:center; align-items:center;'>B</div>",
                                        unsafe_allow_html=True
                                    )
                    st.markdown("---")
                else:
                    preview_len = min(fit_len, 5)
                    preview_wid = min(fit_wid, 5)

                    st.info(f"⚠ Too many boxes ({total_boxes}) to draw. Showing a {preview_len} × {preview_wid} preview instead.")

                    for row in range(preview_wid):
                        cols = st.columns(preview_len)
                        for col_idx in range(preview_len):
                            with cols[col_idx]:
                                st.markdown(
                                    "<div style='background:#90EE90; border:1px solid #333; height:30px; "
                                    "display:flex; justify-content:center; align-items:center;'>B</div>",
                                    unsafe_allow_html=True
                                )

            # ✅ Always show arrangement summary
            st.success(
                f"Arrangement: {fit_len} × {fit_wid} × {fit_hei} = {total_boxes} boxes"
            )

