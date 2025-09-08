<<<<<<< HEAD
# llm_recommender.py

import os
import re
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import math

load_dotenv()

def _extract_json(text: str) -> str:
    """Cleans LLM output and extracts JSON only."""
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
    def recommend(self, length, width, height, weight="", fragile="low",
                  forklift=False, forklift_capacity=0, stacking=False,
                  quantity=1, orientation=None, source="N/A", destination="N/A"):
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

            if not data or "box" not in data or "type" not in data["box"]:
                raise ValueError("Invalid LLM JSON structure")

            return data

        except Exception as e:
            print("LLM recommend error:", e)
            return {
                "box": {
                    "type": "Fallback Box",
                    "internal": f"{length}×{width}×{height} mm",
                    "external": f"{length+40}×{width+40}×{height+15} mm",
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
    def recommend_insert_matrix(self, part_length, part_width, part_height,
                                weight, orientation, outer_box_length,
                                outer_box_width, outer_box_height):
        if not all([part_length, part_width, part_height,
                outer_box_length, outer_box_width, outer_box_height]):
            raise ValueError(f"❌ Missing dimensions: part=({part_length},{part_width},{part_height}), "
                         f"box=({outer_box_length},{outer_box_width},{outer_box_height})")

        if orientation == "width-standing":
            part_length, part_width = part_width, part_length
        elif orientation == "height-standing":
            part_length, part_height = part_height, part_length

        cols = max(1, outer_box_length // part_length)
        rows = max(1, outer_box_width // part_width)
        layers = max(1, outer_box_height // part_height)

        units_per_layer = int(rows * cols)
        total_units = int(units_per_layer * layers)

        matrix_pattern = []
        count = 1
        for r in range(int(rows)):
            row_cells = []
            for c in range(int(cols)):
                row_cells.append(f"cell_{count}")
                count += 1
            matrix_pattern.append(row_cells)

        insert_data = {
            "insert": {
                "type": "PP Insert",
                "orientation": orientation,
                "matrix": f"{rows} × {cols}",
                "insert_dimensions": {
                    "length": outer_box_length,
                    "width": outer_box_width,
                    "height": part_height
                },
                "cell_dimensions": {
                    "length": part_length,
                    "width": part_width,
                    "height": part_height
                },
                "units_per_insert": units_per_layer
            },
            "visualization": {
                "matrix_pattern": matrix_pattern
            },
            "reason": (
                f"{rows}×{cols} layout fits inside {outer_box_length}×{outer_box_width} mm. "
                f"Total {units_per_layer} parts per layer."
            )
        }

        return insert_data

    # ----------------------------------------------------
    # 4️⃣ Helpers for cleaning dimensions
    # ----------------------------------------------------
    def _clean_dimension(self, dim: str) -> int:
        return int(re.sub(r"[^0-9]", "", dim.strip()))

    def _clean_dimensions_tuple(self, dims: str):
        parts = re.split(r"[×x]", dims)
        return tuple(self._clean_dimension(p) for p in parts if p.strip())
=======
# llm_recommender.py

import os
import re
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import math

load_dotenv()

def _extract_json(text: str) -> str:
    """Cleans LLM output and extracts JSON only."""
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
    def recommend(self, length, width, height, weight="", fragile="low",
                  forklift=False, forklift_capacity=0, stacking=False,
                  quantity=1, orientation=None, source="N/A", destination="N/A"):
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

            if not data or "box" not in data or "type" not in data["box"]:
                raise ValueError("Invalid LLM JSON structure")

            return data

        except Exception as e:
            print("LLM recommend error:", e)
            return {
                "box": {
                    "type": "Fallback Box",
                    "internal": f"{length}×{width}×{height} mm",
                    "external": f"{length+40}×{width+40}×{height+15} mm",
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
    def recommend_insert_matrix(self, part_length, part_width, part_height,
                                weight, orientation, outer_box_length,
                                outer_box_width, outer_box_height):
        if not all([part_length, part_width, part_height,
                outer_box_length, outer_box_width, outer_box_height]):
            raise ValueError(f"❌ Missing dimensions: part=({part_length},{part_width},{part_height}), "
                         f"box=({outer_box_length},{outer_box_width},{outer_box_height})")

        if orientation == "width-standing":
            part_length, part_width = part_width, part_length
        elif orientation == "height-standing":
            part_length, part_height = part_height, part_length

        cols = max(1, outer_box_length // part_length)
        rows = max(1, outer_box_width // part_width)
        layers = max(1, outer_box_height // part_height)

        units_per_layer = int(rows * cols)
        total_units = int(units_per_layer * layers)

        matrix_pattern = []
        count = 1
        for r in range(int(rows)):
            row_cells = []
            for c in range(int(cols)):
                row_cells.append(f"cell_{count}")
                count += 1
            matrix_pattern.append(row_cells)

        insert_data = {
            "insert": {
                "type": "PP Insert",
                "orientation": orientation,
                "matrix": f"{rows} × {cols}",
                "insert_dimensions": {
                    "length": outer_box_length,
                    "width": outer_box_width,
                    "height": part_height
                },
                "cell_dimensions": {
                    "length": part_length,
                    "width": part_width,
                    "height": part_height
                },
                "units_per_insert": units_per_layer
            },
            "visualization": {
                "matrix_pattern": matrix_pattern
            },
            "reason": (
                f"{rows}×{cols} layout fits inside {outer_box_length}×{outer_box_width} mm. "
                f"Total {units_per_layer} parts per layer."
            )
        }

        return insert_data

    # ----------------------------------------------------
    # 4️⃣ Helpers for cleaning dimensions
    # ----------------------------------------------------
    def _clean_dimension(self, dim: str) -> int:
        return int(re.sub(r"[^0-9]", "", dim.strip()))

    def _clean_dimensions_tuple(self, dims: str):
        parts = re.split(r"[×x]", dims)
        return tuple(self._clean_dimension(p) for p in parts if p.strip())
>>>>>>> 3a3863a0610f90db8b3fb50756d9c2afa1d1fc53
