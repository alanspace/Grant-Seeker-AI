import streamlit as st
import json
import time
import sys
import os
import asyncio
# Add root directory to path to allow importing backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from backend.adk_agent import GrantSeekerWorkflow
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


# Fit Score Slider
min_fit_score = st.slider(
    "Minimum Fit Score",
    min_value=0,
    max_value=100,
    value=50,
    help="Filter grants by how well they match your description."
)
# Search button and logic
if st.button("Search Grants", type="primary"):
    if not project_text.strip():
        st.warning("Please enter a project description first.")
    else:
        with st.spinner("🔎 AI Agents are scouting for the best matching grants..."):
            try:
                # Initialize workflow
                workflow = GrantSeekerWorkflow()
                
                # Run search (using asyncio.run since we are in a sync context)
                # Note: In a production Streamlit app, we might want to handle the loop differently
                results = asyncio.run(workflow.run(project_text))
                
                st.session_state.grants = results
                
                if not results:
                    st.info("No grants found matching your criteria.")
                    
            except Exception as e:
                st.error(f"An error occurred during search: {e}")

# Display results from session state
if st.session_state.grants:
    st.write("---")
    st.subheader(f"🎯 Found {len(st.session_state.grants)} Matching Grants")
    st.write("")

    # Filter by fit score
    filtered_grants = [g for g in st.session_state.grants if g.get('fit_score', 0) >= min_fit_score]
    
    st.write("---")
    st.subheader(f"🎯 Found {len(filtered_grants)} Grants (Minimum Fit Score: {min_fit_score}%)")
    st.write("")

    for g in filtered_grants:
        # grant_card now returns True if clicked
        if grant_card(g):
            st.session_state.selected_grant = g
            st.switch_page("pages/2_📄_Grant_Details.py")
        st.write("")
elif project_text and not st.session_state.grants:
     # Only show this if a search was attempted but no results found (and it wasn't just empty state)
     # However, since we only populate on button click, we can leave this simple for now.
     pass

