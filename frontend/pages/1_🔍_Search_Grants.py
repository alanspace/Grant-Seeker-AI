import streamlit as st
import json
import time
from utils.ui_components import grant_card

st.title("🔍 Search Grants")
st.markdown("### Describe your project idea and we'll find relevant grants for you.")

# Initialize session state for grants if not present
if 'grants' not in st.session_state:
    st.session_state.grants = []

# Input area with better styling
project_text = st.text_area(
    "Project Description",
    placeholder="e.g., We are a non-profit organization looking to build a community garden to promote sustainable living...",
    height=150,
    help="Provide as much detail as possible to get the best matches."
)

# Search button and logic
if st.button("Search Grants", type="primary"):
    if not project_text.strip():
        st.warning("Please enter a project description first.")
    else:
        with st.spinner("🔎 AI Agents are scouting for the best matching grants..."):
            # Simulate network delay
            time.sleep(1.5)
            
            # Load sample data
            try:
                with open("sample_data/grants.json", "r", encoding="utf-8") as f:
                    st.session_state.grants = json.load(f)
            except FileNotFoundError:
                st.error("Sample data not found. Please ensure '/sample_data/grants.json' exists.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display results from session state
if st.session_state.grants:
    st.write("---")
    st.subheader(f"🎯 Found {len(st.session_state.grants)} Matching Grants")
    st.write("")

    for g in st.session_state.grants:
        # grant_card now returns True if clicked
        if grant_card(g):
            st.session_state.selected_grant = g
            st.switch_page("pages/2_📄_Grant_Details.py")
        st.write("")
elif project_text and not st.session_state.grants:
     # Only show this if a search was attempted but no results found (and it wasn't just empty state)
     # However, since we only populate on button click, we can leave this simple for now.
     pass

