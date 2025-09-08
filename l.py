import os
import re
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part

load_dotenv()


def _extract_json(text: str) -> str:
    """Cleans LLM output and extracts JSON only."""
    # Remove code fences like ```json ... ```
    cleaned = re.sub(r"^```[a-zA-Z]*|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return cleaned


class LLMRecommender:
    def __init__(self):
        self.project = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-pro")

        if not self.project or not self.credentials_path:
            raise ValueError("❌ GCP_PROJECT_ID or GOOGLE_APPLICATION_CREDENTIALS not set")

        self.credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        vertexai.init(project=self.project, location=self.location, credentials=self.credentials)
        self.model = GenerativeModel(self.model_name)

    # ----------------------------------------------------
    # 1️⃣ Outer Box Recommendation
    # ----------------------------------------------------
    def recommend(
        self,
        length,
        width,
        height,
        weight="",
        fragile="low",
        forklift=False,
        forklift_capacity=0,
        stacking=False,
        quantity=1,
        orientation=None,
        source="N/A",
        destination="N/A"
    ):
        prompt = f"""
        You are a packaging design expert. 
        Recommend the best *outer box type* for the given auto part.

        📦 Part Details:
        - Dimensions: {length} × {width} × {height} mm
        - Weight: {weight} kg
        - Fragility: {fragile}
        - Stacking allowed: {stacking}
        - Orientation restrictions: {orientation}
        - Quantity per year: {quantity}

        🚚 Logistics:
        - Source: {source}
        - Destination: {destination}
        - Forklift available: {forklift}, capacity: {forklift_capacity} kg

        ✅ Return JSON with this structure (do not include extra text, only JSON):
        {{
            "box": {{
                "type": "string",
                "internal": "string",
                "external": "string",
                "material": "string",
                "capacity": number
            }},
            "reason": "Explain in 2–3 sentences WHY this box type, dimensions, and material were selected."
        }}
        """
        try:
            response = self.model.generate_content([Part.from_text(prompt)])
            text = response.candidates[0].content.parts[0].text.strip()
            text = _extract_json(text)
            data = json.loads(text)

            # ✅ Validate
            if not data or "box" not in data or "type" not in data["box"]:
                raise ValueError("Invalid LLM JSON structure")

            return data

        except Exception as e:
            print("LLM recommend error:", e)
            return {
                "box": {
                    "type": "Fallback Box",
                    "internal": f"{length}x{width}x{height} mm",
                    "external": f"{length+40}x{width+40}x{height+15} mm",
                    "material": "Corrugated",
                    "capacity": 10
                },
                "reason": "Fallback: default box selected due to LLM failure."
            }

    # ----------------------------------------------------
    # 2️⃣ Orientation Analysis
    # ----------------------------------------------------
    def analyze_orientations(self, length, width, height, weight):
        prompt = f"""
        You are analyzing possible orientations for inserting an auto part.

        📦 Part:
        - Dimensions: {length} × {width} × {height} mm
        - Weight: {weight} kg

        ✅ Return JSON in this structure:
        {{
            "orientations": {{
                "length-standing": "✅ or ❌",
                "width-standing": "✅ or ❌",
                "height-standing": "✅ or ❌",
                "mix-combinations": "✅ or ❌"
            }},
            "explanation": "Brief reasoning why these orientations are feasible or not"
        }}
        """
        try:
            response = self.model.generate_content([Part.from_text(prompt)])
            text = response.candidates[0].content.parts[0].text.strip()
            text = _extract_json(text)
            data = json.loads(text)

            if not data or "orientations" not in data:
                raise ValueError("Invalid orientation structure")

            return data

        except Exception as e:
            print("LLM orientation error:", e)
            return {
                "orientations": {
                    "length-standing": "✅",
                    "width-standing": "✅",
                    "height-standing": "✅",
                    "mix-combinations": "⏳"
                },
                "explanation": "Fallback: assuming all orientations possible."
            }

    # ----------------------------------------------------
    # 3️⃣ Insert + Matrix Recommendation
    # ----------------------------------------------------
    def recommend_insert_matrix(
        self,
        part_length,
        part_width,
        part_height,
        weight,
        orientation="length-standing",
        outer_box_length=1100,
        outer_box_width=900,
        outer_box_height=460,
        clearance=5,
        wall_thickness=15
    ):
        prompt = f"""
        You are a packaging insert designer. Recommend a partition grid layout for storing auto parts.

        📦 Auto Part:
        - Dimensions: {part_length} × {part_width} × {part_height} mm
        - Weight: {weight} kg
        - Orientation: {orientation}

        📐 Outer Box:
        - Internal Dimensions: {outer_box_length} × {outer_box_width} × {outer_box_height} mm
        - Clearance: {clearance} mm between cells
        - Wall Thickness: {wall_thickness} mm on all sides

        ✅ Return JSON in this structure:
        {{
            "insert": {{
                "type": "PP Partition Grid",
                "orientation": "{orientation}",
                "matrix": "rows × columns",
                "insert_dimensions": {{
                    "length": number,
                    "width": number,
                    "height": number
                }},
                "cell_dimensions": {{
                    "length": number,
                    "width": number,
                    "height": number
                }},
                "units_per_insert": number
            }},
            "visualization": {{
                "matrix_pattern": [
                    ["cell_1", "cell_2", "cell_3"],
                    ["cell_4", "cell_5", "cell_6"]
                ]
            }},
            "reason": "Explain why this orientation and matrix were selected. Mention clearance, fit, and efficiency."
        }}
        """
        try:
            response = self.model.generate_content([Part.from_text(prompt)])
            text = response.candidates[0].content.parts[0].text.strip()
            text = _extract_json(text)
            data = json.loads(text)

            if not data or "insert" not in data:
                raise ValueError("Invalid insert structure")

            return data

        except Exception as e:
            print("LLM matrix recommendation error:", e)
            return {
                "insert": {
                    "type": "PP Partition Grid",
                    "orientation": orientation,
                    "matrix": "2 × 3",
                    "insert_dimensions": {
                        "length": outer_box_length,
                        "width": outer_box_width,
                        "height": outer_box_height
                    },
                    "cell_dimensions": {
                        "length": part_length,
                        "width": part_width,
                        "height": part_height
                    },
                    "units_per_insert": 6
                },
                "visualization": {
                    "matrix_pattern": [
                        ["cell_1", "cell_2", "cell_3"],
                        ["cell_4", "cell_5", "cell_6"]
                    ]
                },
                "reason": "Fallback: default 2×3 layout applied. Dimensions padded for clearance."
            }
########################__________########visual


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
    st.warning("⚠️ Please complete Step 1 first.")
    st.stop()

product = st.session_state["product"]

# ✅ Normalize outer box keys
outer_box_raw = st.session_state.get("outer_box", {
    "length": 1100,
    "width": 900,
    "height": 580
})

# 🔍 Debug print
st.write("📦 Outer Box Contents:", outer_box_raw)

# ✅ Extract dimensions safely
outer_box_length = outer_box_raw.get("L") or outer_box_raw.get("length")
outer_box_width = outer_box_raw.get("W") or outer_box_raw.get("width")
outer_box_height = outer_box_raw.get("H") or outer_box_raw.get("height")

# ✅ Validate product keys
required_keys = ["L", "W", "H", "weight"]
if not all(k in product for k in required_keys):
    st.error("🚫 Missing product dimensions. Please complete Step 1.")
    st.stop()

# ✅ Call LLM for insert matrix recommendation
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

# -------------------------------
# Layout: Left = Specs, Right = Grid
# -------------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("🧩 Design of Inserts (PP material)")
    insert = insert_data["insert"]
    st.markdown(f"**Type:** {insert['type']}")
    st.markdown(f"**Orientation:** {insert['orientation']}")
    st.markdown(f"**Matrix Pattern:** {insert['matrix']}")
    st.markdown(f"**Outer Dimensions:** {insert['insert_dimensions']['length']} × {insert['insert_dimensions']['width']} × {insert['insert_dimensions']['height']} mm")
    st.markdown(f"**Weight:** {product['weight']} kg")

    st.markdown("**Cell Details**")
    st.markdown(f"Inner Cell Dimensions: {insert['cell_dimensions']['length']} × {insert['cell_dimensions']['width']} × {insert['cell_dimensions']['height']} mm")
    st.markdown(f"Auto-parts per layer: {insert['units_per_insert']}")

    st.info("💡 Why this layout:")
    st.write(insert_data["reason"])

with right:
    st.subheader("🧮 Matrix Pattern Visualization")
    matrix = insert_data["visualization"]["matrix_pattern"]
    for row in matrix:
        cols = st.columns(len(row))
        for i, cell in enumerate(row):
            with cols[i]:
                st.markdown(f"🟦 {cell}")

# ✅ Navigation
st.markdown("---")
if st.button("➡️ Finalize Packaging"):
    st.switch_page("pages/Finalize.py")
    ###################333##############