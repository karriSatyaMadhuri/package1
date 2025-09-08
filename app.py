
import streamlit as st

st.set_page_config(page_title="📦 Packaging Asset Recommender", layout="wide")

# --- Title and Subtitle ---
st.markdown(
    """
    <h1 style="text-align:center;">Green Packaging Asset Design</h1>
    <p style="text-align:center; font-size:18px; color:gray;">
    Design returnable packaging assets and optimize truck load to reduce logistics cost, 
    carbon emissions and prevent damage.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Two cards ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="border:1px solid #e0e0e0; border-radius:15px; padding:20px;">
            <h3>📦 Design Packaging Asset</h3>
            <p style="color:gray;">
            Recommendation of Auto-Parts Orientation, Outer Boxes, Inserts and Separators 
            for transporting more parts in lesser logistics cost.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Start now →", key="start", use_container_width=True):
        st.switch_page("pages/Inputs.py")

with col2:
    st.markdown(
        """
        <div style="border:1px solid #e0e0e0; border-radius:15px; padding:20px;">
            <h3>🚚 Optimise Truck Load</h3>
            <p style="color:gray;">
            Recommendation of Trucks and Outer Boxes orientation for maximising space 
            utilisation. Compare across various trucks.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Maximise now →", key="maximise", use_container_width=True):
        st.switch_page("pages/truckload.py")

import streamlit as st

st.set_page_config(page_title="📦 Packaging Asset Recommender", layout="wide")

# --- Title and Subtitle ---
st.markdown(
    """
    <h1 style="text-align:center;">Green Packaging Asset Design</h1>
    <p style="text-align:center; font-size:18px; color:gray;">
    Design returnable packaging assets and optimize truck load to reduce logistics cost, 
    carbon emissions and prevent damage.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Two cards ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="border:1px solid #e0e0e0; border-radius:15px; padding:20px;">
            <h3>📦 Design Packaging Asset</h3>
            <p style="color:gray;">
            Recommendation of Auto-Parts Orientation, Outer Boxes, Inserts and Separators 
            for transporting more parts in lesser logistics cost.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Start now →", key="start", use_container_width=True):
        st.switch_page("pages/Inputs.py")

with col2:
    st.markdown(
        """
        <div style="border:1px solid #e0e0e0; border-radius:15px; padding:20px;">
            <h3>🚚 Optimise Truck Load</h3>
            <p style="color:gray;">
            Recommendation of Trucks and Outer Boxes orientation for maximising space 
            utilisation. Compare across various trucks.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Maximise now →", key="maximise", use_container_width=True):
        st.switch_page("pages/truckload.py")

